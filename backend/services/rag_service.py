import os
from typing import List, Dict, Any, Optional
from services.retrieval_service import RetrievalService, retrieval_service
from services.llm_service import LLMService, llm_service, LLMNotConfiguredError, LLMGenerationError

from services.language_service import language_service

DEFAULT_RAG_TOP_K = 5
DEFAULT_MAX_CONTEXT_CHARS = 6000
MIN_SIMILARITY_THRESHOLD = 0.05  # Threshold below which context is deemed non-relevant

NO_CONTEXT_FALLBACK_MESSAGES = {
    "en": "I couldn't find enough relevant information in the available reference material to answer that question.",
    "hi": "उपलब्ध संदर्भ सामग्री में इस प्रश्न का उत्तर देने के लिए पर्याप्त प्रासंगिक जानकारी नहीं मिली।",
    "mr": "उपलब्ध संदर्भ साहित्यामध्ये या प्रश्नाचे उत्तर देण्यासाठी पुरेशी संबंधित माहिती सापडली नाही."
}


class RAGService:
    _instance: Optional['RAGService'] = None

    def __init__(
        self,
        ret_service: Optional[RetrievalService] = None,
        l_service: Optional[LLMService] = None,
        max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
        similarity_threshold: float = MIN_SIMILARITY_THRESHOLD
    ):
        self.retrieval_service = ret_service or RetrievalService.get_instance()
        self.llm_service = l_service or LLMService.get_instance()
        self.max_context_chars = max_context_chars
        self.similarity_threshold = similarity_threshold

    @classmethod
    def get_instance(cls) -> 'RAGService':
        """
        Singleton getter for RAGService.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def construct_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Assembles retrieved document chunks into a bounded, formatted reference context string.
        Preserves complete chunks and top-ranked chunks first.
        """
        context_str, _ = self.construct_context_with_used_chunks(chunks)
        return context_str

    def construct_context_with_used_chunks(self, chunks: List[Dict[str, Any]]) -> tuple:
        """
        Assembles retrieved document chunks into a bounded context string and returns
        both the context string and the list of chunks actually included within max_context_chars.
        """
        if not chunks:
            return "", []

        context_blocks = []
        used_chunks = []
        current_length = 0

        for chunk in chunks:
            filename = chunk.get("filename") or "Document"
            chunk_idx = chunk.get("chunk_index", 0)
            text = chunk.get("chunk_text", "").strip()

            if not text:
                continue

            block = f"--- Document: {filename} (Chunk {chunk_idx}) ---\n{text}\n"
            block_len = len(block)

            if current_length + block_len > self.max_context_chars:
                if not context_blocks:
                    # If single top chunk is longer than limit, include truncated chunk to avoid empty context
                    context_blocks.append(block[:self.max_context_chars])
                    used_chunks.append(chunk)
                break

            context_blocks.append(block)
            used_chunks.append(chunk)
            current_length += block_len

        return "\n".join(context_blocks).strip(), used_chunks

    def _format_sources(self, used_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Converts context-included chunks into clean, user-facing source citation objects.
        Excludes embedding vectors, raw ChromaDB internal objects, and local filesystem paths.
        """
        sources = []
        for chunk in used_chunks:
            raw_text = (chunk.get("chunk_text") or "").strip()
            snippet = (raw_text[:200] + "...") if len(raw_text) > 200 else raw_text

            pages_raw = chunk.get("pages")
            pages_val = None
            if pages_raw is not None:
                if isinstance(pages_raw, list):
                    clean_pages = [p for p in pages_raw if isinstance(p, int) and p > 0]
                    pages_val = clean_pages if clean_pages else None
                elif isinstance(pages_raw, int) and pages_raw > 0:
                    pages_val = [pages_raw]

            source_item = {
                "document_id": str(chunk.get("document_id", "")),
                "filename": str(chunk.get("filename", "")),
                "file_type": str(chunk.get("file_type") or "txt"),
                "chunk_id": str(chunk.get("chunk_id", "")),
                "chunk_index": int(chunk.get("chunk_index", 0)),
                "similarity_score": round(float(chunk.get("similarity_score", 0.0)), 4),
                "pages": pages_val,
                "snippet": snippet
            }
            sources.append(source_item)
        return sources

    def answer_question(self, question: str, top_k: int = DEFAULT_RAG_TOP_K, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes end-to-end RAG pipeline:
        1. Validate question non-empty.
        2. Resolve target response language (auto-detect or explicit override).
        3. Verify LLM service configuration.
        4. Retrieve top-k relevant document chunks via RetrievalService.
        5. Check for empty or non-relevant context (localized fallback if insufficient).
        6. Build bounded reference context string and track context-included chunks.
        7. Generate grounded answer using LLMService in requested language.
        8. Return structured RAG response with accurate source citations and language code.
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty or whitespace-only.")

        clean_question = question.strip()

        # Resolve target language
        resolved_lang = language_service.resolve_language(clean_question, explicit_lang=language)
        lang_display_name = language_service.get_language_name(resolved_lang)
        fallback_msg = NO_CONTEXT_FALLBACK_MESSAGES.get(resolved_lang, NO_CONTEXT_FALLBACK_MESSAGES["en"])

        # Check LLM configuration before executing network retrieval
        if not self.llm_service.is_configured():
            raise LLMNotConfiguredError("LLM service is not configured. Please set LLM_API_KEY in environment.")

        # Perform semantic retrieval
        retrieval_res = self.retrieval_service.retrieve(clean_question, top_k=top_k)
        chunks = retrieval_res.get("results", [])

        # Check for empty retrieval or zero results
        if not chunks or retrieval_res.get("total_results", 0) == 0:
            return {
                "question": clean_question,
                "answer": fallback_msg,
                "language": resolved_lang,
                "sources": []
            }

        # Quality check: verify at least one chunk satisfies minimum similarity threshold
        best_sim = chunks[0].get("similarity_score", 0.0)
        if best_sim < self.similarity_threshold:
            return {
                "question": clean_question,
                "answer": fallback_msg,
                "language": resolved_lang,
                "sources": []
            }

        # Construct bounded context string & track used chunks
        context_str, used_chunks = self.construct_context_with_used_chunks(chunks)

        if not context_str or not used_chunks:
            return {
                "question": clean_question,
                "answer": fallback_msg,
                "language": resolved_lang,
                "sources": []
            }

        # Generate grounded answer via LLM in requested language
        answer = self.llm_service.generate_answer(clean_question, context_str, target_language=lang_display_name)

        # Format source citations strictly for used chunks
        sources = self._format_sources(used_chunks)

        return {
            "question": clean_question,
            "answer": answer,
            "language": resolved_lang,
            "sources": sources
        }


rag_service = RAGService.get_instance()

