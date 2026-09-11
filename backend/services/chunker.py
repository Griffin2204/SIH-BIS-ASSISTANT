import re
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    chunk_text: str
    character_count: int
    file_type: Optional[str] = None
    pages: Optional[int] = None
    embedding: Optional[List[float]] = None
    embedding_dimension: Optional[int] = None
    embedding_model: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def chunk_text(
    cleaned_text: str,
    document_id: str,
    filename: str,
    target_chunk_size: int = 1000,
    overlap: int = 150,
    file_type: Optional[str] = None,
    pages: Optional[int] = None
) -> List[DocumentChunk]:
    """
    Splits cleaned document text into structured, boundary-aware chunks with overlap.
    
    Priority for boundary splitting:
    1. Paragraph boundaries (\\n\\n)
    2. Sentence boundaries (. ? !)
    3. Whitespace boundaries (spaces)
    4. Character fallback
    
    Preserves exact technical identifiers (IS 10500, ISO 9001), technical units (20°C, ±0.5%, ₹500),
    case, and Indian language text without summarizing or altering content.
    """
    if not cleaned_text or not cleaned_text.strip():
        return []

    text = cleaned_text.strip()
    text_length = len(text)

    # 1. Single chunk for short documents
    if text_length <= target_chunk_size:
        c_id = f"{document_id}_chunk_0"
        return [
            DocumentChunk(
                chunk_id=c_id,
                document_id=document_id,
                filename=filename,
                chunk_index=0,
                chunk_text=text,
                character_count=text_length,
                file_type=file_type,
                pages=pages
            )
        ]

    # 2. Decompose document into atomic units (paragraphs / sentences)
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    units: List[str] = []

    for para in raw_paragraphs:
        if len(para) <= target_chunk_size:
            units.append(para)
        else:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(sentence) <= target_chunk_size:
                    units.append(sentence)
                else:
                    words = sentence.split(" ")
                    curr_words: List[str] = []
                    curr_len = 0
                    for word in words:
                        if curr_len + len(word) + 1 <= target_chunk_size:
                            curr_words.append(word)
                            curr_len += len(word) + 1
                        else:
                            if curr_words:
                                units.append(" ".join(curr_words))
                            curr_words = [word]
                            curr_len = len(word)
                    if curr_words:
                        units.append(" ".join(curr_words))

    # 3. Assemble units into chunks respecting target_chunk_size & overlap
    chunks: List[DocumentChunk] = []
    current_units: List[str] = []
    current_len = 0
    chunk_idx = 0

    for unit in units:
        unit_len = len(unit)

        if current_units and (current_len + unit_len + 2 > target_chunk_size):
            chunk_body = "\n\n".join(current_units).strip()
            if chunk_body:
                c_id = f"{document_id}_chunk_{chunk_idx}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=c_id,
                        document_id=document_id,
                        filename=filename,
                        chunk_index=chunk_idx,
                        chunk_text=chunk_body,
                        character_count=len(chunk_body),
                        file_type=file_type,
                        pages=pages
                    )
                )
                chunk_idx += 1

            overlap_prefix = _extract_overlap_prefix(chunk_body, overlap)
            if overlap_prefix:
                current_units = [overlap_prefix, unit]
                current_len = len(overlap_prefix) + 2 + unit_len
            else:
                current_units = [unit]
                current_len = unit_len
        else:
            current_units.append(unit)
            current_len += unit_len + (2 if len(current_units) > 1 else 0)

    if current_units:
        final_body = "\n\n".join(current_units).strip()
        if final_body:
            c_id = f"{document_id}_chunk_{chunk_idx}"
            chunks.append(
                DocumentChunk(
                    chunk_id=c_id,
                    document_id=document_id,
                    filename=filename,
                    chunk_index=chunk_idx,
                    chunk_text=final_body,
                    character_count=len(final_body),
                    file_type=file_type,
                    pages=pages
                )
            )

    return chunks


def _extract_overlap_prefix(text: str, overlap: int) -> str:
    if not text or overlap <= 0:
        return ""

    if len(text) <= overlap:
        return text

    snippet = text[-overlap:]
    space_idx = snippet.find(" ")
    if space_idx != -1 and space_idx < len(snippet) // 2:
        return snippet[space_idx + 1:].strip()

    return snippet.strip()
