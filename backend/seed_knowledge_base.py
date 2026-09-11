import os
import sys
import uuid
import argparse
from typing import List, Dict, Any, Optional

# Ensure backend root is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Try loading .env if dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

from services.document_processor import process_document, DocumentExtractionResult
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStoreService, get_default_collection_name
from services.security_utils import validate_and_sanitize_filename

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
DEFAULT_KB_DIR = os.path.join(BASE_DIR, "knowledge_base")


def get_deterministic_doc_id(filename: str) -> str:
    """
    Generates a deterministic, standard 36-char UUID5 for a knowledge base document
    based on its sanitized filename. Ensures idempotent document identification.
    """
    safe_name = validate_and_sanitize_filename(filename)
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"bis-knowledge-base:{safe_name}"))


def scan_knowledge_base_dir(kb_dir: str) -> List[str]:
    """
    Scans the knowledge base directory for supported documents (.pdf, .docx, .txt).
    Skips hidden files and subdirectories. Returns sorted list of absolute file paths.
    """
    if not os.path.isdir(kb_dir):
        return []

    valid_files = []
    for entry in sorted(os.listdir(kb_dir)):
        if entry.startswith("."):
            continue
        full_path = os.path.join(kb_dir, entry)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(entry)
            if ext.lower() in ALLOWED_EXTENSIONS:
                valid_files.append(full_path)

    return valid_files


def seed_knowledge_base(
    kb_dir: Optional[str] = None,
    provider: Optional[str] = None,
    force: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Main seeding engine:
    1. Scans knowledge base directory for supported documents.
    2. Configures embedding service and active ChromaDB collection.
    3. Idempotently indexes each document into the vector store.
    4. Returns summary dictionary of seeding results.
    """
    target_kb_dir = os.path.abspath(kb_dir or DEFAULT_KB_DIR)

    # Configure embedding provider if specified
    if provider:
        clean_provider = provider.lower().strip()
        os.environ["EMBEDDING_PROVIDER"] = clean_provider
        from services.embedding_service import embedding_service
        embedding_service.provider = clean_provider
        EmbeddingService._instance = None
        VectorStoreService._instance = None

    embedder = EmbeddingService.get_instance()
    if provider and provider.lower().strip() == "gemini":
        if not embedder._should_use_gemini():
            raise RuntimeError(
                "Build-time seeding failed: '--provider gemini' was specified, but GEMINI_API_KEY "
                "(or LLM_API_KEY) is missing or invalid in the environment. "
                "The build cannot proceed with local embeddings. Please configure GEMINI_API_KEY in Render."
            )
        os.environ["CHROMA_COLLECTION_NAME"] = "bis_documents_gemini_multilingual"
        VectorStoreService._instance = None

    vs = VectorStoreService.get_instance()
    active_collection = vs.collection_name
    active_model = getattr(embedder, "active_model_name", embedder.model_name)

    files = scan_knowledge_base_dir(target_kb_dir)

    results = {
        "kb_dir": target_kb_dir,
        "active_collection": active_collection,
        "active_model": active_model,
        "embedding_dimension": embedder.dimension,
        "total_files_found": len(files),
        "newly_indexed": 0,
        "already_indexed": 0,
        "failed": 0,
        "files": []
    }

    if not files:
        print(f"No supported documents (.pdf, .docx, .txt) found in: {target_kb_dir}")
        return results

    collection = vs._init_db()

    for fpath in files:
        fname = os.path.basename(fpath)
        _, ext = os.path.splitext(fname)
        ext_lower = ext.lower()
        safe_fname = validate_and_sanitize_filename(fname)
        doc_id = get_deterministic_doc_id(safe_fname)

        # Check existing chunks in ChromaDB for idempotency
        existing_count = 0
        try:
            existing = collection.get(where={"document_id": doc_id})
            existing_count = len(existing.get("ids", []))
        except Exception:
            existing_count = 0

        file_stat = {
            "filename": safe_fname,
            "document_id": doc_id,
            "path": fpath,
            "file_size": os.path.getsize(fpath),
            "status": "pending",
            "chunk_count": existing_count
        }

        # Idempotency check: skip if already indexed and not force
        if existing_count > 0 and not force:
            print(f"  [ALREADY INDEXED] '{safe_fname}' is present with {existing_count} chunk(s) (ID: {doc_id}). Skipping.")
            file_stat["status"] = "already_indexed"
            results["already_indexed"] += 1
            results["files"].append(file_stat)
            continue

        if dry_run:
            print(f"  [DRY-RUN] Would process and index '{safe_fname}' (ID: {doc_id}).")
            file_stat["status"] = "dry_run"
            results["newly_indexed"] += 1
            results["files"].append(file_stat)
            continue

        action_label = "Re-indexing" if existing_count > 0 else "Indexing"
        print(f"  [{action_label.upper()}] Processing '{safe_fname}' (ID: {doc_id})...")

        try:
            res: DocumentExtractionResult = process_document(
                file_path=fpath,
                file_type=ext_lower,
                document_id=doc_id,
                filename=safe_fname
            )

            if res.success:
                file_stat["status"] = "indexed"
                file_stat["chunk_count"] = res.chunk_count
                file_stat["text_length"] = res.text_length
                file_stat["cleaned_text_length"] = res.cleaned_text_length
                file_stat["pages"] = res.pages
                file_stat["embedding_model"] = res.embedding_model
                file_stat["embedding_dimension"] = res.embedding_dimension
                results["newly_indexed"] += 1
                print(f"    [OK] Successfully indexed {res.chunk_count} chunk(s) ({res.embedding_model}, {res.embedding_dimension}d, {res.pages or 1} page(s)).")
            else:
                file_stat["status"] = "failed"
                file_stat["error"] = res.error
                results["failed"] += 1
                print(f"    [FAIL] Failed to process '{safe_fname}': {res.error}")

        except Exception as e:
            file_stat["status"] = "failed"
            file_stat["error"] = str(e)
            results["failed"] += 1
            print(f"    [FAIL] Exception while indexing '{safe_fname}': {e}")

        results["files"].append(file_stat)

    results["total_collection_chunks"] = vs.count_chunks()
    return results


def print_summary(res: Dict[str, Any]):
    print("\n" + "=" * 55)
    print("        KNOWLEDGE BASE SEEDING SUMMARY")
    print("=====================================================")
    print(f"Knowledge Base Dir:    {res['kb_dir']}")
    print(f"Active Collection:     {res['active_collection']}")
    print(f"Active Model:          {res['active_model']} ({res['embedding_dimension']}d)")
    print(f"Files Discovered:      {res['total_files_found']}")
    print(f"Files Newly Indexed:   {res['newly_indexed']}")
    print(f"Files Already Indexed: {res['already_indexed']}")
    print(f"Files Failed:          {res['failed']}")
    if "total_collection_chunks" in res:
        print(f"Total Vector Chunks:   {res['total_collection_chunks']}")
    print("=====================================================")


def main():
    parser = argparse.ArgumentParser(
        description="Standalone idempotent knowledge-base seeding script for BIS AI Assistant."
    )
    parser.add_argument(
        "--kb-dir",
        type=str,
        default=None,
        help="Path to directory containing knowledge base documents (default: backend/knowledge_base)."
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["auto", "gemini", "local"],
        default=None,
        help="Embedding provider to use (auto, gemini, or local; default: auto)."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing of documents even if they are already present in vector store."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report documents without generating embeddings or modifying vector store."
    )

    args = parser.parse_args()

    print("\nStarting BIS Knowledge Base Seeding...")
    try:
        summary = seed_knowledge_base(
            kb_dir=args.kb_dir,
            provider=args.provider,
            force=args.force,
            dry_run=args.dry_run
        )
        print_summary(summary)
        if summary["failed"] > 0:
            sys.exit(1)
        sys.exit(0)
    except Exception as exc:
        print(f"\n[BUILD ERROR] Knowledge base seeding failed: {exc}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
