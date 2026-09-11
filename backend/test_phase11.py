import os
import sys
import json
import uuid
import subprocess
from unittest.mock import patch, MagicMock

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, BISServiceCategory, BISSearchRequest, BISSearchResponse
from services.bis_search_service import BISSearchService, bis_search_service, BIS_SERVICES_CATEGORIES
from services.vector_store import VectorStoreService, vector_store_service
from services.embedding_service import EmbeddingService, embedding_service
from services.retrieval_service import RetrievalService, retrieval_service
from services.llm_service import LLMService, llm_service
from services.rag_service import RAGService, rag_service
from services.chunker import DocumentChunk

from fastapi.testclient import TestClient

client = TestClient(app)


def run_phase11_tests():
    results = {}
    test_doc_ids_to_clean = []

    print("\n==================================================")
    print("      STARTING PHASE 11 TEST SUITE               ")
    print("==================================================\n")

    # Add setup test chunks so service search and standard search tests find relevant context
    p11_setup_chunk = DocumentChunk(
        chunk_id="doc_p11_setup_chunk_0",
        document_id="doc_p11_setup",
        filename="bis_certification_guide.pdf",
        chunk_index=0,
        chunk_text="Product certification process for ISI mark scheme requires factory inspection and testing of product samples.",
        character_count=108,
        file_type="pdf",
        pages=[1],
        embedding=embedding_service.embed_text("Product certification process for ISI mark scheme requires factory inspection and testing of product samples."),
        embedding_dimension=embedding_service.dimension,
        embedding_model=embedding_service.model_name
    )
    p11_is10500_chunk = DocumentChunk(
        chunk_id="doc_p11_is10500_chunk_0",
        document_id="doc_p11_is10500",
        filename="bis_is10500_spec.pdf",
        chunk_index=0,
        chunk_text="IS 10500 specifies drinking water requirements and quality parameters in India.",
        character_count=82,
        file_type="pdf",
        pages=[1],
        embedding=embedding_service.embed_text("IS 10500 specifies drinking water requirements and quality parameters in India."),
        embedding_dimension=embedding_service.dimension,
        embedding_model=embedding_service.model_name
    )
    vector_store_service.add_chunks([p11_setup_chunk, p11_is10500_chunk])
    test_doc_ids_to_clean.extend(["doc_p11_setup", "doc_p11_is10500"])

    # TEST 1 — GET /bis/services ENDPOINT
    try:
        resp = client.get("/bis/services")
        assert resp.status_code == 200
        cats = resp.json()
        assert isinstance(cats, list)
        assert len(cats) >= 11
        results["1. GET /bis/services Endpoint Test"] = "PASS"
    except Exception as e:
        results["1. GET /bis/services Endpoint Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 2 — SERVICE CATEGORY MODEL VERIFICATION
    try:
        sample_cat = BIS_SERVICES_CATEGORIES[0]
        cat_obj = BISServiceCategory(**sample_cat)
        assert cat_obj.id == "product_certification"
        assert cat_obj.name == "Product Certification"
        assert len(cat_obj.description) > 0
        results["2. Service Category Model Verification Test"] = "PASS"
    except Exception as e:
        results["2. Service Category Model Verification Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 3 — EMPTY SEARCH QUERY VALIDATION
    try:
        resp = client.post("/bis/search", json={"query": "   "})
        assert resp.status_code in (400, 422)
        results["3. Empty Search Validation Test"] = "PASS"
    except Exception as e:
        results["3. Empty Search Validation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 4 — INVALID SERVICE CATEGORY FILTER VALIDATION
    try:
        resp = client.post("/bis/search", json={"query": "certification", "service": "invalid_fake_category_id"})
        assert resp.status_code in (400, 422)
        results["4. Invalid Service Category Validation Test"] = "PASS"
    except Exception as e:
        results["4. Invalid Service Category Validation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 5 — GENERAL QUESTION INTENT DETECTION
    try:
        intent = bis_search_service.detect_intent("What does BIS do?")
        assert intent == "GENERAL_QUESTION"
        results["5. General Question Intent Detection Test"] = "PASS"
    except Exception as e:
        results["5. General Question Intent Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 6 — CERTIFICATION INTENT DETECTION
    try:
        intent = bis_search_service.detect_intent("How do I get BIS certification?")
        assert intent == "CERTIFICATION"
        results["6. Certification Intent Detection Test"] = "PASS"
    except Exception as e:
        results["6. Certification Intent Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 7 — STANDARD SEARCH INTENT DETECTION
    try:
        intent = bis_search_service.detect_intent("Find information about IS 10500")
        assert intent == "STANDARD_SEARCH"
        results["7. Standard Search Intent Detection Test"] = "PASS"
    except Exception as e:
        results["7. Standard Search Intent Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 8 — TESTING INTENT DETECTION
    try:
        intent = bis_search_service.detect_intent("What testing services are available?")
        assert intent == "TESTING"
        results["8. Testing Intent Detection Test"] = "PASS"
    except Exception as e:
        results["8. Testing Intent Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 9 — CONSUMER SERVICE INTENT DETECTION
    try:
        intent = bis_search_service.detect_intent("Consumer services for hallmarking and complaints")
        assert intent == "CONSUMER_SERVICE"
        results["9. Consumer Service Intent Detection Test"] = "PASS"
    except Exception as e:
        results["9. Consumer Service Intent Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 10 — INDUSTRY SERVICE INTENT DETECTION
    try:
        intent = bis_search_service.detect_intent("Factory audit services for industry manufacturers")
        assert intent == "INDUSTRY_SERVICE"
        results["10. Industry Service Intent Detection Test"] = "PASS"
    except Exception as e:
        results["10. Industry Service Intent Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 11 — UNKNOWN INTENT FALLBACK
    try:
        intent = bis_search_service.detect_intent("Random query 12345")
        assert intent == "UNKNOWN"
        results["11. Unknown Intent Fallback Test"] = "PASS"
    except Exception as e:
        results["11. Unknown Intent Fallback Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 12 — STANDARD IDENTIFIER DETECTION
    try:
        std1 = bis_search_service.detect_standard_identifier("What does IS 10500 specify?")
        assert std1 == "IS 10500"
        std2 = bis_search_service.detect_standard_identifier("Tell me about IS/ISO 9001")
        assert std2 == "IS/ISO 9001"
        std3 = bis_search_service.detect_standard_identifier("Requirements of ISO 9001")
        assert std3 == "ISO 9001"
        results["12. Standard Identifier Detection Test"] = "PASS"
    except Exception as e:
        results["12. Standard Identifier Detection Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 13 — STANDARD IDENTIFIER QUERY PRESERVATION
    try:
        raw_q = "Details for IS 10500:2012"
        extracted = bis_search_service.detect_standard_identifier(raw_q)
        assert extracted == "IS 10500:2012"
        results["13. Standard Identifier Query Preservation Test"] = "PASS"
    except Exception as e:
        results["13. Standard Identifier Query Preservation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 14 — SEMANTIC RETRIEVAL INTEGRATION
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Mock BIS answer."):
                res = bis_search_service.search_bis("How do I get BIS certification?")
                assert "query" in res
                assert "intent" in res
                assert "results" in res
                assert "answer" in res
                assert "sources" in res
        results["14. Semantic Retrieval Integration Test"] = "PASS"
    except Exception as e:
        results["14. Semantic Retrieval Integration Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 15 — SEARCH RESULT ORDERING
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Answer."):
                res = bis_search_service.search_bis("BIS certification", top_k=5)
                scores = [r["similarity_score"] for r in res["results"]]
                # Check non-increasing similarity order
                assert scores == sorted(scores, reverse=True)
        results["15. Search Result Ordering Test"] = "PASS"
    except Exception as e:
        results["15. Search Result Ordering Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 16 — SIMILARITY SCORE PRESERVATION
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Answer."):
                res = bis_search_service.search_bis("BIS certification")
                for r in res["results"]:
                    assert 0.0 <= r["similarity_score"] <= 1.0
        results["16. Similarity Score Preservation Test"] = "PASS"
    except Exception as e:
        results["16. Similarity Score Preservation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 17 — SEARCH RESULT METADATA SCHEMA
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Answer."):
                res = bis_search_service.search_bis("BIS certification")
                if res["results"]:
                    r0 = res["results"][0]
                    assert "document_id" in r0
                    assert "filename" in r0
                    assert "chunk_id" in r0
                    assert "chunk_index" in r0
                    assert "similarity_score" in r0
        results["17. Search Result Metadata Schema Test"] = "PASS"
    except Exception as e:
        results["17. Search Result Metadata Schema Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 18 — NO-RESULT BEHAVIOR
    try:
        mock_empty_ret = MagicMock()
        mock_empty_ret.retrieve.return_value = {"question": "q", "results": [], "total_results": 0}
        empty_search_svc = BISSearchService(ret_service=mock_empty_ret)
        with patch.object(empty_search_svc.rag_service.llm_service, "_api_key", "mock_key"):
            res = empty_search_svc.search_bis("Unmatched random term 999")
            assert res["sources"] == []
            assert "couldn't find enough relevant information" in res["answer"].lower() or "not found" in res["answer"].lower()
        results["18. No-Result Behavior Test"] = "PASS"
    except Exception as e:
        results["18. No-Result Behavior Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 19 — SERVICE SEARCH WITH RAG
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Product certification scheme answer."):
                res = client.post("/bis/search", json={"query": "Product certification process", "service": "product_certification"})
                assert res.status_code == 200
                data = res.json()
                assert data["intent"] == "CERTIFICATION"
                assert data["service_filter"] == "product_certification"
                assert data["answer"] == "Product certification scheme answer."
        results["19. Service Search with RAG Test"] = "PASS"
    except Exception as e:
        results["19. Service Search with RAG Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 20 — STANDARD SEARCH WITH RAG
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="IS 10500 specifies drinking water requirements."):
                res = client.post("/bis/search", json={"query": "What does IS 10500 specify?"})
                assert res.status_code == 200
                data = res.json()
                assert data["intent"] == "STANDARD_SEARCH"
                assert data["detected_standard"] == "IS 10500"
                assert data["answer"] == "IS 10500 specifies drinking water requirements."
        results["20. Standard Search with RAG Test"] = "PASS"
    except Exception as e:
        results["20. Standard Search with RAG Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 21 — SOURCES ATTACHED TO SEARCH RESULTS
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Grounded response."):
                res = client.post("/bis/search", json={"query": "What is BIS certification?"})
                assert res.status_code == 200
                assert isinstance(res.json()["sources"], list)
        results["21. Sources Attached to Search Results Test"] = "PASS"
    except Exception as e:
        results["21. Sources Attached to Search Results Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 22 — SOURCES MATCH RETRIEVED CHUNKS
    try:
        mock_ret = MagicMock()
        mock_ret.retrieve.return_value = {
            "question": "q",
            "results": [{"document_id": "d1", "filename": "match_chunk.pdf", "chunk_id": "c1", "chunk_index": 0, "similarity_score": 0.9, "chunk_text": "Text"}],
            "total_results": 1
        }
        match_search = BISSearchService(ret_service=mock_ret)
        with patch.object(match_search.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(match_search.rag_service.llm_service, "generate_answer", return_value="Ans"):
                res = match_search.search_bis("Query")
                assert len(res["sources"]) == 1
                assert res["sources"][0]["filename"] == "match_chunk.pdf"
        results["22. Sources Match Retrieved Chunks Test"] = "PASS"
    except Exception as e:
        results["22. Sources Match Retrieved Chunks Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 23 — NO FAKE SOURCES
    try:
        mock_ret_empty = MagicMock()
        mock_ret_empty.retrieve.return_value = {"question": "q", "results": [], "total_results": 0}
        no_fake_svc = BISSearchService(ret_service=mock_ret_empty)
        with patch.object(no_fake_svc.rag_service.llm_service, "_api_key", "mock_key"):
            res = no_fake_svc.search_bis("Unmatched question")
            assert res["sources"] == []
        results["23. No Fake Sources Test"] = "PASS"
    except Exception as e:
        results["23. No Fake Sources Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 24 — NO FLOAT EMBEDDINGS EXPOSED
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Ans"):
                res = client.post("/bis/search", json={"query": "BIS certification"})
                body_text = res.text
                assert "embedding" not in body_text or '"embedding":[' not in body_text
        results["24. No Vector Embeddings Exposed Test"] = "PASS"
    except Exception as e:
        results["24. No Vector Embeddings Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 25 — NO FILESYSTEM PATHS EXPOSED
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Ans"):
                res = client.post("/bis/search", json={"query": "BIS certification"})
                body_text = res.text
                assert "stored_filename" not in body_text
                assert "filepath" not in body_text
        results["25. No Filesystem Paths Exposed Test"] = "PASS"
    except Exception as e:
        results["25. No Filesystem Paths Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 26 — NO API KEYS EXPOSED
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "secret_p11_key_999"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Safe ans."):
                res = client.post("/bis/search", json={"query": "BIS certification"})
                assert "secret_p11_key_999" not in res.text
        results["26. No API Keys Exposed Test"] = "PASS"
    except Exception as e:
        results["26. No API Keys Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 27 — CONTROLLED SEARCH TEST
    doc_b11_id = f"doc_b11_{uuid.uuid4().hex[:8]}"
    test_doc_ids_to_clean.append(doc_b11_id)
    doc_b11_text = "IS 10500 specifies requirements related to drinking water quality parameters in India."
    doc_b11_chunk = DocumentChunk(
        chunk_id=f"{doc_b11_id}_chunk_0",
        document_id=doc_b11_id,
        filename="bis_is10500_spec.pdf",
        chunk_index=0,
        chunk_text=doc_b11_text,
        character_count=len(doc_b11_text),
        file_type="pdf",
        pages=[1],
        embedding=embedding_service.embed_text(doc_b11_text),
        embedding_dimension=384,
        embedding_model="all-MiniLM-L6-v2"
    )

    try:
        vector_store_service.add_chunks([doc_b11_chunk])
        ctrl_llm = LLMService(api_key="mock_key")
        ctrl_search_svc = BISSearchService(r_service=RAGService(l_service=ctrl_llm))

        with patch.object(ctrl_llm, "generate_answer", return_value="IS 10500 specifies drinking water quality parameters."):
            res_ctrl = ctrl_search_svc.search_bis("What does IS 10500 specify?")
            assert res_ctrl["intent"] == "STANDARD_SEARCH"
            assert res_ctrl["detected_standard"] == "IS 10500"
            assert len(res_ctrl["results"]) >= 1
            top_res = res_ctrl["results"][0]
            assert top_res["filename"] == "bis_is10500_spec.pdf"
            assert top_res["pages"] == [1]
        results["27. Controlled Search Test"] = "PASS"
    except Exception as e:
        results["27. Controlled Search Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 28 — CERTIFICATION TEST
    try:
        with patch.object(bis_search_service.rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(bis_search_service.rag_service.llm_service, "generate_answer", return_value="Submit application and samples."):
                res_cert = bis_search_service.search_bis("How do I get BIS certification?")
                assert res_cert["intent"] == "CERTIFICATION"
                assert res_cert["answer"] == "Submit application and samples."
        results["28. Certification Test"] = "PASS"
    except Exception as e:
        results["28. Certification Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 29 — NO-FABRICATION TEST
    try:
        mock_ret_nofab = MagicMock()
        mock_ret_nofab.retrieve.return_value = {"question": "q", "results": [], "total_results": 0}
        nofab_svc = BISSearchService(ret_service=mock_ret_nofab)
        with patch.object(nofab_svc.rag_service.llm_service, "_api_key", "mock_key"):
            res_nofab = nofab_svc.search_bis("What is the BIS fee for XYZ certification?")
            assert res_nofab["sources"] == []
            assert "couldn't find enough relevant information" in res_nofab["answer"].lower() or "not found" in res_nofab["answer"].lower()
        results["29. No-Fabrication Test"] = "PASS"
    except Exception as e:
        results["29. No-Fabrication Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 30 — POST /ask REGRESSION TEST
    try:
        with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="Ask regression ans."):
                resp = client.post("/ask", json={"question": "What is BIS certification?"})
                assert resp.status_code == 200
                assert "answer" in resp.json()
                assert "sources" in resp.json()
        results["30. POST /ask Regression Test"] = "PASS"
    except Exception as e:
        results["30. POST /ask Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 31 — POST /retrieve REGRESSION TEST
    try:
        resp = client.post("/retrieve", json={"question": "What is BIS certification?", "top_k": 5})
        assert resp.status_code == 200
        assert "results" in resp.json()
        results["31. POST /retrieve Regression Test"] = "PASS"
    except Exception as e:
        results["31. POST /retrieve Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 32 — GET /documents REGRESSION TEST
    try:
        resp = client.get("/documents")
        assert resp.status_code == 200
        assert "documents" in resp.json()
        results["32. GET /documents Regression Test"] = "PASS"
    except Exception as e:
        results["32. GET /documents Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 33 — GET /vector-store/health REGRESSION TEST
    try:
        resp = client.get("/vector-store/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
        results["33. GET /vector-store/health Regression Test"] = "PASS"
    except Exception as e:
        results["33. GET /vector-store/health Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 34 — PHASE 9 REGRESSION TEST SUITE
    try:
        from test_phase9 import run_tests as run_p9_tests
        p9_pass = run_p9_tests()
        assert p9_pass is True, "Phase 9 test suite reported failures."
        results["34. Phase 9 Test Suite Regression Test"] = "PASS"
    except Exception as e:
        results["34. Phase 9 Test Suite Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 35 — PHASE 10 REGRESSION TEST SUITE
    try:
        from test_phase10 import run_phase10_tests as run_p10_tests
        p10_pass = run_p10_tests()
        assert p10_pass is True, "Phase 10 test suite reported failures."
        results["35. Phase 10 Test Suite Regression Test"] = "PASS"
    except Exception as e:
        results["35. Phase 10 Test Suite Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 36 — FRONTEND BUILD REGRESSION TEST
    try:
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
        res_build = subprocess.run(["npm.cmd", "run", "build"], cwd=frontend_dir, capture_output=True, text=True)
        assert res_build.returncode == 0, f"Frontend build failed: {res_build.stderr}"
        results["36. Frontend Build Regression Test"] = "PASS"
    except Exception as e:
        results["36. Frontend Build Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # CLEANUP TEST DATA
    print("\n--- CLEANING UP TEST DATA ---")
    cleaned_count = 0
    for doc_id in test_doc_ids_to_clean:
        del_c = vector_store_service.delete_document_chunks(doc_id)
        cleaned_count += del_c
    print(f"Cleaned up {cleaned_count} test document chunks across {len(test_doc_ids_to_clean)} test document IDs.")

    print("\n==================================================")
    print("      PHASE 11 TEST RESULTS SUMMARY              ")
    print("==================================================")
    all_passed = True
    for test_name, status in results.items():
        print(f"{test_name}: {status}")
        if status.startswith("FAIL"):
            all_passed = False

    print("\nOVERALL PHASE 11 STATUS:", "ALL TESTS PASSED SUCCESSFULLY!" if all_passed else "SOME TESTS FAILED.")
    return all_passed


if __name__ == "__main__":
    success = run_phase11_tests()
    sys.exit(0 if success else 1)
