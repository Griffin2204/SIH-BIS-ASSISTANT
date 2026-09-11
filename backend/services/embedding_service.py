import os
from typing import List, Dict, Any, Optional

DEFAULT_MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
DEFAULT_BATCH_SIZE = 32


class EmbeddingService:
    _instance: Optional['EmbeddingService'] = None

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.environ.get("EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
        self._model: Optional[Any] = None
        self._dimension: Optional[int] = None

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

    @property
    def is_model_loaded(self) -> bool:
        """
        Returns True if the underlying embedding model has been loaded into memory.
        """
        return self._model is not None

    def _load_model(self) -> Any:
        """
        Lazy initialization: loads SentenceTransformer model on CPU when first requested.
        Does NOT run at module import time or during FastAPI startup.
        """
        if self._model is None:
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
        Returns the embedding dimension. If model is not loaded yet, returns the
        known dimension (384) without triggering heavyweight model download or loading.
        """
        if self._dimension is not None:
            return self._dimension
        return 384

    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a single string into a normalized floating-point numerical vector.
        Raises ValueError if text is empty or whitespace.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty or whitespace-only text.")

        model = self._load_model()
        vector = model.encode(text.strip(), normalize_embeddings=True)
        return vector.tolist()

    def embed_chunks(self, chunks: List[Any], batch_size: int = DEFAULT_BATCH_SIZE) -> List[Any]:
        """
        Embeds a list of DocumentChunk objects in batches.
        Attaches 'embedding', 'embedding_dimension', and 'embedding_model' to each chunk.
        """
        if not chunks:
            return []

        model = self._load_model()
        texts = [c.chunk_text for c in chunks]

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

