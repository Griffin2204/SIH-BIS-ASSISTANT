import os
import sys
import json
import uuid
import subprocess
from unittest.mock import patch, MagicMock

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, SourceItem, QuestionResponse
from services.vector_store import VectorStoreService, vector_store_service
from services.embedding_service import EmbeddingService, embedding_service
from services.retrieval_service import RetrievalService, retrieval_service
from services.llm_service import LLMService, llm_service, LLMNotConfiguredError, LLMGenerationError
from services.rag_service import RAGService, rag_service
from services.chunker import DocumentChunk

from fastapi.testclient import TestClient

client = TestClient(app)


def run_phase10_tests():
    results = {}
    test_doc_ids_to_clean = []

    print("\n==================================================")
    print("      STARTING PHASE 10 TEST SUITE               ")
    print("==================================================\n")

    # TEST 1 — SOURCE MODEL CREATION
    try:
        source_data = {
            "document_id": "doc_123",
            "filename": "is_10500_water.pdf",
            "file_type": "pdf",
            "chunk_id": "doc_123_chunk_0",
            "chunk_index": 0,
            "similarity_score": 0.9412,
            "pages": [3],
            "snippet": "Drinking water parameters..."
        }
        item = SourceItem(**source_data)
        assert item.document_id == "doc_123"
        assert item.filename == "is_10500_water.pdf"
        assert item.file_type == "pdf"
        assert item.chunk_index == 0
        assert item.similarity_score == 0.9412
        assert item.pages == [3]
        assert item.snippet == "Drinking water parameters..."
        results["1. Source Model Creation Test"] = "PASS"
    except Exception as e:
        results["1. Source Model Creation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 2 — SOURCE METADATA EXTRACTION FROM RETRIEVED CHUNKS
    try:
        mock_chunks = [
            {
                "document_id": "doc_abc",
                "filename": "bis_standard.pdf",
                "file_type": "pdf",
                "chunk_id": "doc_abc_chunk_2",
                "chunk_index": 2,
                "similarity_score": 0.885,
                "pages": [4, 5],
                "chunk_text": "Clause 4.1 specifies test methods."
            }
        ]
        test_rag = RAGService(l_service=LLMService(api_key="mock_key"))
        formatted = test_rag._format_sources(mock_chunks)
        assert len(formatted) == 1
        src = formatted[0]
        assert src["document_id"] == "doc_abc"
        assert src["filename"] == "bis_standard.pdf"
        assert src["file_type"] == "pdf"
        assert src["chunk_id"] == "doc_abc_chunk_2"
        assert src["chunk_index"] == 2
        assert src["similarity_score"] == 0.885
        assert src["pages"] == [4, 5]
        assert "Clause 4.1" in src["snippet"]
        results["2. Source Metadata Extraction Test"] = "PASS"
    except Exception as e:
        results["2. Source Metadata Extraction Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 3 — SOURCE ORDERING PRESERVATION
    try:
        ordered_chunks = [
            {"document_id": "d1", "filename": "doc1.txt", "chunk_index": 0, "similarity_score": 0.95, "chunk_text": "T1"},
            {"document_id": "d2", "filename": "doc2.txt", "chunk_index": 1, "similarity_score": 0.85, "chunk_text": "T2"},
            {"document_id": "d3", "filename": "doc3.txt", "chunk_index": 2, "similarity_score": 0.75, "chunk_text": "T3"}
        ]
        test_rag = RAGService(l_service=LLMService(api_key="mock_key"))
        sources = test_rag._format_sources(ordered_chunks)
        assert [s["filename"] for s in sources] == ["doc1.txt", "doc2.txt", "doc3.txt"]
        assert [s["similarity_score"] for s in sources] == [0.95, 0.85, 0.75]
        results["3. Source Ordering Preservation Test"] = "PASS"
    except Exception as e:
        results["3. Source Ordering Preservation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 4 — SIMILARITY SCORE PRESERVATION
    try:
        chunk = {"document_id": "d1", "filename": "f.txt", "chunk_index": 0, "similarity_score": 0.912345, "chunk_text": "Text"}
        test_rag = RAGService()
        formatted = test_rag._format_sources([chunk])
        assert formatted[0]["similarity_score"] == 0.9123
        results["4. Similarity Score Preservation Test"] = "PASS"
    except Exception as e:
        results["4. Similarity Score Preservation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 5 — PDF PAGE METADATA PRESERVATION
    try:
        pdf_chunk = {"document_id": "pdf1", "filename": "report.pdf", "file_type": "pdf", "chunk_index": 1, "similarity_score": 0.9, "pages": [7], "chunk_text": "Page 7 content"}
        test_rag = RAGService()
        formatted = test_rag._format_sources([pdf_chunk])
        assert formatted[0]["pages"] == [7]
        results["5. PDF Page Metadata Preservation Test"] = "PASS"
    except Exception as e:
        results["5. PDF Page Metadata Preservation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 6 — MISSING PAGE METADATA HANDLING
    try:
        txt_chunk = {"document_id": "txt1", "filename": "notes.txt", "file_type": "txt", "chunk_index": 0, "similarity_score": 0.9, "pages": None, "chunk_text": "Text notes"}
        test_rag = RAGService()
        formatted = test_rag._format_sources([txt_chunk])
        assert formatted[0]["pages"] is None
        results["6. Missing Page Metadata Handling Test"] = "PASS"
    except Exception as e:
        results["6. Missing Page Metadata Handling Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 7 — MULTIPLE CHUNKS FROM SAME DOCUMENT
    try:
        multi_chunks = [
            {"document_id": "doc_same", "filename": "bis_code.pdf", "chunk_index": 1, "similarity_score": 0.92, "chunk_text": "Chunk 1 text"},
            {"document_id": "doc_same", "filename": "bis_code.pdf", "chunk_index": 2, "similarity_score": 0.88, "chunk_text": "Chunk 2 text"}
        ]
        test_rag = RAGService()
        sources = test_rag._format_sources(multi_chunks)
        assert len(sources) == 2
        assert sources[0]["chunk_index"] == 1
        assert sources[1]["chunk_index"] == 2
        results["7. Multiple Chunks From Same Document Test"] = "PASS"
    except Exception as e:
        results["7. Multiple Chunks From Same Document Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 8 — CONTEXT-SELECTED CHUNKS FILTERING
    try:
        small_rag = RAGService(max_context_chars=100, l_service=LLMService(api_key="mock_key"))
        c1 = {"document_id": "d1", "filename": "c1.txt", "chunk_index": 0, "chunk_text": "A" * 70}
        c2 = {"document_id": "d2", "filename": "c2.txt", "chunk_index": 1, "chunk_text": "B" * 70}
        ctx_str, used = small_rag.construct_context_with_used_chunks([c1, c2])
        assert len(used) == 1
        assert used[0]["filename"] == "c1.txt"
        results["8. Context-Selected Chunks Filtering Test"] = "PASS"
    except Exception as e:
        results["8. Context-Selected Chunks Filtering Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 9 — NO-CONTEXT CASE RETURNS EMPTY SOURCES
    try:
        empty_retriever = MagicMock()
        empty_retriever.retrieve.return_value = {"question": "q", "results": [], "total_results": 0}
        no_ctx_rag = RAGService(ret_service=empty_retriever, l_service=LLMService(api_key="mock_key"))
        resp = no_ctx_rag.answer_question("What is BIS?")
        assert resp["sources"] == []
        assert "couldn't find enough relevant information" in resp["answer"]
        results["9. No-Context Case Test"] = "PASS"
    except Exception as e:
        results["9. No-Context Case Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 10 — LOW-RELEVANCE CUTOFF RETURNS EMPTY SOURCES
    try:
        low_sim_retriever = MagicMock()
        low_sim_retriever.retrieve.return_value = {
            "question": "q",
            "results": [{"document_id": "d", "filename": "f.txt", "similarity_score": 0.01, "chunk_text": "irrelevant"}],
            "total_results": 1
        }
        low_rag = RAGService(ret_service=low_sim_retriever, l_service=LLMService(api_key="mock_key"))
        resp = low_rag.answer_question("What is BIS?")
        assert resp["sources"] == []
        results["10. Low-Relevance Cutoff Test"] = "PASS"
    except Exception as e:
        results["10. Low-Relevance Cutoff Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 11 — RAG ANSWER + SOURCES RETURNED TOGETHER
    try:
        mock_ret = MagicMock()
        mock_ret.retrieve.return_value = {
            "question": "Water standard?",
            "results": [
                {"document_id": "d_w", "filename": "water_std.pdf", "file_type": "pdf", "chunk_id": "c0", "chunk_index": 0, "similarity_score": 0.95, "pages": [2], "chunk_text": "IS 10500 is drinking water standard."}
            ],
            "total_results": 1
        }
        mock_llm = LLMService(api_key="mock_key")
        full_rag = RAGService(ret_service=mock_ret, l_service=mock_llm)
        with patch.object(mock_llm, "generate_answer", return_value="IS 10500 regulates drinking water standard."):
            res = full_rag.answer_question("Water standard?")
            assert res["question"] == "Water standard?"
            assert res["answer"] == "IS 10500 regulates drinking water standard."
            assert len(res["sources"]) == 1
            assert res["sources"][0]["filename"] == "water_std.pdf"
            assert res["sources"][0]["similarity_score"] == 0.95
        results["11. RAG Answer + Sources Combination Test"] = "PASS"
    except Exception as e:
        results["11. RAG Answer + Sources Combination Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 12 — API /ask ENDPOINT SOURCES INTEGRATION
    try:
        with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="BIS answer."):
                response = client.post("/ask", json={"question": "What is BIS certification?"})
                assert response.status_code == 200
                data = response.json()
                assert "question" in data
                assert "answer" in data
                assert "sources" in data
                assert isinstance(data["sources"], list)
        results["12. API /ask Endpoint Sources Integration Test"] = "PASS"
    except Exception as e:
        results["12. API /ask Endpoint Sources Integration Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 13 — API /ask SOURCES MATCH RETRIEVED CHUNKS
    try:
        mock_ret = MagicMock()
        mock_ret.retrieve.return_value = {
            "question": "Test query?",
            "results": [
                {"document_id": "doc_test13", "filename": "matched_doc.pdf", "file_type": "pdf", "chunk_id": "doc_test13_c0", "chunk_index": 0, "similarity_score": 0.93, "pages": [1], "chunk_text": "Matched text chunk."}
            ],
            "total_results": 1
        }
        with patch.object(rag_service, "retrieval_service", mock_ret):
            with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
                with patch.object(rag_service.llm_service, "generate_answer", return_value="Matched answer."):
                    response = client.post("/ask", json={"question": "Test query?"})
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data["sources"]) == 1
                    assert data["sources"][0]["filename"] == "matched_doc.pdf"
                    assert data["sources"][0]["chunk_id"] == "doc_test13_c0"
        results["13. API /ask Sources Match Retrieved Chunks Test"] = "PASS"
    except Exception as e:
        results["13. API /ask Sources Match Retrieved Chunks Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 14 — SINGLE RETRIEVAL PASS VERIFICATION
    try:
        mock_ret = MagicMock()
        mock_ret.retrieve.return_value = {
            "question": "Single pass?",
            "results": [
                {"document_id": "d_sp", "filename": "sp.txt", "chunk_index": 0, "similarity_score": 0.9, "chunk_text": "Single pass text."}
            ],
            "total_results": 1
        }
        with patch.object(rag_service, "retrieval_service", mock_ret):
            with patch.object(rag_service.llm_service, "_api_key", "mock_key"):
                with patch.object(rag_service.llm_service, "generate_answer", return_value="Single pass ans."):
                    client.post("/ask", json={"question": "Single pass?"})
                    assert mock_ret.retrieve.call_count == 1
        results["14. Single Retrieval Pass Verification Test"] = "PASS"
    except Exception as e:
        results["14. Single Retrieval Pass Verification Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 15 — NO VECTOR EMBEDDINGS EXPOSED
    try:
        mock_chunk_with_emb = {
            "document_id": "d1",
            "filename": "f.txt",
            "chunk_index": 0,
            "similarity_score": 0.9,
            "chunk_text": "Text",
            "embedding": [0.123] * 384
        }
        test_rag = RAGService()
        sources = test_rag._format_sources([mock_chunk_with_emb])
        assert "embedding" not in sources[0]
        for src in sources:
            assert "embedding" not in src
        results["15. No Vector Embeddings Exposed Test"] = "PASS"
    except Exception as e:
        results["15. No Vector Embeddings Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 16 — NO FILESYSTEM PATHS EXPOSED
    try:
        mock_chunk_paths = {
            "document_id": "d1",
            "filename": "user_doc.pdf",
            "stored_filename": "uuid123_user_doc.pdf",
            "filepath": "C:\\server\\uploads\\uuid123_user_doc.pdf",
            "chunk_index": 0,
            "similarity_score": 0.9,
            "chunk_text": "Text"
        }
        test_rag = RAGService()
        sources = test_rag._format_sources([mock_chunk_paths])
        assert "stored_filename" not in sources[0]
        assert "filepath" not in sources[0]
        assert "C:\\" not in json.dumps(sources[0])
        results["16. No Filesystem Paths Exposed Test"] = "PASS"
    except Exception as e:
        results["16. No Filesystem Paths Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 17 — NO API KEYS EXPOSED
    try:
        with patch.object(rag_service.llm_service, "_api_key", "secret_key_12345"):
            with patch.object(rag_service.llm_service, "generate_answer", return_value="Safe answer."):
                response = client.post("/ask", json={"question": "What is BIS?"})
                body_str = response.text
                assert "secret_key_12345" not in body_str
        results["17. No API Keys Exposed Test"] = "PASS"
    except Exception as e:
        results["17. No API Keys Exposed Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 18 — CONTROLLED SOURCE INTEGRITY TEST
    doc_a_id = f"doc_a_{uuid.uuid4().hex[:8]}"
    doc_b_id = f"doc_b_{uuid.uuid4().hex[:8]}"
    test_doc_ids_to_clean.extend([doc_a_id, doc_b_id])

    chunk_a_text = "ABC certification requirements mandate factory testing and quality control procedures."
    chunk_b_text = "XYZ testing requirements involve independent electrical laboratory verification."

    chunk_a = DocumentChunk(
        chunk_id=f"{doc_a_id}_chunk_0",
        document_id=doc_a_id,
        filename="abc_certification_manual.pdf",
        chunk_index=0,
        chunk_text=chunk_a_text,
        character_count=len(chunk_a_text),
        file_type="pdf",
        pages=[2],
        embedding=embedding_service.embed_text(chunk_a_text),
        embedding_dimension=384,
        embedding_model="all-MiniLM-L6-v2"
    )
    chunk_b = DocumentChunk(
        chunk_id=f"{doc_b_id}_chunk_0",
        document_id=doc_b_id,
        filename="xyz_testing_spec.docx",
        chunk_index=0,
        chunk_text=chunk_b_text,
        character_count=len(chunk_b_text),
        file_type="docx",
        embedding=embedding_service.embed_text(chunk_b_text),
        embedding_dimension=384,
        embedding_model="all-MiniLM-L6-v2"
    )

    try:
        vector_store_service.add_chunks([chunk_a, chunk_b])

        controlled_llm = LLMService(api_key="mock_key")
        controlled_rag = RAGService(l_service=controlled_llm)

        with patch.object(controlled_llm, "generate_answer", return_value="ABC certification mandates quality control procedures."):
            rag_output = controlled_rag.answer_question("What does ABC certification require?")
            assert rag_output["answer"] == "ABC certification mandates quality control procedures."
            assert len(rag_output["sources"]) >= 1
            top_source = rag_output["sources"][0]
            assert top_source["chunk_id"] == chunk_a.chunk_id
            assert top_source["filename"] == "abc_certification_manual.pdf"
            assert top_source["pages"] == [2]
            assert top_source["similarity_score"] > 0.5
        results["18. Controlled Source Integrity Test"] = "PASS"
    except Exception as e:
        results["18. Controlled Source Integrity Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 19 — NO FAKE CITATIONS TEST
    try:
        mock_empty_ret = MagicMock()
        mock_empty_ret.retrieve.return_value = {"question": "q", "results": [], "total_results": 0}
        no_fake_rag = RAGService(ret_service=mock_empty_ret, l_service=LLMService(api_key="mock_key"))
        res = no_fake_rag.answer_question("Nonexistent question?")
        assert res["sources"] == []
        results["19. No Fake Citations Test"] = "PASS"
    except Exception as e:
        results["19. No Fake Citations Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 20 — EXISTING /documents ENDPOINT REGRESSION
    try:
        resp = client.get("/documents")
        assert resp.status_code == 200
        assert "documents" in resp.json()
        results["20. Existing /documents Endpoint Regression Test"] = "PASS"
    except Exception as e:
        results["20. Existing /documents Endpoint Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 21 — EXISTING /retrieve ENDPOINT REGRESSION
    try:
        resp = client.post("/retrieve", json={"question": "What is BIS certification?", "top_k": 5})
        assert resp.status_code == 200
        assert "results" in resp.json()
        results["21. Existing /retrieve Endpoint Regression Test"] = "PASS"
    except Exception as e:
        results["21. Existing /retrieve Endpoint Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 22 — EXISTING VECTOR STORE HEALTH REGRESSION
    try:
        resp = client.get("/vector-store/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
        results["22. Existing Vector Store Regression Test"] = "PASS"
    except Exception as e:
        results["22. Existing Vector Store Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 23 — PHASE 9 TEST SUITE REGRESSION
    try:
        from test_phase9 import run_tests as run_p9_tests
        p9_success = run_p9_tests()
        assert p9_success is True, "Phase 9 test suite execution reported failures."
        results["23. Phase 9 Test Suite Regression Test"] = "PASS"
    except Exception as e:
        results["23. Phase 9 Test Suite Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 24 — FRONTEND BUILD REGRESSION
    try:
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
        res_build = subprocess.run(["npm.cmd", "run", "build"], cwd=frontend_dir, capture_output=True, text=True)
        assert res_build.returncode == 0, f"Frontend build failed: {res_build.stderr}"
        results["24. Frontend Build Regression Test"] = "PASS"
    except Exception as e:
        results["24. Frontend Build Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # CLEANUP TEST DATA
    print("\n--- CLEANING UP TEST DATA ---")
    cleaned_count = 0
    for doc_id in test_doc_ids_to_clean:
        del_c = vector_store_service.delete_document_chunks(doc_id)
        cleaned_count += del_c
    print(f"Cleaned up {cleaned_count} test document chunks across {len(test_doc_ids_to_clean)} test document IDs.")

    print("\n==================================================")
    print("      PHASE 10 TEST RESULTS SUMMARY              ")
    print("==================================================")
    all_passed = True
    for test_name, status in results.items():
        print(f"{test_name}: {status}")
        if status.startswith("FAIL"):
            all_passed = False

    print("\nOVERALL PHASE 10 STATUS:", "ALL TESTS PASSED SUCCESSFULLY!" if all_passed else "SOME TESTS FAILED.")
    return all_passed


if __name__ == "__main__":
    success = run_phase10_tests()
    sys.exit(0 if success else 1)
