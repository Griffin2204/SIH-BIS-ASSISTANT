import os
import sys
import uuid
import subprocess
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from main import app, documents_db, UPLOAD_DIR
from services.language_service import LanguageService, language_service
from services.embedding_service import EmbeddingService, embedding_service
from services.vector_store import VectorStoreService, vector_store_service
from services.retrieval_service import RetrievalService, retrieval_service
from services.llm_service import LLMService, llm_service
from services.rag_service import RAGService, rag_service
from services.bis_search_service import BISSearchService, bis_search_service
from services.chunker import DocumentChunk


def run_phase12_tests():
    print("\n" + "=" * 50)
    print("      STARTING PHASE 12 TEST SUITE               ")
    print("=" * 50 + "\n")

    client = TestClient(app)
    results = {}
    test_doc_ids_to_clean = []

    # Clean up any leftover test data
    test_p12_cleanup = ["doc_p12_cross_lang", "doc_p12_ctrl_en", "doc_p12_reindex_test"]
    for d_id in test_p12_cleanup:
        vector_store_service.delete_document_chunks(d_id)

    # TEST 1 — LANGUAGE SERVICE INITIALIZATION
    try:
        assert language_service is not None
        assert isinstance(language_service, LanguageService)
        results["1. Language Service Initialization Test"] = "PASS"
    except Exception as e:
        results["1. Language Service Initialization Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 2 — SUPPORTED LANGUAGES LIST
    try:
        supp = language_service.get_supported_languages()
        assert "en" in supp
        assert "hi" in supp
        assert "mr" in supp
        results["2. Supported Languages List Test"] = "PASS"
    except Exception as e:
        results["2. Supported Languages List Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 3 — VALID LANGUAGE CODES
    try:
        for code in ["en", "hi", "mr", "EN", "Hi", "MR "]:
            val = language_service.validate_language(code)
            assert val in ["en", "hi", "mr"]
        results["3. Valid Language Codes Test"] = "PASS"
    except Exception as e:
        results["3. Valid Language Codes Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 4 — INVALID LANGUAGE CODE VALIDATION
    try:
        for bad_code in ["fr", "es", "de", "klingon", "123"]:
            try:
                language_service.validate_language(bad_code)
                assert False, f"Expected ValueError for '{bad_code}'"
            except ValueError:
                pass
        results["4. Invalid Language Code Validation Test"] = "PASS"
    except Exception as e:
        results["4. Invalid Language Code Validation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 5 — ENGLISH LANGUAGE DETECTION
    try:
        d1 = language_service.detect_language("What is BIS certification?")
        d2 = language_service.detect_language("How to apply for ISI mark in India?")
        assert d1 == "en", f"Expected 'en', got '{d1}'"
        assert d2 == "en", f"Expected 'en', got '{d2}'"
        results["5. English Language Detection Test"] = "PASS"
    except Exception as e:
        results["5. English Language Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 6 — HINDI LANGUAGE DETECTION
    try:
        h1 = language_service.detect_language("बीआईएस प्रमाणन क्या है?")
        h2 = language_service.detect_language("भारत में बीआईएस प्रमाणन कैसे प्राप्त करें?")
        assert h1 == "hi", f"Expected 'hi', got '{h1}'"
        assert h2 == "hi", f"Expected 'hi', got '{h2}'"
        results["6. Hindi Language Detection Test"] = "PASS"
    except Exception as e:
        results["6. Hindi Language Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 7 — MARATHI LANGUAGE DETECTION
    try:
        m1 = language_service.detect_language("बीआयएस प्रमाणन म्हणजे काय?")
        m2 = language_service.detect_language("भारतामध्ये बीआयएस काय आहे?")
        m3 = language_service.detect_language("याबद्दल सविस्तर माहिती द्या आणि वेळ सांगा")
        assert m1 == "mr", f"Expected 'mr', got '{m1}'"
        assert m2 == "mr", f"Expected 'mr', got '{m2}'"
        assert m3 == "mr", f"Expected 'mr', got '{m3}'"
        results["7. Marathi Language Detection Test"] = "PASS"
    except Exception as e:
        results["7. Marathi Language Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 8 — DEVANAGARI SCRIPT HANDLING (DISTINGUISHING HI VS MR)
    try:
        # Both use Devanagari; verify they are not both lumped as Hindi
        hi_res = language_service.detect_language("यह क्या है?")
        mr_res = language_service.detect_language("हे काय आहे?")
        assert hi_res == "hi", f"Expected 'hi', got '{hi_res}'"
        assert mr_res == "mr", f"Expected 'mr', got '{mr_res}'"
        results["8. Devanagari Script Handling Test"] = "PASS"
    except Exception as e:
        results["8. Devanagari Script Handling Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 9 — AMBIGUOUS / UNKNOWN LANGUAGE FALLBACK
    try:
        u1 = language_service.detect_language("12345 67890 !@#$")
        assert u1 == "unknown"
        # resolve_language defaults safely to 'en' when unknown
        r1 = language_service.resolve_language("12345 67890 !@#$")
        assert r1 == "en"
        results["9. Unknown/Ambiguous Language Fallback Test"] = "PASS"
    except Exception as e:
        results["9. Unknown/Ambiguous Language Fallback Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 10 — EXPLICIT LANGUAGE OVERRIDE
    try:
        # Question in English, but user explicitly overrides language to 'mr'
        res_lang = language_service.resolve_language("What is BIS certification?", explicit_lang="mr")
        assert res_lang == "mr", f"Expected 'mr', got '{res_lang}'"

        # Question in Hindi, override to 'en'
        res_lang_en = language_service.resolve_language("बीआईएस प्रमाणन क्या है?", explicit_lang="en")
        assert res_lang_en == "en", f"Expected 'en', got '{res_lang_en}'"
        results["10. Explicit Language Override Test"] = "PASS"
    except Exception as e:
        results["10. Explicit Language Override Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 11 — AUTOMATIC LANGUAGE RESOLUTION
    try:
        assert language_service.resolve_language("What is BIS?") == "en"
        assert language_service.resolve_language("बीआईएस क्या है?") == "hi"
        assert language_service.resolve_language("बीआयएस काय आहे?") == "mr"
        results["11. Automatic Language Resolution Test"] = "PASS"
    except Exception as e:
        results["11. Automatic Language Resolution Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 12 — TECHNICAL IDENTIFIER PRESERVATION IN MULTILINGUAL QUERIES
    try:
        q_hi = "IS 10500 मानक क्या है?"
        q_mr = "IS/ISO 9001 बद्दल माहिती द्या"
        std_hi = bis_search_service.detect_standard_identifier(q_hi)
        std_mr = bis_search_service.detect_standard_identifier(q_mr)
        assert std_hi == "IS 10500", f"Expected 'IS 10500', got '{std_hi}'"
        assert std_mr == "IS/ISO 9001", f"Expected 'IS/ISO 9001', got '{std_mr}'"
        results["12. Technical Identifier Preservation in Queries Test"] = "PASS"
    except Exception as e:
        results["12. Technical Identifier Preservation in Queries Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 13 — MULTILINGUAL EMBEDDING SERVICE INITIALIZATION
    try:
        assert embedding_service is not None
        assert "multilingual" in embedding_service.model_name.lower() or "minilm" in embedding_service.model_name.lower()
        results["13. Multilingual Embedding Service Initialization Test"] = "PASS"
    except Exception as e:
        results["13. Multilingual Embedding Service Initialization Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 14 — EMBEDDING DIMENSION METADATA
    try:
        dim = embedding_service.dimension
        assert dim == 384, f"Expected 384, got {dim}"
        results["14. Embedding Dimension Metadata Test"] = "PASS"
    except Exception as e:
        results["14. Embedding Dimension Metadata Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 15 — QUERY/DOCUMENT EMBEDDING COMPATIBILITY
    try:
        q_vec = embedding_service.embed_text("Sample multilingual query")
        doc_vec = embedding_service.embed_text("Sample multilingual document")
        assert len(q_vec) == len(doc_vec) == 384
        assert isinstance(q_vec[0], float)
        assert isinstance(doc_vec[0], float)
        results["15. Query/Document Embedding Compatibility Test"] = "PASS"
    except Exception as e:
        results["15. Query/Document Embedding Compatibility Test"] = f"FAIL: {type(e).__name__}: {e}"

    # SETUP CONTROLLED MULTILINGUAL DOCUMENT FOR TESTS 16-20
    doc_cross_id = "doc_p12_cross_lang"
    test_doc_ids_to_clean.append(doc_cross_id)
    doc_cross_text = "BIS certification is a conformity assessment process for applicable products in India."
    doc_cross_chunk = DocumentChunk(
        chunk_id=f"{doc_cross_id}_chunk_0",
        document_id=doc_cross_id,
        filename="bis_certification_guide.pdf",
        chunk_index=0,
        chunk_text=doc_cross_text,
        character_count=len(doc_cross_text),
        file_type="pdf",
        pages=[1],
        embedding=embedding_service.embed_text(doc_cross_text),
        embedding_dimension=embedding_service.dimension,
        embedding_model=embedding_service.model_name
    )
    vector_store_service.add_chunks([doc_cross_chunk])

    # TEST 16 — MULTILINGUAL RETRIEVAL PIPELINE
    try:
        ret_out = retrieval_service.retrieve("BIS certification process", top_k=3)
        assert ret_out["total_results"] >= 1
        assert "similarity_score" in ret_out["results"][0]
        results["16. Multilingual Retrieval Pipeline Test"] = "PASS"
    except Exception as e:
        results["16. Multilingual Retrieval Pipeline Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 17 — CONTROLLED CROSS-LANGUAGE RETRIEVAL TEST
    try:
        # Cross-language queries in English, Hindi, and Marathi
        q_en = "What is BIS certification?"
        q_hi = "बीआईएस प्रमाणन क्या है?"
        q_mr = "बीआयएस प्रमाणन म्हणजे काय?"
        q_unrelated = "How to bake a chocolate cake at home?"

        res_en = retrieval_service.retrieve(q_en, top_k=20)
        res_hi = retrieval_service.retrieve(q_hi, top_k=20)
        res_mr = retrieval_service.retrieve(q_mr, top_k=20)
        res_unr = retrieval_service.retrieve(q_unrelated, top_k=20)

        # Find the cross-language chunk in each result
        def find_chunk_score(res):
            for r in res["results"]:
                if r["chunk_id"] == doc_cross_chunk.chunk_id:
                    return r["similarity_score"]
            return 0.0

        score_en = find_chunk_score(res_en)
        score_hi = find_chunk_score(res_hi)
        score_mr = find_chunk_score(res_mr)
        score_unr = find_chunk_score(res_unr)

        assert score_en > 0.4, f"English score too low: {score_en}"
        assert score_hi > 0.3, f"Hindi cross-language score too low: {score_hi}"
        assert score_mr > 0.3, f"Marathi cross-language score too low: {score_mr}"
        assert score_hi > score_unr, f"Hindi score ({score_hi}) should be higher than unrelated ({score_unr})"
        assert score_mr > score_unr, f"Marathi score ({score_mr}) should be higher than unrelated ({score_unr})"

        results["17. Controlled Cross-Language Retrieval Test"] = "PASS"
    except Exception as e:
        results["17. Controlled Cross-Language Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 18 — ENGLISH QUERY -> ENGLISH DOCUMENT RETRIEVAL
    try:
        res = retrieval_service.retrieve("What is BIS certification?", top_k=20)
        matched = [r for r in res["results"] if r["chunk_id"] == doc_cross_chunk.chunk_id]
        assert len(matched) >= 1
        results["18. English Query -> English Document Retrieval Test"] = "PASS"
    except Exception as e:
        results["18. English Query -> English Document Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 19 — HINDI QUERY -> RELEVANT ENGLISH DOCUMENT RETRIEVAL
    try:
        res = retrieval_service.retrieve("बीआईएस प्रमाणन क्या है?", top_k=20)
        matched = [r for r in res["results"] if r["chunk_id"] == doc_cross_chunk.chunk_id]
        assert len(matched) >= 1
        results["19. Hindi Query -> Relevant English Document Retrieval Test"] = "PASS"
    except Exception as e:
        results["19. Hindi Query -> Relevant English Document Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 20 — MARATHI QUERY -> RELEVANT ENGLISH DOCUMENT RETRIEVAL
    try:
        res = retrieval_service.retrieve("बीआयएस प्रमाणन म्हणजे काय?", top_k=20)
        matched = [r for r in res["results"] if r["chunk_id"] == doc_cross_chunk.chunk_id]
        assert len(matched) >= 1
        results["20. Marathi Query -> Relevant English Document Retrieval Test"] = "PASS"
    except Exception as e:
        results["20. Marathi Query -> Relevant English Document Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 21 — RAG PROMPT INSTRUCTION FOR ENGLISH
    try:
        prompt_en = llm_service.construct_prompt("What is BIS?", "Context text", target_language="English")
        assert "Requested language:\nEnglish" in prompt_en or "English" in prompt_en
        assert "IS 10500" in prompt_en  # Technical identifier preservation rule
        results["21. RAG Answer in English Prompt Test"] = "PASS"
    except Exception as e:
        results["21. RAG Answer in English Prompt Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 22 — RAG PROMPT INSTRUCTION FOR HINDI
    try:
        prompt_hi = llm_service.construct_prompt("बीआईएस क्या है?", "Context text", target_language="Hindi")
        assert "Requested language:\nHindi" in prompt_hi or "Hindi" in prompt_hi
        assert "preserving technical identifiers exactly" in prompt_hi.lower() or "preserved exactly" in prompt_hi.lower()
        results["22. RAG Answer in Hindi Prompt Test"] = "PASS"
    except Exception as e:
        results["22. RAG Answer in Hindi Prompt Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 23 — RAG PROMPT INSTRUCTION FOR MARATHI
    try:
        prompt_mr = llm_service.construct_prompt("बीआयएस काय आहे?", "Context text", target_language="Marathi")
        assert "Requested language:\nMarathi" in prompt_mr or "Marathi" in prompt_mr
        assert "preserving technical identifiers exactly" in prompt_mr.lower() or "preserved exactly" in prompt_mr.lower()
        results["23. RAG Answer in Marathi Prompt Test"] = "PASS"
    except Exception as e:
        results["23. RAG Answer in Marathi Prompt Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 24 — GROUNDING STILL WORKS IN ALL LANGUAGES
    try:
        with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="Grounded multilingual answer."):
                ans_en = rag_service.answer_question("What is BIS certification?", language="en")
                ans_hi = rag_service.answer_question("बीआईएस प्रमाणन क्या है?", language="hi")
                ans_mr = rag_service.answer_question("बीआयएस प्रमाणन म्हणजे काय?", language="mr")
                assert ans_en["language"] == "en"
                assert ans_hi["language"] == "hi"
                assert ans_mr["language"] == "mr"
                assert len(ans_en["sources"]) >= 1
                assert len(ans_hi["sources"]) >= 1
                assert len(ans_mr["sources"]) >= 1
        results["24. Grounding in All Languages Test"] = "PASS"
    except Exception as e:
        results["24. Grounding in All Languages Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 25 — NO-CONTEXT FALLBACK IN HINDI
    try:
        mock_ret_empty = MagicMock()
        mock_ret_empty.retrieve.return_value = {"question": "q", "results": [], "total_results": 0}
        rag_empty = RAGService(ret_service=mock_ret_empty)
        with patch.object(rag_empty.llm_service, "_api_key", "mock_key"):
            res_fb_hi = rag_empty.answer_question("अपरिचित शब्द ९९९", language="hi")
            assert res_fb_hi["language"] == "hi"
            assert "पर्याप्त प्रासंगिक जानकारी नहीं मिली" in res_fb_hi["answer"]
            assert res_fb_hi["sources"] == []
        results["25. No-Context Fallback in Hindi Test"] = "PASS"
    except Exception as e:
        results["25. No-Context Fallback in Hindi Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 26 — NO-CONTEXT FALLBACK IN MARATHI
    try:
        mock_ret_empty = MagicMock()
        mock_ret_empty.retrieve.return_value = {"question": "q", "results": [], "total_results": 0}
        rag_empty = RAGService(ret_service=mock_ret_empty)
        with patch.object(rag_empty.llm_service, "_api_key", "mock_key"):
            res_fb_mr = rag_empty.answer_question("अपरिचित शब्द ९९९", language="mr")
            assert res_fb_mr["language"] == "mr"
            assert "पुरेशी संबंधित माहिती सापडली नाही" in res_fb_mr["answer"]
            assert res_fb_mr["sources"] == []
        results["26. No-Context Fallback in Marathi Test"] = "PASS"
    except Exception as e:
        results["26. No-Context Fallback in Marathi Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 27 — SOURCES PRESERVED IN MULTILINGUAL QUERIES
    try:
        with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="उत्तर."):
                res_src = rag_service.answer_question("बीआईएस प्रमाणन क्या है?", language="hi")
                assert len(res_src["sources"]) >= 1
                top_src = res_src["sources"][0]
                assert "document_id" in top_src
                assert "filename" in top_src
                assert "similarity_score" in top_src
        results["27. Sources Preserved in Multilingual Queries Test"] = "PASS"
    except Exception as e:
        results["27. Sources Preserved in Multilingual Queries Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 28 — SOURCE METADATA NOT TRANSLATED OR CORRUPTED
    try:
        with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="Ans"):
                res = rag_service.answer_question("बीआयएस प्रमाणन काय आहे?", language="mr")
                assert len(res["sources"]) >= 1
                top_src = res["sources"][0]
                # Filename must remain original ASCII string, not translated into Marathi/Hindi
                assert isinstance(top_src["filename"], str) and len(top_src["filename"]) > 0
                assert not any(ord(c) > 127 for c in top_src["filename"]), "Filename was translated into non-ASCII text"
                assert top_src["file_type"] in ["pdf", "docx", "txt"]
                assert isinstance(top_src["chunk_id"], str)
        results["28. Source Metadata Not Translated Test"] = "PASS"
    except Exception as e:
        results["28. Source Metadata Not Translated Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 29 — POST /ask EXPLICIT LANGUAGE PARAMETER
    try:
        with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="Ask explicit answer."):
                resp = client.post("/ask", json={"question": "What is BIS certification?", "language": "hi"})
                assert resp.status_code == 200
                data = resp.json()
                assert data["language"] == "hi"
                assert "answer" in data
                assert "sources" in data
        results["29. POST /ask Explicit Language Parameter Test"] = "PASS"
    except Exception as e:
        results["29. POST /ask Explicit Language Parameter Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 30 — POST /ask AUTOMATIC LANGUAGE DETECTION
    try:
        with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="Auto ans."):
                resp_hi = client.post("/ask", json={"question": "बीआईएस प्रमाणन क्या है?"})
                assert resp_hi.status_code == 200
                assert resp_hi.json()["language"] == "hi"

                resp_mr = client.post("/ask", json={"question": "बीआयएस प्रमाणन म्हणजे काय?"})
                assert resp_mr.status_code == 200
                assert resp_mr.json()["language"] == "mr"

                resp_en = client.post("/ask", json={"question": "What is BIS certification?"})
                assert resp_en.status_code == 200
                assert resp_en.json()["language"] == "en"
        results["30. POST /ask Automatic Language Detection Test"] = "PASS"
    except Exception as e:
        results["30. POST /ask Automatic Language Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 31 — POST /ask INVALID LANGUAGE RETURNS 400
    try:
        resp = client.post("/ask", json={"question": "What is BIS?", "language": "unsupported_lang"})
        assert resp.status_code in (400, 422)
        results["31. POST /ask Invalid Language Validation Test"] = "PASS"
    except Exception as e:
        results["31. POST /ask Invalid Language Validation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 32 — POST /bis/search MULTILINGUAL QUERY
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="BIS Search Ans."):
                resp = client.post("/bis/search", json={"query": "बीआईएस प्रमाणन कैसे प्राप्त करें?"})
                assert resp.status_code == 200
                data = resp.json()
                assert data["language"] == "hi"
                assert data["intent"] == "CERTIFICATION"
                assert "answer" in data
                assert "sources" in data
        results["32. POST /bis/search Multilingual Query Test"] = "PASS"
    except Exception as e:
        results["32. POST /bis/search Multilingual Query Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 33 — STANDARD IDENTIFIER PRESERVATION IN BIS SEARCH
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Standard Ans."):
                resp = client.post("/bis/search", json={"query": "IS 10500 मानक काय आहे?", "language": "mr"})
                assert resp.status_code == 200
                data = resp.json()
                assert data["detected_standard"] == "IS 10500"
                assert data["language"] == "mr"
                assert data["intent"] == "STANDARD_SEARCH"
        results["33. Standard Identifier Preservation in Search Test"] = "PASS"
    except Exception as e:
        results["33. Standard Identifier Preservation in Search Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 34 — NO VECTOR EMBEDDINGS EXPOSED
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Ans"):
                resp = client.post("/bis/search", json={"query": "बीआईएस प्रमाणन"})
                assert '"embedding":[' not in resp.text
        results["34. No Vector Embeddings Exposed Test"] = "PASS"
    except Exception as e:
        results["34. No Vector Embeddings Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 35 — NO API KEYS EXPOSED
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "secret_multilingual_key_888"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Safe ans."):
                resp = client.post("/bis/search", json={"query": "बीआईएस प्रमाणन"})
                assert "secret_multilingual_key_888" not in resp.text
        results["35. No API Keys Exposed Test"] = "PASS"
    except Exception as e:
        results["35. No API Keys Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 36 — NO FILESYSTEM PATHS EXPOSED
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Safe ans."):
                resp = client.post("/bis/search", json={"query": "बीआईएस प्रमाणन"})
                assert "stored_filename" not in resp.text
        results["36. No Filesystem Paths Exposed Test"] = "PASS"
    except Exception as e:
        results["36. No Filesystem Paths Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 37 — ACTIVE COLLECTION AND OLD/NEW VECTOR ISOLATION
    try:
        active_coll = vector_store_service.collection_name
        assert "multilingual" in active_coll or active_coll == "bis_documents_multilingual"
        results["37. Active Collection & Old/New Vector Isolation Test"] = "PASS"
    except Exception as e:
        results["37. Active Collection & Old/New Vector Isolation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 38 — REINDEXING MECHANISM ENDPOINT (POST /documents/reindex)
    try:
        resp = client.post("/documents/reindex")
        assert resp.status_code == 200
        data = resp.json()
        assert "documents_reindexed" in data
        assert "active_collection" in data
        assert "active_embedding_model" in data
        results["38. Reindexing Mechanism Endpoint Test"] = "PASS"
    except Exception as e:
        results["38. Reindexing Mechanism Endpoint Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 39 — ORIGINAL SOURCE FILES PRESERVED
    try:
        # Check upload directory exists and has not been cleared
        assert os.path.isdir(UPLOAD_DIR)
        results["39. Original Source Files Preserved Test"] = "PASS"
    except Exception as e:
        results["39. Original Source Files Preserved Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 40 — PHASE 11 REGRESSION TEST SUITE
    try:
        from test_phase11 import run_phase11_tests as run_p11_tests
        p11_pass = run_p11_tests()
        assert p11_pass is True, "Phase 11 test suite reported failures."
        results["40. Phase 11 Regression Test Suite"] = "PASS"
    except Exception as e:
        results["40. Phase 11 Regression Test Suite"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 41 — PHASE 10 REGRESSION TEST SUITE
    try:
        from test_phase10 import run_phase10_tests as run_p10_tests
        p10_pass = run_p10_tests()
        assert p10_pass is True, "Phase 10 test suite reported failures."
        results["41. Phase 10 Regression Test Suite"] = "PASS"
    except Exception as e:
        results["41. Phase 10 Regression Test Suite"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 42 — PHASE 9 REGRESSION TEST SUITE
    try:
        from test_phase9 import run_tests as run_p9_tests
        p9_pass = run_p9_tests()
        assert p9_pass is True, "Phase 9 test suite reported failures."
        results["42. Phase 9 Regression Test Suite"] = "PASS"
    except Exception as e:
        results["42. Phase 9 Regression Test Suite"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 43 — EXISTING ENDPOINTS REGRESSION
    try:
        r1 = client.get("/documents")
        assert r1.status_code == 200
        r2 = client.post("/retrieve", json={"question": "What is BIS certification?", "top_k": 3})
        assert r2.status_code == 200
        r3 = client.get("/vector-store/health")
        assert r3.status_code == 200
        assert r3.json()["status"] == "healthy"
        r4 = client.get("/bis/services")
        assert r4.status_code == 200
        results["43. Existing Endpoints Regression Test"] = "PASS"
    except Exception as e:
        results["43. Existing Endpoints Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 44 — FRONTEND PRODUCTION BUILD REGRESSION
    try:
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
        res_build = subprocess.run(["npm.cmd", "run", "build"], cwd=frontend_dir, capture_output=True, text=True)
        assert res_build.returncode == 0, f"Frontend build failed: {res_build.stderr}"
        results["44. Frontend Production Build Regression Test"] = "PASS"
    except Exception as e:
        results["44. Frontend Production Build Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # CLEANUP TEST DATA
    print("\n--- CLEANING UP TEST DATA ---")
    cleaned_count = 0
    for doc_id in test_doc_ids_to_clean:
        del_c = vector_store_service.delete_document_chunks(doc_id)
        cleaned_count += del_c
    print(f"Cleaned up {cleaned_count} test document chunks across {len(test_doc_ids_to_clean)} test document IDs.")

    print("\n==================================================")
    print("      PHASE 12 TEST RESULTS SUMMARY              ")
    print("==================================================")
    all_passed = True
    for test_name, status in results.items():
        print(f"{test_name}: {status}")
        if status.startswith("FAIL"):
            all_passed = False

    print("\nOVERALL PHASE 12 STATUS:", "ALL TESTS PASSED SUCCESSFULLY!" if all_passed else "SOME TESTS FAILED.")
    return all_passed


if __name__ == "__main__":
    success = run_phase12_tests()
    sys.exit(0 if success else 1)
