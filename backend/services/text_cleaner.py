import re
import unicodedata

def clean_text(raw_text: str) -> str:
    """
    Cleans and normalizes extracted document text for downstream processing.
    
    Operations:
    1. NFC Unicode Normalization (supports Indian languages, math, technical symbols, currency).
    2. Line break normalization (converts \\r\\n and \\r to \\n).
    3. Per-line whitespace normalization (converts tabs and multiple spaces to single spaces; trims line ends).
    4. Excessive blank line reduction (converts 3+ consecutive newlines to double newlines \\n\\n).
    5. Preserves case, numbers, standards identifiers (IS 10500, ISO 9001), headings, and paragraphs.
    """
    if not raw_text:
        return ""

    # 1. Safe Unicode Normalization (NFC preserves Indic scripts, math, currency & legal symbols)
    text = unicodedata.normalize("NFC", raw_text)

    # 2. Normalize Line Breaks (\\r\\n and \\r -> \\n)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Process lines: normalize horizontal whitespace and trim each line
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Convert tabs to spaces
        line_clean = line.replace("\t", " ")
        # Replace multiple spaces within a line with a single space
        line_clean = re.sub(r" {2,}", " ", line_clean)
        # Trim leading and trailing spaces on the line
        line_clean = line_clean.strip()
        cleaned_lines.append(line_clean)

    text = "\n".join(cleaned_lines)

    # 4. Normalize excessive blank lines (3 or more consecutive newlines -> double newline)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
