import os
import uuid
import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from services.document_processor import process_document
from services.vector_store import VectorStoreService
from services.retrieval_service import RetrievalService
from services.rag_service import RAGService, LLMNotConfiguredError, LLMGenerationError
from services.bis_search_service import BISSearchService, bis_search_service, BIS_SERVICES_CATEGORIES
from services.language_service import language_service
from services.rate_limiter import rate_limiter
from services.security_utils import (
    sanitize_error_detail,
    validate_and_sanitize_filename,
    assert_within_directory,
    MAX_QUESTION_LENGTH,
    MAX_QUERY_LENGTH,
    MAX_FILENAME_LENGTH
)

# Initialize FastAPI application
app = FastAPI(
    title="BIS AI Assistant Backend API",
    description="Backend API for AI-powered Intelligent Assistant for Indian Standards and BIS Services",
    version="1.0.0"
)

# Convert validation errors to 400 Bad Request cleanly
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": sanitize_error_detail(str(exc))}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": sanitize_error_detail(str(exc))}
    )

# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if request.url.path.startswith(("/ask", "/retrieve", "/bis", "/documents")):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

# Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    expensive_paths = ("/ask", "/retrieve", "/bis/search", "/documents/upload")
    if request.method == "POST" and any(request.url.path == p or request.url.path.startswith(p + "/") for p in expensive_paths):
        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = rate_limiter.check(client_ip, endpoint=request.url.path)
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please wait before retrying."},
                headers={"Retry-After": str(retry_after)}
            )
    return await call_next(request)

# Configure CORS Middleware
raw_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "").strip()
if raw_origins:
    cors_origins = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]
else:
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8009",
        "http://127.0.0.1:8009",
    ]

is_production = os.environ.get("ENVIRONMENT", "").lower() == "production" or os.environ.get("APP_ENV", "").lower() == "production"
if is_production and "*" in cors_origins:
    cors_origins = [o for o in cors_origins if o != "*"]
    if not cors_origins:
        cors_origins = ["http://127.0.0.1:8000"]

allow_credentials = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Upload directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(BASE_DIR, "documents", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configuration constraints
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

# In-memory metadata storage
documents_db: Dict[str, Dict[str, Any]] = {}


# Pydantic Schemas
class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        description="The query question string sent by the user.",
        example="What is BIS certification?"
    )
    language: Optional[str] = Field(
        None,
        description="Optional target language code ('en', 'hi', 'mr'). If omitted, language is detected automatically.",
        example="hi"
    )

    @field_validator("question")
    @classmethod
    def validate_question_non_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or contain only whitespace.")
        if len(trimmed) > MAX_QUESTION_LENGTH:
            raise ValueError(f"Question exceeds maximum allowed length of {MAX_QUESTION_LENGTH} characters.")
        return trimmed

    @field_validator("language")
    @classmethod
    def validate_language_code(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return language_service.validate_language(value)


class SourceItem(BaseModel):
    document_id: str = Field(..., description="Unique ID of the document.")
    filename: str = Field(..., description="User-facing filename of the reference document.")
    file_type: Optional[str] = Field("txt", description="File type extension (pdf, docx, txt).")
    chunk_id: str = Field(..., description="Unique chunk ID.")
    chunk_index: int = Field(..., description="Zero-indexed chunk position within the document.")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0).")
    pages: Optional[List[int]] = Field(None, description="Page numbers where chunk appears (for PDF).")
    snippet: Optional[str] = Field(None, description="Short relevant text excerpt from the chunk.")


class QuestionResponse(BaseModel):
    question: str = Field(..., description="The original query question.")
    answer: str = Field(..., description="The generated response answer.")
    language: str = Field("en", description="Resolved response language code ('en', 'hi', 'mr').")
    sources: List[SourceItem] = Field(default_factory=list, description="List of structured source references.")


class BISServiceCategory(BaseModel):
    id: str = Field(..., description="Unique category identifier.")
    name: str = Field(..., description="Display name of service category.")
    description: str = Field(..., description="Description of the service category.")


class BISSearchRequest(BaseModel):
    query: str = Field(..., description="Search query string.", example="How do I get BIS certification?")
    service: Optional[str] = Field(None, description="Optional service category filter ID.", example="product_certification")
    top_k: Optional[int] = Field(5, description="Number of top relevant chunks to retrieve (1 to 20).")
    language: Optional[str] = Field(
        None,
        description="Optional target language code ('en', 'hi', 'mr'). If omitted, language is detected automatically.",
        example="hi"
    )

    @field_validator("query")
    @classmethod
    def validate_query_non_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Query string cannot be empty or contain only whitespace.")
        if len(trimmed) > MAX_QUERY_LENGTH:
            raise ValueError(f"Query string exceeds maximum allowed length of {MAX_QUERY_LENGTH} characters.")
        return trimmed

    @field_validator("service")
    @classmethod
    def validate_service_filter(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        valid_ids = {cat["id"] for cat in BIS_SERVICES_CATEGORIES}
        if trimmed.lower() not in valid_ids:
            raise ValueError(f"Invalid service category filter '{trimmed}'. Valid options are: {', '.join(sorted(valid_ids))}")
        return trimmed.lower()

    @field_validator("top_k")
    @classmethod
    def validate_top_k_range(cls, value: Optional[int]) -> int:
        if value is None:
            return 5
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError("top_k must be a positive integer >= 1.")
        if value > 20:
            raise ValueError("top_k cannot exceed maximum limit of 20.")
        return value

    @field_validator("language")
    @classmethod
    def validate_language_code(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return language_service.validate_language(value)


class BISSearchResponse(BaseModel):
    query: str = Field(..., description="Original search query.")
    intent: str = Field(..., description="Detected search intent category.")
    detected_standard: Optional[str] = Field(None, description="Detected Indian Standard identifier (e.g. IS 10500).")
    service_filter: Optional[str] = Field(None, description="Applied service category filter.")
    language: str = Field("en", description="Resolved response language code ('en', 'hi', 'mr').")
    results: List[SourceItem] = Field(default_factory=list, description="Ranked retrieved search chunk items.")
    answer: str = Field(..., description="Grounded RAG answer.")
    sources: List[SourceItem] = Field(default_factory=list, description="Context-selected source citations.")


class DocumentUploadResponse(BaseModel):
    filename: str
    document_id: str
    file_type: str
    file_size: int
    text_length: int
    cleaned_text_length: int
    chunk_count: int
    embedding_model: str
    embedding_dimension: int
    vector_store_status: str
    pages: Optional[Any] = None
    message: str


class DocumentListItem(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    text_length: int
    cleaned_text_length: int
    chunk_count: int
    embedding_model: str
    embedding_dimension: int
    vector_store_status: str
    pages: Optional[Any] = None
    uploaded_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentListItem]


class ChunkItem(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    chunk_text: str
    character_count: int
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = None
    vector_store_status: Optional[str] = "indexed"
    file_type: Optional[str] = None
    pages: Optional[Any] = None


class DocumentChunksResponse(BaseModel):
    document_id: str
    chunk_count: int
    chunks: List[ChunkItem]


class VectorStoreHealthResponse(BaseModel):
    status: str
    collection_name: str
    count: int
    persisted: Optional[bool] = True


class RetrievalRequest(BaseModel):
    question: str = Field(..., description="The query question string sent by the user.", example="What is BIS certification?")
    top_k: Optional[int] = Field(5, description="Number of top relevant chunks to retrieve (1 to 20).")

    @field_validator("question")
    @classmethod
    def validate_question_non_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or contain only whitespace.")
        if len(trimmed) > MAX_QUESTION_LENGTH:
            raise ValueError(f"Question exceeds maximum allowed length of {MAX_QUESTION_LENGTH} characters.")
        return trimmed

    @field_validator("top_k")
    @classmethod
    def validate_top_k_range(cls, value: Optional[int]) -> int:
        if value is None:
            return 5
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError("top_k must be a positive integer >= 1.")
        if value > 20:
            raise ValueError("top_k cannot exceed maximum limit of 20.")
        return value


class RetrievedChunkItem(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    file_type: Optional[str] = None
    chunk_index: int
    chunk_text: str
    character_count: int
    embedding_model: str
    embedding_dimension: int
    pages: Optional[Any] = None
    distance: float
    similarity_score: float


class RetrievalResponse(BaseModel):
    question: str
    results: List[RetrievedChunkItem]
    total_results: int


# Routes
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    """Health check endpoint to verify backend service status."""
    return {
        "status": "healthy",
        "message": "BIS AI Assistant Backend API is running"
    }


@app.post("/ask", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
def ask_question(payload: QuestionRequest):
    """
    RAG Question-Answering endpoint.
    Retrieves relevant document chunks, constructs grounded context, and generates an AI answer in requested or detected language.
    """
    try:
        rag_inst = RAGService.get_instance()
        rag_res = rag_inst.answer_question(payload.question, language=payload.language)
        return QuestionResponse(
            question=rag_res["question"],
            answer=rag_res["answer"],
            language=rag_res.get("language", "en"),
            sources=rag_res.get("sources", [])
        )
    except LLMNotConfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=sanitize_error_detail(str(e))
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=sanitize_error_detail(str(ve))
        )
    except Exception as e:
        safe_detail = sanitize_error_detail(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG answer generation failed: {safe_detail}"
        )


@app.post("/documents/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload, extract, clean, chunk, embed, and persist vectors in local ChromaDB.
    Validates file format, size, sanitizes filename, stores file locally, processes & indexes text vectors.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided in request."
        )

    # Sanitize filename and prevent path traversal
    try:
        safe_filename = validate_and_sanitize_filename(file.filename)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=sanitize_error_detail(str(ve))
        )

    # Extract extension
    _, ext = os.path.splitext(safe_filename)
    ext_lower = ext.lower()

    if ext_lower not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext_lower}'. Allowed formats are PDF, DOCX, and TXT."
        )

    # Read content to validate size and empty check
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    # Unique identifier and stored filename to prevent overwriting
    doc_id = str(uuid.uuid4())
    stored_filename = f"{doc_id}_{safe_filename}"
    stored_filepath = os.path.join(UPLOAD_DIR, stored_filename)

    # Validate containment within UPLOAD_DIR
    if not assert_within_directory(stored_filepath, UPLOAD_DIR):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File path is outside the allowed directory."
        )

    # Save file to disk
    try:
        with open(stored_filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document to server storage: {sanitize_error_detail(str(e))}"
        )

    # Extract, clean, chunk, embed, and store vectors using document processor service
    try:
        extraction_result = process_document(
            file_path=stored_filepath,
            file_type=ext_lower,
            document_id=doc_id,
            filename=safe_filename
        )
    except Exception as e:
        if os.path.exists(stored_filepath):
            try:
                os.remove(stored_filepath)
            except OSError:
                pass
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process document text: {sanitize_error_detail(str(e))}"
        )

    if not extraction_result.success:
        if os.path.exists(stored_filepath):
            try:
                os.remove(stored_filepath)
            except OSError:
                pass
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=sanitize_error_detail(extraction_result.error or "Failed to process document text.")
        )

    # Save metadata in memory (store chunks & embeddings internally for downstream vector indexing)
    uploaded_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_metadata = {
        "document_id": doc_id,
        "filename": safe_filename,
        "stored_filename": stored_filename,
        "file_type": ext_lower.lstrip("."),
        "file_size": file_size,
        "text_length": extraction_result.text_length,
        "cleaned_text_length": extraction_result.cleaned_text_length,
        "chunk_count": extraction_result.chunk_count,
        "embedding_model": extraction_result.embedding_model,
        "embedding_dimension": extraction_result.embedding_dimension,
        "vector_store_status": extraction_result.vector_store_status,
        "pages": extraction_result.pages,
        "uploaded_at": uploaded_at,
        "_chunks": [c.to_dict() for c in extraction_result.chunks],
        "_cleaned_text": extraction_result.cleaned_text
    }
    documents_db[doc_id] = doc_metadata

    return DocumentUploadResponse(
        filename=safe_filename,
        document_id=doc_id,
        file_type=ext_lower.lstrip("."),
        file_size=file_size,
        text_length=extraction_result.text_length,
        cleaned_text_length=extraction_result.cleaned_text_length,
        chunk_count=extraction_result.chunk_count,
        embedding_model=extraction_result.embedding_model,
        embedding_dimension=extraction_result.embedding_dimension,
        vector_store_status=extraction_result.vector_store_status,
        pages=extraction_result.pages,
        message="Document uploaded, text extracted, cleaned, chunked, embedded, and persisted in ChromaDB successfully."
    )


@app.get("/documents", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
def list_documents():
    """
    Returns list of metadata for all uploaded documents.
    Does not expose internal file paths or raw/cleaned/chunk/vector contents.
    """
    items = []
    for doc in documents_db.values():
        items.append(
            DocumentListItem(
                document_id=doc["document_id"],
                filename=doc["filename"],
                file_type=doc.get("file_type", "txt"),
                file_size=doc.get("file_size", 0),
                text_length=doc.get("text_length", 0),
                cleaned_text_length=doc.get("cleaned_text_length", 0),
                chunk_count=doc.get("chunk_count", 0),
                embedding_model=doc.get("embedding_model", ""),
                embedding_dimension=doc.get("embedding_dimension", 384),
                vector_store_status=doc.get("vector_store_status", "indexed"),
                pages=doc.get("pages"),
                uploaded_at=doc.get("uploaded_at") or doc.get("upload_timestamp") or ""
            )
        )
    return DocumentListResponse(documents=items)


@app.get("/documents/{document_id}/chunks", response_model=DocumentChunksResponse, status_code=status.HTTP_200_OK)
def get_document_chunks(document_id: str):
    """
    Development endpoint to retrieve structured chunk metadata for a specific document.
    Does not expose internal filesystem paths or raw vector float arrays in list response.
    """
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found."
        )

    doc_data = documents_db[document_id]
    chunks_raw = doc_data.get("_chunks", [])
    chunk_items = [ChunkItem(**c) for c in chunks_raw]

    return DocumentChunksResponse(
        document_id=document_id,
        chunk_count=len(chunk_items),
        chunks=chunk_items
    )


@app.get("/vector-store/health", response_model=VectorStoreHealthResponse, status_code=status.HTTP_200_OK)
def get_vector_store_health():
    """
    Health check endpoint for ChromaDB persistent vector database.
    """
    vector_store = VectorStoreService.get_instance()
    health_data = vector_store.get_health()
    return VectorStoreHealthResponse(
        status=health_data["status"],
        collection_name=health_data.get("collection_name", "bis_documents"),
        count=health_data["count"],
        persisted=health_data.get("persisted", True)
    )


@app.post("/retrieve", response_model=RetrievalResponse, status_code=status.HTTP_200_OK)
def retrieve_chunks(payload: RetrievalRequest):
    """
    Development endpoint to perform semantic similarity search on persistent ChromaDB collection.
    Converts query text to normalized vector and retrieves top-k relevant document chunks.
    """
    try:
        retriever = RetrievalService.get_instance()
        res = retriever.retrieve(
            question=payload.question,
            top_k=payload.top_k or 5
        )
        return RetrievalResponse(**res)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=sanitize_error_detail(str(ve))
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform semantic retrieval: {sanitize_error_detail(str(e))}"
        )


@app.get("/bis/services", response_model=List[BISServiceCategory], status_code=status.HTTP_200_OK)
def get_bis_services():
    """
    Returns list of structured, authoritative BIS service categories.
    """
    search_svc = BISSearchService.get_instance()
    return search_svc.get_service_categories()


@app.post("/bis/search", response_model=BISSearchResponse, status_code=status.HTTP_200_OK)
def search_bis_services(payload: BISSearchRequest):
    """
    Dedicated BIS Search endpoint.
    Detects user intent and standard identifiers, performs hybrid retrieval, and returns grounded RAG answer + sources.
    """
    try:
        search_svc = BISSearchService.get_instance()
        search_res = search_svc.search_bis(
            query=payload.query,
            service_filter=payload.service,
            top_k=payload.top_k or 5,
            language=payload.language
        )
        return BISSearchResponse(**search_res)
    except LLMNotConfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=sanitize_error_detail(str(e))
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=sanitize_error_detail(str(ve))
        )
    except Exception as e:
        safe_detail = sanitize_error_detail(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BIS search failed: {safe_detail}"
        )


class ReindexResponse(BaseModel):
    message: str
    documents_reindexed: int
    active_embedding_model: str
    active_collection: str
    documents: List[str]


@app.post("/documents/reindex", response_model=ReindexResponse, status_code=status.HTTP_200_OK)
def reindex_documents():
    """
    Reindexes all uploaded documents using the active multilingual embedding model
    into the active ChromaDB collection without deleting source files.
    """
    from services.embedding_service import EmbeddingService
    from services.vector_store import VectorStoreService

    embedder = EmbeddingService.get_instance()
    vs = VectorStoreService.get_instance()

    reindexed_ids = []
    # If documents_db is empty, discover uploaded files present on disk
    if not documents_db and os.path.isdir(UPLOAD_DIR):
        for fname in os.listdir(UPLOAD_DIR):
            fpath = os.path.join(UPLOAD_DIR, fname)
            if os.path.isfile(fpath):
                ext = os.path.splitext(fname)[1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    parts = fname.split("_", 1)
                    doc_id = parts[0] if len(parts) > 1 and len(parts[0]) == 36 else str(uuid.uuid4())
                    orig_name = parts[1] if len(parts) > 1 and len(parts[0]) == 36 else fname
                    documents_db[doc_id] = {
                        "document_id": doc_id,
                        "filename": orig_name,
                        "stored_filename": fname,
                        "file_type": ext.lstrip("."),
                        "file_size": os.path.getsize(fpath),
                        "upload_timestamp": datetime.datetime.utcnow().isoformat() + "Z"
                    }

    for doc_id, doc in list(documents_db.items()):
        stored_filename = doc.get("stored_filename")
        if not stored_filename:
            continue
        stored_filepath = os.path.join(UPLOAD_DIR, stored_filename)
        if not os.path.isfile(stored_filepath):
            continue

        ext_lower = f".{doc.get('file_type', 'txt')}"
        safe_filename = doc.get("filename", stored_filename)

        res = process_document(
            file_path=stored_filepath,
            file_type=ext_lower,
            document_id=doc_id,
            filename=safe_filename
        )
        if res.success:
            doc["text_length"] = res.text_length
            doc["cleaned_text_length"] = res.cleaned_text_length
            doc["chunk_count"] = res.chunk_count
            doc["embedding_model"] = res.embedding_model
            doc["embedding_dimension"] = res.embedding_dimension
            doc["vector_store_status"] = res.vector_store_status
            doc["pages"] = res.pages
            doc["uploaded_at"] = doc.get("uploaded_at") or doc.get("upload_timestamp") or datetime.datetime.now(datetime.timezone.utc).isoformat()
            doc["_chunks"] = [c.to_dict() for c in res.chunks]
            doc["_cleaned_text"] = res.cleaned_text
            reindexed_ids.append(doc_id)

    return ReindexResponse(
        message="All uploaded documents reindexed successfully into active collection.",
        documents_reindexed=len(reindexed_ids),
        active_embedding_model=embedder.model_name,
        active_collection=vs.collection_name,
        documents=reindexed_ids
    )


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)



