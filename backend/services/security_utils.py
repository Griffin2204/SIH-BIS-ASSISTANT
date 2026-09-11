import os
import re
from typing import Optional

# Maximum allowed lengths
MAX_FILENAME_LENGTH = 255
MAX_QUESTION_LENGTH = 1000
MAX_QUERY_LENGTH = 1000
MAX_DOCUMENT_CHARS = 1_000_000

# Regex patterns for sanitization
API_KEY_REGEX = re.compile(r'(?:AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._-]+)', re.IGNORECASE)
FILESYSTEM_PATH_REGEX = re.compile(r'(?:[A-Za-z]:\\[^\s"\'<>]+|/(?:Users|home|var|etc|opt|tmp)/[^\s"\'<>]+)', re.IGNORECASE)
TRACEBACK_REGEX = re.compile(r'Traceback\s*\(most\s*recent\s*call\s*last\):[\s\S]+', re.IGNORECASE)


def sanitize_error_detail(detail: str) -> str:
    """
    Strips API keys, tokens, filesystem paths, and Python tracebacks from error strings.
    Ensures safe, non-leaking user-facing error messages.
    """
    if not detail or not isinstance(detail, str):
        return "An error occurred while processing the request."

    sanitized = detail

    # Redact API keys and authorization tokens
    sanitized = API_KEY_REGEX.sub("[REDACTED_SECRET]", sanitized)

    # Redact Python tracebacks
    sanitized = TRACEBACK_REGEX.sub("Internal server error occurred.", sanitized)

    # Redact filesystem paths
    sanitized = FILESYSTEM_PATH_REGEX.sub("[REDACTED_PATH]", sanitized)

    return sanitized.strip()


def validate_and_sanitize_filename(raw_filename: Optional[str]) -> str:
    """
    Validates and sanitizes an uploaded filename:
    1. Prevents path traversal (strips directory components, rejects ../ and ..\\).
    2. Enforces MAX_FILENAME_LENGTH (255 characters).
    3. Normalizes allowed characters to [a-zA-Z0-9._-].
    4. Ensures file has a valid extension.
    """
    if not raw_filename or not raw_filename.strip():
        raise ValueError("Filename cannot be empty.")

    # Disallow path traversal sequences
    if ".." in raw_filename or "/" in raw_filename or "\\" in raw_filename:
        # Extract purely the base name
        cleaned_base = os.path.basename(raw_filename.replace("\\", "/"))
    else:
        cleaned_base = raw_filename.strip()

    # Disallow absolute Windows drive letters (e.g. C:filename.txt)
    if ":" in cleaned_base:
        cleaned_base = cleaned_base.split(":")[-1].lstrip("/\\")

    # Enforce allowed characters only
    safe_name = "".join(c for c in cleaned_base if c.isalnum() or c in (".", "_", "-")).strip()

    if not safe_name or safe_name.startswith("."):
        safe_name = f"uploaded_file{safe_name}"

    if len(safe_name) > MAX_FILENAME_LENGTH:
        # Keep extension intact
        base, ext = os.path.splitext(safe_name)
        allowed_base_len = MAX_FILENAME_LENGTH - len(ext)
        safe_name = base[:allowed_base_len] + ext

    return safe_name


def assert_within_directory(target_path: str, base_directory: str) -> bool:
    """
    Verifies that target_path resides strictly within base_directory.
    Prevents path traversal and directory escape attacks.
    """
    abs_target = os.path.abspath(target_path)
    abs_base = os.path.abspath(base_directory)

    try:
        common = os.path.commonpath([abs_target, abs_base])
        return common == abs_base
    except (ValueError, Exception):
        return False
