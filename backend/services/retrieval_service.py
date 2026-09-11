import os
from typing import List, Dict, Any, Optional
from services.embedding_service import EmbeddingService, embedding_service
from services.vector_store import VectorStoreService, vector_store_service

DEFAULT_TOP_K = 5
MAX_TOP_K = 20


class RetrievalService:
    _instance: Optional['RetrievalService'] = None

    def __init__(self, emb_service: Optional[EmbeddingService] = None, vs_service: Optional[VectorStoreService] = None):
        self.embedding_service = emb_service or EmbeddingService.get_instance()
        self.vector_store_service = vs_service or VectorStoreService.get_instance()

    @classmethod
    def get_instance(cls) -> 'RetrievalService':
        """
        Singleton pattern to ensure RetrievalService is initialized once and reused across all requests.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def retrieve(self, question: str, top_k: int = DEFAULT_TOP_K) -> Dict[str, Any]:
        """
        Performs semantic similarity retrieval for a user question.
        
        Steps:
        1. Validate question non-empty and top_k parameter bounds.
        2. Convert question to 384-dim normalized query vector using all-MiniLM-L6-v2.
        3. Search local persistent ChromaDB collection ('bis_documents').
        4. Calculate Cosine Similarity from Cosine Distance:
           ChromaDB returns Cosine Distance d = 1 - cos(theta) for hnsw:space = cosine.
           Since vectors are L2-normalized (|v|_2 = 1.0), Cosine Similarity s = cos(theta) = 1.0 - d.
        5. Return structured top-k results sorted by relevance.
        """
        # 1. Validation
        if not question or not question.strip():
            raise ValueError("Question cannot be empty or whitespace-only.")

        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            raise ValueError(f"top_k must be a positive integer >= 1. Received: {top_k}")

        if top_k > MAX_TOP_K:
            raise ValueError(f"top_k exceeds maximum allowed limit of {MAX_TOP_K}. Received: {top_k}")

        clean_question = question.strip()
        if len(clean_question) > 1000:
            raise ValueError("Question exceeds maximum allowed length of 1000 characters.")

        # 2. Generate Query Embedding using existing EmbeddingService
        query_vector = self.embedding_service.embed_text(clean_question)

        # 3. Perform ChromaDB Semantic Search using existing VectorStoreService
        raw_res = self.vector_store_service.query_similar_chunks(query_vector, top_k=top_k)

        ids_list = raw_res.get("ids", [[]])[0]
        docs_list = raw_res.get("documents", [[]])[0]
        metas_list = raw_res.get("metadatas", [[]])[0]
        dists_list = raw_res.get("distances", [[]])[0]

        results = []
        for i in range(len(ids_list)):
            chunk_id = ids_list[i]
            chunk_text = docs_list[i] if i < len(docs_list) else ""
            raw_meta = metas_list[i] if i < len(metas_list) else None
            meta = raw_meta if (raw_meta is not None and isinstance(raw_meta, dict)) else {}
            dist = dists_list[i] if i < len(dists_list) else 0.0

            # Distance & Similarity calculation for ChromaDB cosine space
            distance_val = round(float(dist), 4)
            # Mathematical conversion: similarity_score = 1.0 - Cosine_Distance
            similarity_val = round(1.0 - distance_val, 4)

            pages_val = meta.get("pages")
            if pages_val == -1:
                pages_val = None

            results.append({
                "chunk_id": chunk_id,
                "document_id": meta.get("document_id", ""),
                "filename": meta.get("filename", ""),
                "file_type": meta.get("file_type", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "chunk_text": chunk_text,
                "character_count": meta.get("character_count", len(chunk_text)),
                "embedding_model": meta.get("embedding_model", self.embedding_service.model_name),
                "embedding_dimension": meta.get("embedding_dimension", self.embedding_service.dimension),
                "pages": pages_val,
                "distance": distance_val,
                "similarity_score": similarity_val
            })

        return {
            "question": clean_question,
            "results": results,
            "total_results": len(results)
        }


retrieval_service = RetrievalService.get_instance()
