import os
import json
import math
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

DEFAULT_MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
DEFAULT_BATCH_SIZE = 32
GEMINI_EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
GEMINI_EMBEDDING_DIMENSION = int(os.environ.get("GEMINI_EMBEDDING_DIMENSION", "768"))


class EmbeddingService:
    _instance: Optional['EmbeddingService'] = None

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.environ.get("EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
        self._model: Optional[Any] = None
        self._dimension: Optional[int] = None
        self.provider = os.environ.get("EMBEDDING_PROVIDER", "auto").lower().strip()

    @property
    def active_model_name(self) -> str:
        """
        Returns the identifier of the active embedding model being used.
        """
        if self._should_use_gemini():
            return GEMINI_EMBEDDING_MODEL
        return self.model_name

    @classmethod
    def get_instance(cls, model_name: Optional[str] = None) -> 'EmbeddingService':
        """
        Singleton pattern to ensure embedding model is loaded once and reused across all requests.
        If a different model_name is explicitly requested, instantiates/returns appropriate service.
        """
        target_model = model_name or os.environ.get("EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
        if cls._instance is None or (model_name is not None and cls._instance.model_name != target_model):
            cls._instance = cls(model_name=target_model)
        return cls._instance

    def _get_api_key(self) -> Optional[str]:
        return (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("LLM_API_KEY")
            or os.environ.get("EMBEDDING_API_KEY")
        )

    def _should_use_gemini(self) -> bool:
        """
        Determines whether to use Google Gemini API for embeddings instead of local PyTorch model.
        In cloud deployment environments (e.g. Render where memory is strictly constrained to 512MB),
        using Gemini API consumes ~0MB model RAM, preventing OOM SIGKILL terminations.
        In local test environments, falls back to SentenceTransformer.
        """
        api_key = self._get_api_key()
        has_valid_key = bool(api_key and api_key.strip() and api_key.strip() not in ("mock_key", "your_api_key_here"))

        if self.provider == "gemini":
            return has_valid_key
        elif self.provider in ("local", "sentence-transformers", "torch"):
            return False
        elif self.provider == "auto":
            # Auto mode: use Gemini if running on Render or if explicitly flagged, and key is available
            is_cloud = bool(os.environ.get("RENDER") or os.environ.get("USE_CLOUD_EMBEDDINGS"))
            return is_cloud and has_valid_key
        return False

    @property
    def is_model_loaded(self) -> bool:
        """
        Returns True if the underlying embedding model has been loaded into memory.
        """
        if self._should_use_gemini():
            return True
        return self._model is not None

    def _load_model(self) -> Any:
        """
        Lazy initialization: loads SentenceTransformer model on CPU when first requested.
        Does NOT run at module import time or during FastAPI startup.
        """
        if self._model is None:
            try:
                import torch
                torch.set_num_threads(1)
                torch.set_grad_enabled(False)
            except Exception:
                pass
            from sentence_transformers import SentenceTransformer
            # Model execution on CPU with L2 normalization
            self._model = SentenceTransformer(self.model_name, device="cpu")
            try:
                if hasattr(self._model, "get_embedding_dimension"):
                    self._dimension = self._model.get_embedding_dimension() or 384
                elif hasattr(self._model, "get_sentence_embedding_dimension"):
                    self._dimension = self._model.get_sentence_embedding_dimension() or 384
                else:
                    self._dimension = 384
            except Exception:
                self._dimension = 384
        return self._model

    @property
    def dimension(self) -> int:
        """
        Returns the embedding dimension. If model is using Gemini in production, returns GEMINI_EMBEDDING_DIMENSION (768).
        If SentenceTransformer is used in local dev/tests, returns the known dimension (384).
        """
        if self._should_use_gemini():
            return GEMINI_EMBEDDING_DIMENSION
        if self._dimension is not None:
            return self._dimension
        return 384

    def _normalize(self, vector: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 1e-12:
            return [float(x / norm) for x in vector]
        return vector

    def _embed_gemini(self, texts: List[str], task_type: Optional[str] = None) -> Optional[List[List[float]]]:
        """
        Calls Google Gemini gemini-embedding-001 REST API requesting outputDimensionality.
        """
        api_key = self._get_api_key()
        if not api_key:
            return None

        target_dim = GEMINI_EMBEDDING_DIMENSION
        clean_model = GEMINI_EMBEDDING_MODEL
        if clean_model.startswith("models/"):
            clean_model = clean_model[len("models/"):]

        try:
            if len(texts) == 1:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:embedContent?key={api_key}"
                payload: Dict[str, Any] = {
                    "model": GEMINI_EMBEDDING_MODEL,
                    "content": {"parts": [{"text": texts[0]}]},
                    "outputDimensionality": target_dim
                }
                if task_type:
                    payload["taskType"] = task_type
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    values = data.get("embedding", {}).get("values", [])
                    if values and len(values) == target_dim:
                        return [self._normalize(values)]
            else:
                all_embeddings = []
                batch_size = 50
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:batchEmbedContents?key={api_key}"
                    requests_list = []
                    for t in batch:
                        item: Dict[str, Any] = {
                            "model": GEMINI_EMBEDDING_MODEL,
                            "content": {"parts": [{"text": t}]},
                            "outputDimensionality": target_dim
                        }
                        if task_type:
                            item["taskType"] = task_type
                        requests_list.append(item)
                    payload = {"requests": requests_list}
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        embeddings = data.get("embeddings", [])
                        for emb_obj in embeddings:
                            vals = emb_obj.get("values", [])
                            if vals and len(vals) == target_dim:
                                all_embeddings.append(self._normalize(vals))
                            else:
                                return None
                return all_embeddings
        except Exception:
            return None
        return None

    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a single string into a normalized floating-point numerical vector.
        Raises ValueError if text is empty or whitespace.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty or whitespace-only text.")

        clean_text = text.strip()

        if self._should_use_gemini():
            res = self._embed_gemini([clean_text], task_type="RETRIEVAL_QUERY")
            if res and len(res) > 0:
                return res[0]

        model = self._load_model()
        vector = model.encode(clean_text, normalize_embeddings=True)
        return vector.tolist()

    def embed_chunks(self, chunks: List[Any], batch_size: int = DEFAULT_BATCH_SIZE) -> List[Any]:
        """
        Embeds a list of DocumentChunk objects in batches.
        Attaches 'embedding', 'embedding_dimension', and 'embedding_model' to each chunk.
        """
        if not chunks:
            return []

        texts = [c.chunk_text for c in chunks]

        if self._should_use_gemini():
            vectors = self._embed_gemini(texts, task_type="RETRIEVAL_DOCUMENT")
            if vectors and len(vectors) == len(chunks):
                for chunk, vec_list in zip(chunks, vectors):
                    chunk.embedding = vec_list
                    chunk.embedding_dimension = len(vec_list)
                    chunk.embedding_model = GEMINI_EMBEDDING_MODEL
                return chunks

        model = self._load_model()
        # Batch encoding on CPU
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        for chunk, vector in zip(chunks, vectors):
            vec_list = vector.tolist()
            chunk.embedding = vec_list
            chunk.embedding_dimension = len(vec_list)
            chunk.embedding_model = self.model_name

        return chunks


embedding_service = EmbeddingService.get_instance()

