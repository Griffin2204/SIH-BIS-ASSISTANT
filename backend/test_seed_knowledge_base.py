import os
import sys
import shutil
import tempfile
from typing import Dict, Any

# Ensure backend root is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from seed_knowledge_base import (
    get_deterministic_doc_id,
    scan_knowledge_base_dir,
    seed_knowledge_base,
    DEFAULT_KB_DIR
)
from services.vector_store import VectorStoreService, get_default_collection_name
from services.embedding_service import EmbeddingService
from services.retrieval_service import RetrievalService
from services.rag_service import RAGService


def run_tests():
    print("\n" + "=" * 55)
    print("     RUNNING KNOWLEDGE BASE SEEDING TEST SUITE")
    print("=====================================================\n")

    results: Dict[str, str] = {}
    vs = VectorStoreService.get_instance()
    collection = vs._init_db()

    # TEST 1: Deterministic Document ID Generation
    try:
        id1 = get_deterministic_doc_id("BIS_Information_and_Knowledge_Base.pdf")
        id2 = get_deterministic_doc_id("BIS_Information_and_Knowledge_Base.pdf")
        id3 = get_deterministic_doc_id("another_doc.pdf")
        assert id1 == id2, "Document IDs for the same filename must match exactly."
        assert id1 != id3, "Document IDs for different filenames must differ."
        assert len(id1) == 36, f"Expected 36-char UUID format, got length {len(id1)}"
        results["1. Deterministic Document ID Generation"] = "PASS"
    except Exception as e:
        results["1. Deterministic Document ID Generation"] = f"FAIL: {e}"

    # TEST 2: Knowledge Base Directory Scanning
    temp_dir = tempfile.mkdtemp(prefix="kb_scan_test_")
    try:
        # Create test files: valid, invalid, and hidden
        with open(os.path.join(temp_dir, "doc1.pdf"), "w") as f: f.write("dummy")
        with open(os.path.join(temp_dir, "doc2.docx"), "w") as f: f.write("dummy")
        with open(os.path.join(temp_dir, "doc3.txt"), "w") as f: f.write("dummy")
        with open(os.path.join(temp_dir, "ignored.exe"), "w") as f: f.write("dummy")
        with open(os.path.join(temp_dir, ".hidden.pdf"), "w") as f: f.write("dummy")

        scanned = scan_knowledge_base_dir(temp_dir)
        basenames = [os.path.basename(p) for p in scanned]
        assert "doc1.pdf" in basenames
        assert "doc2.docx" in basenames
        assert "doc3.txt" in basenames
        assert "ignored.exe" not in basenames
        assert ".hidden.pdf" not in basenames
        assert len(scanned) == 3
        results["2. Directory Scanner File Filtering"] = "PASS"
    except Exception as e:
        results["2. Directory Scanner File Filtering"] = f"FAIL: {e}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # TEST 3: Scan Real Knowledge Base Directory
    try:
        real_files = scan_knowledge_base_dir(DEFAULT_KB_DIR)
        assert len(real_files) >= 1, "Expected at least 1 file in backend/knowledge_base/"
        real_names = [os.path.basename(p) for p in real_files]
        assert "BIS_Information_and_Knowledge_Base.pdf" in real_names
        results["3. Real Knowledge Base PDF Discovery"] = "PASS"
    except Exception as e:
        results["3. Real Knowledge Base PDF Discovery"] = f"FAIL: {e}"

    # TEST 4: Dry-Run Mode
    temp_kb_dir = tempfile.mkdtemp(prefix="kb_dryrun_test_")
    try:
        with open(os.path.join(temp_kb_dir, "test_dryrun.txt"), "w") as f:
            f.write("Sample test content for dry run testing.")
        dry_res = seed_knowledge_base(kb_dir=temp_kb_dir, dry_run=True)
        assert dry_res["total_files_found"] == 1
        assert dry_res["newly_indexed"] == 1
        assert dry_res["failed"] == 0
        assert dry_res["files"][0]["status"] == "dry_run"
        results["4. Dry-Run Mode Execution"] = "PASS"
    except Exception as e:
        results["4. Dry-Run Mode Execution"] = f"FAIL: {e}"
    finally:
        shutil.rmtree(temp_kb_dir, ignore_errors=True)

    # TEST 5: Actual Seeding of Real Knowledge Base PDF
    seeded_doc_id = get_deterministic_doc_id("BIS_Information_and_Knowledge_Base.pdf")
    initial_chunks_count = 0
    try:
        # Force index to ensure clean baseline for testing
        seed_res = seed_knowledge_base(kb_dir=DEFAULT_KB_DIR, force=True)
        assert seed_res["failed"] == 0, f"Seeding failed: {seed_res}"
        assert seed_res["newly_indexed"] >= 1

        # Check ChromaDB for stored chunks
        existing = collection.get(where={"document_id": seeded_doc_id}, include=["metadatas", "documents"])
        initial_chunks_count = len(existing.get("ids", []))
        assert initial_chunks_count > 0, f"Expected chunks in ChromaDB for {seeded_doc_id}, found 0"

        # Verify metadata structure
        meta = existing["metadatas"][0]
        assert meta["document_id"] == seeded_doc_id
        assert meta["filename"] == "BIS_Information_and_Knowledge_Base.pdf"
        assert meta["file_type"] == "pdf"
        assert meta["pages"] == 6, f"Expected 6 pages, got {meta.get('pages')}"
        assert "chunk_index" in meta
        assert "embedding_model" in meta
        assert "embedding_dimension" in meta

        results["5. Real Knowledge Base PDF Seeding & Metadata"] = "PASS"
    except Exception as e:
        results["5. Real Knowledge Base PDF Seeding & Metadata"] = f"FAIL: {e}"

    # TEST 6: Idempotency (Running second time without --force)
    try:
        second_res = seed_knowledge_base(kb_dir=DEFAULT_KB_DIR, force=False)
        assert second_res["failed"] == 0
        assert second_res["already_indexed"] >= 1, f"Expected already_indexed >= 1, got {second_res['already_indexed']}"
        assert second_res["newly_indexed"] == 0, f"Expected newly_indexed == 0 on second run, got {second_res['newly_indexed']}"

        # Verify chunk count in ChromaDB is unchanged
        existing_after = collection.get(where={"document_id": seeded_doc_id})
        after_count = len(existing_after.get("ids", []))
        assert after_count == initial_chunks_count, (
            f"Chunk count changed on second run! Was {initial_chunks_count}, now {after_count}"
        )
        results["6. Idempotency Check (Zero Duplication on Re-run)"] = "PASS"
    except Exception as e:
        results["6. Idempotency Check (Zero Duplication on Re-run)"] = f"FAIL: {e}"

    # TEST 7: Idempotency with --force (Replaces cleanly, no duplicates)
    try:
        force_res = seed_knowledge_base(kb_dir=DEFAULT_KB_DIR, force=True)
        assert force_res["failed"] == 0
        assert force_res["newly_indexed"] >= 1

        existing_force = collection.get(where={"document_id": seeded_doc_id})
        force_count = len(existing_force.get("ids", []))
        assert force_count == initial_chunks_count, (
            f"Force re-index created duplicate chunks! Expected {initial_chunks_count}, found {force_count}"
        )
        results["7. Force Re-index Idempotency (Clean Replacement)"] = "PASS"
    except Exception as e:
        results["7. Force Re-index Idempotency (Clean Replacement)"] = f"FAIL: {e}"

    # TEST 8: Semantic Retrieval of Seeded Knowledge
    try:
        retriever = RetrievalService.get_instance()
        test_query = "Renewal, Retesting and Change in Scope of BIS licences"
        retrieval_res = retriever.retrieve(test_query, top_k=5)
        assert len(retrieval_res["results"]) > 0, "No chunks retrieved for query"

        top_chunk = retrieval_res["results"][0]
        assert top_chunk["document_id"] == seeded_doc_id, f"Expected top chunk to be seeded doc, got {top_chunk['document_id']}"
        assert top_chunk["filename"] == "BIS_Information_and_Knowledge_Base.pdf"
        assert top_chunk["similarity_score"] > 0.6, f"Expected similarity > 0.6, got {top_chunk['similarity_score']}"
        results["8. Semantic Retrieval of Seeded Knowledge"] = "PASS"
    except Exception as e:
        results["8. Semantic Retrieval of Seeded Knowledge"] = f"FAIL: {e}"

    # TEST 9: Citation and Source Structure Compatibility
    try:
        rag = RAGService.get_instance()
        retrieval_res = retriever.retrieve("BIS Act 2016 conformity assessment schemes", top_k=3)
        context_str, used_chunks = rag.construct_context_with_used_chunks(retrieval_res["results"])
        sources = rag._format_sources(used_chunks)

        assert len(sources) > 0, "Expected formatted sources"
        source = sources[0]
        assert "document_id" in source
        assert "filename" in source
        assert "chunk_id" in source
        assert "chunk_index" in source
        assert "similarity_score" in source
        assert "snippet" in source
        assert "pages" in source
        results["9. Citation & Source Structure Compatibility"] = "PASS"
    except Exception as e:
        results["9. Citation & Source Structure Compatibility"] = f"FAIL: {e}"

    # TEST 10: Provider Collection Isolation
    try:
        from services.embedding_service import embedding_service
        # Local provider
        os.environ["EMBEDDING_PROVIDER"] = "local"
        embedding_service.provider = "local"
        EmbeddingService._instance = None
        VectorStoreService._instance = None
        coll_local = get_default_collection_name()
        assert coll_local == "bis_documents_multilingual", f"Expected 'bis_documents_multilingual', got '{coll_local}'"

        # Gemini provider
        os.environ["EMBEDDING_PROVIDER"] = "gemini"
        os.environ["GEMINI_API_KEY"] = "test_mock_gemini_key_for_collection_check"
        embedding_service.provider = "gemini"
        EmbeddingService._instance = None
        VectorStoreService._instance = None
        coll_gemini = get_default_collection_name()
        assert coll_gemini == "bis_documents_gemini_multilingual", f"Expected 'bis_documents_gemini_multilingual', got '{coll_gemini}'"

        # Reset back to default
        os.environ.pop("EMBEDDING_PROVIDER", None)
        os.environ.pop("GEMINI_API_KEY", None)
        embedding_service.provider = "auto"
        EmbeddingService._instance = None
        VectorStoreService._instance = None
        results["10. Provider Collection Isolation (Gemini vs Local)"] = "PASS"
    except Exception as e:
        results["10. Provider Collection Isolation (Gemini vs Local)"] = f"FAIL: {e}"

    # TEST 11: Build-Time Seeding Fails Clearly when GEMINI_API_KEY is Unavailable
    try:
        orig_gemini = os.environ.get("GEMINI_API_KEY")
        orig_llm = os.environ.get("LLM_API_KEY")
        orig_emb = os.environ.get("EMBEDDING_API_KEY")
        try:
            os.environ["GEMINI_API_KEY"] = ""
            os.environ["LLM_API_KEY"] = ""
            os.environ["EMBEDDING_API_KEY"] = ""
            from services.embedding_service import embedding_service
            embedding_service.provider = "gemini"
            EmbeddingService._instance = None
            VectorStoreService._instance = None

            raised = False
            try:
                seed_knowledge_base(provider="gemini", dry_run=True)
            except RuntimeError as exc:
                raised = True
                assert "Build-time seeding failed" in str(exc)
                assert "GEMINI_API_KEY" in str(exc)
            assert raised, "Expected RuntimeError when --provider gemini is specified without API key"
            results["11. Build-Time Seeding Fails Clearly Without API Key"] = "PASS"
        finally:
            if orig_gemini is not None:
                os.environ["GEMINI_API_KEY"] = orig_gemini
            else:
                os.environ.pop("GEMINI_API_KEY", None)
            if orig_llm is not None:
                os.environ["LLM_API_KEY"] = orig_llm
            else:
                os.environ.pop("LLM_API_KEY", None)
            if orig_emb is not None:
                os.environ["EMBEDDING_API_KEY"] = orig_emb
            else:
                os.environ.pop("EMBEDDING_API_KEY", None)
            embedding_service.provider = "auto"
            EmbeddingService._instance = None
            VectorStoreService._instance = None
    except Exception as e:
        results["11. Build-Time Seeding Fails Clearly Without API Key"] = f"FAIL: {e}"

    # TEST 12: Build-Time Gemini Model and Collection Guarantee
    try:
        orig_gemini = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ["GEMINI_API_KEY"] = "mock_valid_key_for_collection_check_only"
            os.environ["EMBEDDING_PROVIDER"] = "gemini"
            from services.embedding_service import embedding_service
            embedding_service.provider = "gemini"
            EmbeddingService._instance = None
            VectorStoreService._instance = None

            summary = seed_knowledge_base(provider="gemini", dry_run=True)
            assert summary["active_collection"] == "bis_documents_gemini_multilingual", (
                f"Expected bis_documents_gemini_multilingual, got {summary['active_collection']}"
            )
            assert summary["active_model"] == "models/gemini-embedding-001", (
                f"Expected models/gemini-embedding-001, got {summary['active_model']}"
            )
            assert summary["embedding_dimension"] == 768, (
                f"Expected dimension 768, got {summary['embedding_dimension']}"
            )
            results["12. Build-Time Gemini Model and Collection Guarantee"] = "PASS"
        finally:
            if orig_gemini is not None:
                os.environ["GEMINI_API_KEY"] = orig_gemini
            else:
                os.environ.pop("GEMINI_API_KEY", None)
            os.environ.pop("EMBEDDING_PROVIDER", None)
            os.environ.pop("CHROMA_COLLECTION_NAME", None)
            embedding_service.provider = "auto"
            EmbeddingService._instance = None
            VectorStoreService._instance = None
    except Exception as e:
        results["12. Build-Time Gemini Model and Collection Guarantee"] = f"FAIL: {e}"

    # PRINT TEST SUMMARY
    print("\n" + "=" * 55)
    print("      KNOWLEDGE BASE SEEDING TEST RESULTS")
    print("=====================================================")
    all_passed = True
    passed = 0
    failed = 0
    for name, status in results.items():
        print(f"{name}: {status}")
        if status == "PASS":
            passed += 1
        else:
            all_passed = False
            failed += 1

    print(f"\nTotal Tests: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("OVERALL STATUS:", "ALL TESTS PASSED!" if all_passed else "SOME TESTS FAILED.")
    print("=====================================================\n")
    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
