import os
import sys
import json
import uuid
import math
import subprocess
import urllib.request
import urllib.parse
import docx

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.vector_store import VectorStoreService, vector_store_service
from services.embedding_service import EmbeddingService, embedding_service
from services.retrieval_service import RetrievalService, retrieval_service
from services.chunker import DocumentChunk
from services.text_cleaner import clean_text

BASE_URL = "http://127.0.0.1:8000"

def create_minimal_pdf_bytes():
    return (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 73 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Bureau of Indian Standards BIS Certification PDF test content.) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000302 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n425\n%%EOF\n"
    )

def create_docx_bytes(text: str) -> bytes:
    doc = docx.Document()
    doc.add_paragraph(text)
    temp_path = f"temp_{uuid.uuid4().hex}.docx"
    doc.save(temp_path)
    with open(temp_path, "rb") as f:
        data = f.read()
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return data

def post_multipart(url: str, filename: str, content: bytes, content_type: str):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
    body.extend(content)
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(url, data=bytes(body), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            resp_body = resp.read().decode("utf-8")
            return status, json.loads(resp_body)
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(resp_body)
        except Exception:
            parsed = {"detail": resp_body}
        return e.code, parsed

def http_get(url: str):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            resp_body = resp.read().decode("utf-8")
            return status, json.loads(resp_body)
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(resp_body)
        except Exception:
            parsed = {"detail": resp_body}
        return e.code, parsed

def http_post_json(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            resp_body = resp.read().decode("utf-8")
            return status, json.loads(resp_body)
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(resp_body)
        except Exception:
            parsed = {"detail": resp_body}
        return e.code, parsed

def run_tests():
    results = {}
    test_doc_ids_to_clean = []

    print("--- STARTING PHASE 8 TEST SUITE ---")

    # TEST 1 — RETRIEVAL SERVICE INITIALIZATION
    try:
        retriever = RetrievalService.get_instance()
        assert retriever.embedding_service is not None
        assert retriever.vector_store_service is not None
        health = retriever.vector_store_service.get_health()
        assert health["status"] == "healthy"
        assert health["collection_name"] == "bis_documents"
        results["1. Retrieval Service Initialization Test"] = "PASS"
    except Exception as e:
        results["1. Retrieval Service Initialization Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 2 — QUERY EMBEDDING
    try:
        emb_service = EmbeddingService.get_instance()
        q_text = "What is BIS certification?"
        q_vec = emb_service.embed_text(q_text)
        assert len(q_vec) == 384
        norm = math.sqrt(sum(x * x for x in q_vec))
        assert abs(norm - 1.0) < 1e-4
        assert emb_service.model_name == "all-MiniLM-L6-v2"
        results["2. Query Embedding Test"] = "PASS"
    except Exception as e:
        results["2. Query Embedding Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 3 — SINGLE DOCUMENT RETRIEVAL
    doc3_id = f"doc_p8_single_{uuid.uuid4().hex[:8]}"
    test_doc_ids_to_clean.append(doc3_id)
    doc3_text = "Bureau of Indian Standards BIS certification ensures product quality and safety compliance across India."
    doc3_vec = embedding_service.embed_text(doc3_text)
    doc3_chunk = DocumentChunk(
        chunk_id=f"{doc3_id}_chunk_0",
        document_id=doc3_id,
        filename="bis_single.txt",
        chunk_index=0,
        chunk_text=doc3_text,
        character_count=len(doc3_text),
        file_type="txt",
        pages=1,
        embedding=doc3_vec,
        embedding_dimension=384,
        embedding_model="all-MiniLM-L6-v2"
    )
    try:
        vector_store_service.add_chunks([doc3_chunk])
        ret_res = retrieval_service.retrieve("What is BIS certification?", top_k=15)
        assert ret_res["total_results"] > 0
        found_ids = [r["document_id"] for r in ret_res["results"]]
        assert doc3_id in found_ids, f"doc3_id {doc3_id} not found in retrieved results"
        results["3. Single Document Retrieval Test"] = "PASS"
    except Exception as e:
        results["3. Single Document Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 4 — SEMANTIC RELEVANCE
    doc_bis_id = f"doc_p8_bis_{uuid.uuid4().hex[:8]}"
    doc_net_id = f"doc_p8_net_{uuid.uuid4().hex[:8]}"
    test_doc_ids_to_clean.extend([doc_bis_id, doc_net_id])

    text_bis = "The Bureau of Indian Standards BIS certification scheme guarantees product safety and compliance with Indian Standards."
    text_net = "Computer networking routers, switches, TCP IP protocols, and ethernet packet framing routing."

    chunk_bis = DocumentChunk(
        chunk_id=f"{doc_bis_id}_chunk_0",
        document_id=doc_bis_id,
        filename="bis_guide.txt",
        chunk_index=0,
        chunk_text=text_bis,
        character_count=len(text_bis),
        file_type="txt",
        embedding=embedding_service.embed_text(text_bis),
        embedding_dimension=384,
        embedding_model="all-MiniLM-L6-v2"
    )

    chunk_net = DocumentChunk(
        chunk_id=f"{doc_net_id}_chunk_0",
        document_id=doc_net_id,
        filename="networking.txt",
        chunk_index=0,
        chunk_text=text_net,
        character_count=len(text_net),
        file_type="txt",
        embedding=embedding_service.embed_text(text_net),
        embedding_dimension=384,
        embedding_model="all-MiniLM-L6-v2"
    )

    try:
        vector_store_service.add_chunks([chunk_bis, chunk_net])

        # Query networking -> Net doc distance must be smaller than BIS doc distance
        res_net = retrieval_service.retrieve("What is a network router?", top_k=15)
        dist_net_for_net = next((r["distance"] for r in res_net["results"] if r["document_id"] == doc_net_id), 999.0)
        dist_bis_for_net = next((r["distance"] for r in res_net["results"] if r["document_id"] == doc_bis_id), 999.0)
        assert dist_net_for_net < dist_bis_for_net, f"Networking distance ({dist_net_for_net}) should be less than BIS distance ({dist_bis_for_net}) for networking query"

        # Query BIS -> BIS doc distance must be smaller than Net doc distance
        res_bis = retrieval_service.retrieve("What is BIS product certification?", top_k=15)
        dist_bis_for_bis = next((r["distance"] for r in res_bis["results"] if r["document_id"] == doc_bis_id), 999.0)
        dist_net_for_bis = next((r["distance"] for r in res_bis["results"] if r["document_id"] == doc_net_id), 999.0)
        assert dist_bis_for_bis < dist_net_for_bis, f"BIS distance ({dist_bis_for_bis}) should be less than Networking distance ({dist_net_for_bis}) for BIS query"

        results["4. Semantic Relevance Test"] = "PASS"
    except Exception as e:
        results["4. Semantic Relevance Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 5 — TOP-K
    try:
        k1 = retrieval_service.retrieve("BIS standard", top_k=1)
        assert len(k1["results"]) == 1

        k3 = retrieval_service.retrieve("BIS standard", top_k=3)
        assert len(k3["results"]) <= 3

        k5 = retrieval_service.retrieve("BIS standard", top_k=5)
        assert len(k5["results"]) <= 5
        results["5. Top-K Filtering Test"] = "PASS"
    except Exception as e:
        results["5. Top-K Filtering Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 6 — RESULT ORDER
    try:
        r_order = retrieval_service.retrieve("BIS certification guidelines", top_k=5)
        dists = [r["distance"] for r in r_order["results"]]
        # Distances must be sorted non-decreasing (most relevant / smallest distance first)
        for i in range(len(dists) - 1):
            assert dists[i] <= dists[i + 1]
        results["6. Result Ordering Test"] = "PASS"
    except Exception as e:
        results["6. Result Ordering Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 7 — METADATA
    try:
        r_meta = retrieval_service.retrieve("BIS certification", top_k=1)
        assert len(r_meta["results"]) > 0
        item = r_meta["results"][0]
        required_keys = [
            "chunk_id", "document_id", "filename", "file_type",
            "chunk_index", "character_count", "embedding_model", "embedding_dimension"
        ]
        for key in required_keys:
            assert key in item, f"Missing key '{key}' in retrieved metadata"
        results["7. Metadata Preservation Test"] = "PASS"
    except Exception as e:
        results["7. Metadata Preservation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 8 — DISTANCE
    try:
        r_dist = retrieval_service.retrieve("BIS certification", top_k=1)
        assert len(r_dist["results"]) > 0
        dist_val = r_dist["results"][0]["distance"]
        assert isinstance(dist_val, float)
        assert dist_val >= 0.0
        results["8. Distance Verification Test"] = "PASS"
    except Exception as e:
        results["8. Distance Verification Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 9 — SIMILARITY SCORE
    try:
        r_sim = retrieval_service.retrieve("BIS certification", top_k=1)
        assert len(r_sim["results"]) > 0
        item = r_sim["results"][0]
        assert "similarity_score" in item
        sim_val = item["similarity_score"]
        dist_val = item["distance"]
        # Formula: similarity_score = round(1.0 - distance, 4)
        expected_sim = round(1.0 - dist_val, 4)
        assert abs(sim_val - expected_sim) < 1e-4
        results["9. Similarity Score Formula Test"] = "PASS"
    except Exception as e:
        results["9. Similarity Score Formula Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 10 — EMPTY DATABASE
    try:
        empty_vs = VectorStoreService(persist_directory=vector_store_service.persist_directory, collection_name=f"temp_empty_{uuid.uuid4().hex[:6]}")
        empty_retriever = RetrievalService(vs_service=empty_vs)
        r_empty = empty_retriever.retrieve("What is BIS?", top_k=5)
        assert r_empty["total_results"] == 0
        assert r_empty["results"] == []
        results["10. Empty Database Handling Test"] = "PASS"
    except Exception as e:
        results["10. Empty Database Handling Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 11 — EMPTY QUESTION
    try:
        try:
            retrieval_service.retrieve("", top_k=5)
            assert False, "Should have raised ValueError for empty string"
        except ValueError:
            pass

        try:
            retrieval_service.retrieve("   ", top_k=5)
            assert False, "Should have raised ValueError for whitespace string"
        except ValueError:
            pass

        results["11. Empty Question Validation Test"] = "PASS"
    except Exception as e:
        results["11. Empty Question Validation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 12 — INVALID TOP-K
    try:
        try:
            retrieval_service.retrieve("Valid question", top_k=0)
            assert False, "Should have raised ValueError for top_k=0"
        except ValueError:
            pass

        try:
            retrieval_service.retrieve("Valid question", top_k=-1)
            assert False, "Should have raised ValueError for top_k=-1"
        except ValueError:
            pass

        try:
            retrieval_service.retrieve("Valid question", top_k=100)
            assert False, "Should have raised ValueError for top_k > 20"
        except ValueError:
            pass

        results["12. Invalid Top-K Validation Test"] = "PASS"
    except Exception as e:
        results["12. Invalid Top-K Validation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 13 — MULTILINGUAL / UNICODE QUERY
    try:
        u_query = "भारतीय मानक ब्यूरो BIS प्रमाणन की क्या प्रक्रिया है?"
        r_unicode = retrieval_service.retrieve(u_query, top_k=3)
        assert "results" in r_unicode
        results["13. Multilingual/Unicode Query Test"] = "PASS"
    except Exception as e:
        results["13. Multilingual/Unicode Query Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 14 — API ENDPOINT (POST /retrieve)
    try:
        status, resp = http_post_json(f"{BASE_URL}/retrieve", {"question": "What is BIS certification?", "top_k": 5})
        assert status == 200, f"Status: {status}, Response: {resp}"
        assert resp["question"] == "What is BIS certification?"
        assert "results" in resp
        assert "total_results" in resp
        if len(resp["results"]) > 0:
            assert "embedding" not in resp["results"][0]
            assert "distance" in resp["results"][0]
            assert "similarity_score" in resp["results"][0]
        results["14. API Endpoint /retrieve Test"] = "PASS"
    except Exception as e:
        results["14. API Endpoint /retrieve Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 15 — API VALIDATION
    try:
        s_emp, r_emp = http_post_json(f"{BASE_URL}/retrieve", {"question": "", "top_k": 5})
        assert s_emp in (400, 422), f"Expected 400 or 422, got {s_emp}"

        s_k, r_k = http_post_json(f"{BASE_URL}/retrieve", {"question": "Valid", "top_k": -5})
        assert s_k in (400, 422), f"Expected 400 or 422, got {s_k}"

        results["15. API Input Validation Test"] = "PASS"
    except Exception as e:
        results["15. API Input Validation Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 16 — VECTOR STORE PERSISTENCE
    try:
        fresh_vs = VectorStoreService(persist_directory=vector_store_service.persist_directory)
        fresh_retriever = RetrievalService(vs_service=fresh_vs)
        r_pers = fresh_retriever.retrieve("What is BIS certification?", top_k=5)
        assert r_pers["total_results"] > 0
        results["16. Vector Store Persistence Test"] = "PASS"
    except Exception as e:
        results["16. Vector Store Persistence Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 17 — EXISTING PIPELINE REGRESSION
    try:
        pipe_txt = "BIS standard IS 10500:2012 defines drinking water parameters in India."
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "bis_pipeline_reg.txt", pipe_txt.encode("utf-8"), "text/plain")
        assert status in (200, 201)
        doc_id = resp["document_id"]
        test_doc_ids_to_clean.append(doc_id)

        # Retrieve chunk from uploaded file via API endpoint
        s_p, r_pipe = http_post_json(f"{BASE_URL}/retrieve", {"question": "What standard defines drinking water parameters?", "top_k": 15})
        assert s_p == 200, f"Status: {s_p}, Response: {r_pipe}"
        pipe_doc_ids = [r["document_id"] for r in r_pipe["results"]]
        assert doc_id in pipe_doc_ids, f"Uploaded pipeline doc_id {doc_id} not found in retrieved results"
        results["17. Existing Ingestion Pipeline Regression Test"] = "PASS"
    except Exception as e:
        results["17. Existing Ingestion Pipeline Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 18 — PDF RETRIEVAL
    try:
        pdf_bytes = create_minimal_pdf_bytes()
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "pdf_retrieve_test.pdf", pdf_bytes, "application/pdf")
        assert status in (200, 201)
        pdf_doc_id = resp["document_id"]
        test_doc_ids_to_clean.append(pdf_doc_id)

        s_pdf, r_pdf = http_post_json(f"{BASE_URL}/retrieve", {"question": "Bureau of Indian Standards PDF content", "top_k": 15})
        assert s_pdf == 200, f"Status: {s_pdf}, Response: {r_pdf}"
        pdf_found_ids = [r["document_id"] for r in r_pdf["results"]]
        assert pdf_doc_id in pdf_found_ids, f"PDF doc_id {pdf_doc_id} not found in retrieved results"
        results["18. PDF Document Retrieval Test"] = "PASS"
    except Exception as e:
        results["18. PDF Document Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 19 — DOCX RETRIEVAL
    try:
        docx_bytes = create_docx_bytes("DOCX semantic retrieval test for Bureau of Indian Standards specification documents.")
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "docx_retrieve_test.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        assert status in (200, 201)
        docx_doc_id = resp["document_id"]
        test_doc_ids_to_clean.append(docx_doc_id)

        s_docx, r_docx = http_post_json(f"{BASE_URL}/retrieve", {"question": "DOCX specification documents", "top_k": 15})
        assert s_docx == 200, f"Status: {s_docx}, Response: {r_docx}"
        docx_found_ids = [r["document_id"] for r in r_docx["results"]]
        assert docx_doc_id in docx_found_ids, f"DOCX doc_id {docx_doc_id} not found in retrieved results"
        results["19. DOCX Document Retrieval Test"] = "PASS"
    except Exception as e:
        results["19. DOCX Document Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 20 — TXT RETRIEVAL
    try:
        txt_bytes = "TXT semantic retrieval test for BIS standard conformity assessment.".encode("utf-8")
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "txt_retrieve_test.txt", txt_bytes, "text/plain")
        assert status in (200, 201)
        txt_doc_id = resp["document_id"]
        test_doc_ids_to_clean.append(txt_doc_id)

        s_txt, r_txt = http_post_json(f"{BASE_URL}/retrieve", {"question": "conformity assessment", "top_k": 15})
        assert s_txt == 200, f"Status: {s_txt}, Response: {r_txt}"
        txt_found_ids = [r["document_id"] for r in r_txt["results"]]
        assert txt_doc_id in txt_found_ids, f"TXT doc_id {txt_doc_id} not found in retrieved results"
        results["20. TXT Document Retrieval Test"] = "PASS"
    except Exception as e:
        results["20. TXT Document Retrieval Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 21 — EXISTING ENDPOINTS REGRESSION
    try:
        # GET /
        s_root, _ = http_get(f"{BASE_URL}/")
        assert s_root == 200

        # GET /docs
        req_docs = urllib.request.Request(f"{BASE_URL}/docs", method="GET")
        with urllib.request.urlopen(req_docs) as resp_docs:
            assert resp_docs.status == 200

        # GET /documents
        s_docs, r_docs = http_get(f"{BASE_URL}/documents")
        assert s_docs == 200

        # POST /ask
        s_ask, r_ask = http_post_json(f"{BASE_URL}/ask", {"question": "What is BIS certification?"})
        assert s_ask == 200
        assert r_ask["answer"] == "Temporary response"

        results["21. Existing Endpoints Regression Test"] = "PASS"
    except Exception as e:
        results["21. Existing Endpoints Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 22 — FRONTEND BUILD REGRESSION
    try:
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
        res_build = subprocess.run(["npm.cmd", "run", "build"], cwd=frontend_dir, capture_output=True, text=True)
        assert res_build.returncode == 0, f"Frontend build failed: {res_build.stderr}"
        results["22. Frontend Build Regression Test"] = "PASS"
    except Exception as e:
        results["22. Frontend Build Regression Test"] = f"FAIL: {type(e).__name__}: {e}"

    # CLEANUP TEST DATA
    print("\n--- CLEANING UP TEST DATA ---")
    cleaned_count = 0
    for doc_id in test_doc_ids_to_clean:
        del_c = vector_store_service.delete_document_chunks(doc_id)
        cleaned_count += del_c
    print(f"Cleaned up {cleaned_count} test document chunks across {len(test_doc_ids_to_clean)} test document IDs.")

    print("\n--- PHASE 8 TEST RESULTS SUMMARY ---")
    all_passed = True
    for test_name, status in results.items():
        print(f"{test_name}: {status}")
        if not status.startswith("PASS"):
            all_passed = False

    print("\nOVERALL STATUS:", "ALL TESTS PASSED SUCCESSFULLY!" if all_passed else "SOME TESTS FAILED.")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
