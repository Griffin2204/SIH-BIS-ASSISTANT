import os
import sys
import json
import uuid
import math
import shutil
import urllib.request
import urllib.parse
import docx

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.vector_store import VectorStoreService, vector_store_service
from services.embedding_service import embedding_service
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

    print("--- STARTING PHASE 7 TEST SUITE ---")

    # TEST 1: Vector Store Initialization
    try:
        health = vector_store_service.get_health()
        assert health["status"] == "healthy"
        assert health["collection_name"] == "bis_documents"
        results["1. Vector Store Initialization Test"] = "PASS"
    except Exception as e:
        results["1. Vector Store Initialization Test"] = f"FAIL: {e}"

    # TEST 2: Single Chunk Insertion Test
    test_doc_id = f"doc_test_{uuid.uuid4().hex[:8]}"
    single_chunk_id = f"{test_doc_id}_chunk_0"
    sample_text = "Bureau of Indian Standards BIS certification ensures safety and reliability."
    sample_emb = embedding_service.embed_text(sample_text)

    test_chunk = DocumentChunk(
        chunk_id=single_chunk_id,
        document_id=test_doc_id,
        filename="test_single.txt",
        chunk_index=0,
        chunk_text=sample_text,
        character_count=len(sample_text),
        file_type="txt",
        pages=1,
        embedding=sample_emb,
        embedding_dimension=384,
        embedding_model="all-MiniLM-L6-v2"
    )

    try:
        added = vector_store_service.add_chunks([test_chunk])
        assert added == 1
        results["2. Single Chunk Insertion Test"] = "PASS"
    except Exception as e:
        results["2. Single Chunk Insertion Test"] = f"FAIL: {e}"

    # TEST 3: Chunk Retrieval Test
    try:
        retrieved = vector_store_service.get_chunk(single_chunk_id)
        assert retrieved is not None
        assert retrieved["chunk_id"] == single_chunk_id
        assert retrieved["document"] == sample_text
        assert retrieved["metadata"]["document_id"] == test_doc_id
        assert retrieved["metadata"]["filename"] == "test_single.txt"
        results["3. Chunk Retrieval Test"] = "PASS"
    except Exception as e:
        results["3. Chunk Retrieval Test"] = f"FAIL: {e}"

    # TEST 4: Duplicate Chunk Insertion Test (Upsert / Stable ID)
    try:
        initial_total = vector_store_service.count_chunks()
        # Re-add exact same chunk
        re_added = vector_store_service.add_chunks([test_chunk])
        after_total = vector_store_service.count_chunks()
        assert re_added == 1
        assert after_total == initial_total # Count must not double
        results["4. Duplicate Chunk Insertion Test"] = "PASS"
    except Exception as e:
        results["4. Duplicate Chunk Insertion Test"] = f"FAIL: {e}"

    # TEST 5: Multiple Chunks Insertion Test
    multi_doc_id = f"doc_multi_{uuid.uuid4().hex[:8]}"
    multi_chunks = []
    for i in range(5):
        txt = f"This is section {i} of BIS standards document covering technical requirements."
        emb = embedding_service.embed_text(txt)
        multi_chunks.append(
            DocumentChunk(
                chunk_id=f"{multi_doc_id}_chunk_{i}",
                document_id=multi_doc_id,
                filename="test_multi.txt",
                chunk_index=i,
                chunk_text=txt,
                character_count=len(txt),
                file_type="txt",
                pages=1,
                embedding=emb,
                embedding_dimension=384,
                embedding_model="all-MiniLM-L6-v2"
            )
        )

    try:
        added_multi = vector_store_service.add_chunks(multi_chunks)
        assert added_multi == 5
        results["5. Multiple Chunks Insertion Test"] = "PASS"
    except Exception as e:
        results["5. Multiple Chunks Insertion Test"] = f"FAIL: {e}"

    # TEST 6: Document-Chunk Association Test
    try:
        # Check retrieval of chunks for multi_doc_id
        chunk_0 = vector_store_service.get_chunk(f"{multi_doc_id}_chunk_0")
        assert chunk_0 is not None
        assert chunk_0["metadata"]["document_id"] == multi_doc_id
        results["6. Document-Chunk Association Test"] = "PASS"
    except Exception as e:
        results["6. Document-Chunk Association Test"] = f"FAIL: {e}"

    # TEST 7: Document Re-indexing Test
    try:
        deleted_count = vector_store_service.delete_document_chunks(multi_doc_id)
        assert deleted_count == 5
        after_del = vector_store_service.get_chunk(f"{multi_doc_id}_chunk_0")
        assert after_del is None
        # Re-add 3 chunks for re-indexing simulation
        re_added_count = vector_store_service.add_chunks(multi_chunks[:3])
        assert re_added_count == 3
        results["7. Document Re-indexing Test"] = "PASS"
    except Exception as e:
        results["7. Document Re-indexing Test"] = f"FAIL: {e}"

    # TEST 8: Persistence Test across Client Re-initialization
    try:
        # Create a fresh VectorStoreService instance pointed to same directory
        fresh_service = VectorStoreService(persist_directory=vector_store_service.persist_directory)
        chunk_fresh = fresh_service.get_chunk(single_chunk_id)
        assert chunk_fresh is not None
        assert chunk_fresh["document"] == sample_text
        results["8. Vector Store Persistence Test"] = "PASS"
    except Exception as e:
        results["8. Vector Store Persistence Test"] = f"FAIL: {e}"

    # TEST 9: PDF Document Pipeline Test via API
    try:
        pdf_bytes = create_minimal_pdf_bytes()
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "bis_standards_test.pdf", pdf_bytes, "application/pdf")
        assert status in (200, 201), f"Status: {status}, Response: {resp}"
        assert resp["vector_store_status"] == "indexed"
        assert resp["chunk_count"] > 0
        pdf_doc_id = resp["document_id"]

        # Verify chunk metadata & indexing status via API endpoint
        s_c, r_c = http_get(f"{BASE_URL}/documents/{pdf_doc_id}/chunks")
        assert s_c == 200, f"Status: {s_c}, Response: {r_c}"
        assert r_c["chunk_count"] > 0
        assert r_c["chunks"][0]["vector_store_status"] == "indexed"
        assert r_c["chunks"][0]["chunk_id"] == f"{pdf_doc_id}_chunk_0"
        results["9. PDF Document Pipeline Test"] = "PASS"
    except Exception as e:
        results["9. PDF Document Pipeline Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 10: DOCX Document Pipeline Test via API
    try:
        docx_bytes = create_docx_bytes("Bureau of Indian Standards DOCX specification document for testing vector store integration.")
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "bis_spec_test.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        assert status in (200, 201), f"Status: {status}, Response: {resp}"
        assert resp["vector_store_status"] == "indexed"
        assert resp["chunk_count"] > 0
        docx_doc_id = resp["document_id"]

        # Verify chunk metadata & indexing status via API endpoint
        s_c, r_c = http_get(f"{BASE_URL}/documents/{docx_doc_id}/chunks")
        assert s_c == 200, f"Status: {s_c}, Response: {r_c}"
        assert r_c["chunk_count"] > 0
        assert r_c["chunks"][0]["vector_store_status"] == "indexed"
        assert r_c["chunks"][0]["chunk_id"] == f"{docx_doc_id}_chunk_0"
        results["10. DOCX Document Pipeline Test"] = "PASS"
    except Exception as e:
        results["10. DOCX Document Pipeline Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 11: TXT Document Pipeline Test via API
    try:
        txt_bytes = "BIS standard IS 10500:2012 specifies requirements for drinking water.".encode("utf-8")
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "bis_water_test.txt", txt_bytes, "text/plain")
        assert status in (200, 201), f"Status: {status}, Response: {resp}"
        assert resp["vector_store_status"] == "indexed"
        assert resp["chunk_count"] > 0
        txt_doc_id = resp["document_id"]

        # Verify chunk metadata & indexing status via API endpoint
        s_c, r_c = http_get(f"{BASE_URL}/documents/{txt_doc_id}/chunks")
        assert s_c == 200, f"Status: {s_c}, Response: {r_c}"
        assert r_c["chunk_count"] > 0
        assert r_c["chunks"][0]["vector_store_status"] == "indexed"
        assert r_c["chunks"][0]["chunk_id"] == f"{txt_doc_id}_chunk_0"
        results["11. TXT Document Pipeline Test"] = "PASS"
    except Exception as e:
        results["11. TXT Document Pipeline Test"] = f"FAIL: {type(e).__name__}: {e}"

    # TEST 12: Invalid/Empty Document Handling Test
    try:
        empty_bytes = b""
        status, resp = post_multipart(f"{BASE_URL}/documents/upload", "empty.txt", empty_bytes, "text/plain")
        assert status == 400
        unsupported_bytes = b"random content"
        status2, resp2 = post_multipart(f"{BASE_URL}/documents/upload", "test.exe", unsupported_bytes, "application/octet-stream")
        assert status2 == 400
        results["12. Invalid/Empty Document Handling Test"] = "PASS"
    except Exception as e:
        results["12. Invalid/Empty Document Handling Test"] = f"FAIL: {e}"

    # TEST 13: Vector Store Failure Handling Test
    try:
        # Pass empty list to add_chunks
        added_empty = vector_store_service.add_chunks([])
        assert added_empty == 0
        # Delete non-existent doc chunks
        del_nonexist = vector_store_service.delete_document_chunks("non_existent_doc_id_9999")
        assert del_nonexist == 0
        results["13. Vector Store Failure Handling Test"] = "PASS"
    except Exception as e:
        results["13. Vector Store Failure Handling Test"] = f"FAIL: {e}"

    # TEST 14: Embedding Model & Normalization Regression Test
    try:
        vec = embedding_service.embed_text("Test normalization for vector DB")
        assert len(vec) == 384
        norm = math.sqrt(sum(x * x for x in vec))
        assert abs(norm - 1.0) < 1e-4
        results["14. Embedding Model Regression Test"] = "PASS"
    except Exception as e:
        results["14. Embedding Model Regression Test"] = f"FAIL: {e}"

    # TEST 15: Existing System & API Regression Test
    try:
        # GET /
        s_root, r_root = http_get(f"{BASE_URL}/")
        assert s_root == 200
        assert "status" in r_root or "message" in r_root

        # GET /docs (returns html, so HTTP 200)
        req_docs = urllib.request.Request(f"{BASE_URL}/docs", method="GET")
        with urllib.request.urlopen(req_docs) as resp_docs:
            assert resp_docs.status == 200

        # GET /documents
        s_docs, r_docs = http_get(f"{BASE_URL}/documents")
        assert s_docs == 200
        assert "documents" in r_docs
        if len(r_docs["documents"]) > 0:
            assert "vector_store_status" in r_docs["documents"][0]

        # GET /vector-store/health
        s_health, r_health = http_get(f"{BASE_URL}/vector-store/health")
        assert s_health == 200
        assert r_health["status"] == "healthy"
        assert r_health["collection_name"] == "bis_documents"

        # POST /ask
        s_ask, r_ask = http_post_json(f"{BASE_URL}/ask", {"question": "What is BIS certification?"})
        assert s_ask == 200
        assert "answer" in r_ask

        results["15. Existing System Regression Test"] = "PASS"
    except Exception as e:
        results["15. Existing System Regression Test"] = f"FAIL: {e}"

    print("\n--- PHASE 7 TEST RESULTS SUMMARY ---")
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
