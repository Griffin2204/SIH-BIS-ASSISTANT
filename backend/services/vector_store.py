import os
from typing import List, Dict, Any, Optional
from services.chunker import DocumentChunk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_STORE_DIR = os.environ.get("CHROMA_PERSIST_DIRECTORY", os.path.join(BASE_DIR, "vector_store"))

DEFAULT_COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION_NAME", "bis_documents_multilingual")


def get_default_collection_name() -> str:
    """
    Returns the appropriate isolated ChromaDB collection name based on the active embedding provider.
    SentenceTransformer and Gemini embeddings reside in incompatible vector spaces and MUST NOT be mixed.
    """
    env_name = os.environ.get("CHROMA_COLLECTION_NAME")
    if env_name:
        return env_name
    try:
        from services.embedding_service import embedding_service
        if embedding_service._should_use_gemini():
            return "bis_documents_gemini_multilingual"
    except Exception:
        pass
    return "bis_documents_multilingual"


class VectorStoreService:
    _instance: Optional['VectorStoreService'] = None

    def __init__(self, persist_directory: str = VECTOR_STORE_DIR, collection_name: Optional[str] = None):
        self.persist_directory = persist_directory
        self.collection_name = collection_name or get_default_collection_name()
        self._client: Optional[Any] = None
        self._collection: Optional[Any] = None

    @classmethod
    def get_instance(cls, persist_directory: str = VECTOR_STORE_DIR, collection_name: Optional[str] = None) -> 'VectorStoreService':
        """
        Singleton pattern to ensure persistent ChromaDB client is initialized once and reused.
        """
        target_coll = collection_name or get_default_collection_name()
        if cls._instance is None or cls._instance.collection_name != target_coll:
            cls._instance = cls(persist_directory=persist_directory, collection_name=target_coll)
        return cls._instance

    @property
    def is_initialized(self) -> bool:
        """
        Returns True if the ChromaDB client and collection have been initialized.
        """
        return self._client is not None and self._collection is not None

    def _init_db(self):
        """
        Initializes persistent ChromaDB client and gets or creates the target collection.
        Lazy initialization: connects to ChromaDB only when actually needed.
        """
        if self._client is None or self._collection is None:
            import chromadb
            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_directory)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """
        Persists a list of embedded DocumentChunk objects into ChromaDB.
        Uses upsert to ensure stable IDs and avoid duplicate records.
        """
        if not chunks:
            return 0

        collection = self._init_db()
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for c in chunks:
            if not c.embedding:
                raise ValueError(f"Chunk '{c.chunk_id}' is missing embedding vector.")

            ids.append(c.chunk_id)
            embeddings.append(c.embedding)
            documents.append(c.chunk_text)

            meta = {
                "document_id": c.document_id,
                "filename": c.filename,
                "file_type": c.file_type or "",
                "chunk_index": c.chunk_index,
                "character_count": c.character_count,
                "embedding_model": c.embedding_model or "",
                "embedding_dimension": c.embedding_dimension or len(c.embedding),
                "pages": c.pages if c.pages is not None else -1
            }
            metadatas.append(meta)

        # Batch upsert to ChromaDB
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return len(ids)

    def delete_document_chunks(self, document_id: str) -> int:
        """
        Deletes all stored vector records associated with a document_id.
        Allows clean re-indexing without leaving stale duplicate chunks.
        """
        collection = self._init_db()
        try:
            # Query existing chunks for count
            existing = collection.get(where={"document_id": document_id})
            count = len(existing.get("ids", []))
            if count > 0:
                collection.delete(where={"document_id": document_id})
            return count
        except Exception:
            return 0

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single chunk by chunk_id from ChromaDB.
        """
        try:
            collection = self._init_db()
            res = collection.get(ids=[chunk_id], include=["embeddings", "documents", "metadatas"])
            if res and res.get("ids") and len(res["ids"]) > 0:
                return {
                    "chunk_id": res["ids"][0],
                    "document": res["documents"][0] if res.get("documents") else "",
                    "metadata": res["metadatas"][0] if res.get("metadatas") else {},
                    "embedding": res["embeddings"][0] if res.get("embeddings") is not None else None
                }
        except Exception:
            pass
        return None

    def count_chunks(self) -> int:
        """
        Returns the total count of vector chunks in the collection.
        """
        collection = self._init_db()
        return collection.count()

    def query_similar_chunks(self, query_embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """
        Queries ChromaDB collection using a 384-dim query embedding vector.
        ChromaDB uses HNSW with Cosine Distance (hnsw:space = cosine).
        Returns dictionary containing ids, documents, metadatas, and distances.
        """
        collection = self._init_db()
        total_count = collection.count()
        if total_count == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        n_results = min(top_k, total_count)
        res = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return res

    def get_health(self) -> Dict[str, Any]:
        """
        Returns health and status metadata for the vector store.
        """
        collection = self._init_db()
        return {
            "status": "healthy",
            "collection": self.collection_name,
            "collection_name": self.collection_name,
            "count": collection.count(),
            "persisted": True
        }



vector_store_service = VectorStoreService.get_instance()

