import re

from ragdocforge.analyzers.oracle_object_extractor import MIN_CHUNK_OBJECT_CONFIDENCE, extract_error_metadata, extract_oracle_object_candidates
from ragdocforge.schemas.chunk_models import RagChunk
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.utils.token_utils import estimate_tokens
from ragdocforge.utils.text_utils import unique_sorted

MIN_CHUNK_TOKENS = 120
GENERIC_LOW_PRIORITY_SECTIONS = {
    "REFERENCES",
    "REFERENCE",
    "COMMUNITY DISCUSSIONS",
    "RELATED LINKS",
    "EXTERNAL RESOURCES",
    "APPENDIX",
    "SEE ALSO",
    "ADDITIONAL INFORMATION",
}
ACTION_KEYWORD_RE = re.compile(r"\b(?:action|resolution|resolve|fix|diagnos(?:e|is|tic)|validate|validation|procedure|step|troubleshoot|cause)\b", re.I)
SQL_BLOCK_RE = re.compile(r"```sql[\s\S]+?```", re.I)


class Chunker:
    def chunk(self, document: ParsedDocument, chunk_size: int = 700, chunk_overlap: int = 100, min_chunk_tokens: int = MIN_CHUNK_TOKENS) -> list[RagChunk]:
        if not document.raw_text.split():
            return []
        chunk_size = max(100, chunk_size)
        chunk_overlap = min(max(0, chunk_overlap), chunk_size // 2)
        chunks: list[RagChunk] = []
        text_sections: list[tuple[str | None, str]] = []
        for section_title, section_text in self._sections(document.raw_text):
            for text in self._split_section(section_text, chunk_size, chunk_overlap):
                text_sections.append((section_title, text))
        text_sections = self._merge_small_chunks(text_sections, min_chunk_tokens)
        for section_title, text in text_sections:
            chunks.append(self._build_chunk(document, chunks, text, section_title, min_chunk_tokens))
        return chunks

    def _sections(self, text: str) -> list[tuple[str | None, str]]:
        matches = list(re.finditer(r"(?m)^(#{1,6}\s+.+)$", text))
        if not matches:
            return [(None, text.strip())]
        sections: list[tuple[str | None, str]] = []
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections.append((None, preamble))
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            title = match.group(1).lstrip("#").strip()
            section_text = text[start:end].strip()
            if section_text:
                sections.append((title, section_text))
        return sections

    def _split_section(self, text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        if estimate_tokens(text) <= chunk_size:
            return [text]
        parts = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        if len(parts) > 1:
            return self._pack_parts(parts, chunk_size, chunk_overlap)
        return self._split_words(text, chunk_size, chunk_overlap)

    def _pack_parts(self, parts: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
        chunks: list[str] = []
        current: list[str] = []
        for part in parts:
            if estimate_tokens(part) > chunk_size:
                if current:
                    chunks.append("\n\n".join(current))
                    current = []
                chunks.extend(self._split_words(part, chunk_size, chunk_overlap))
                continue
            candidate = "\n\n".join(current + [part])
            if current and estimate_tokens(candidate) > chunk_size:
                chunks.append("\n\n".join(current))
                overlap_words = " ".join(chunks[-1].split()[-chunk_overlap:]) if chunk_overlap else ""
                current = [overlap_words, part] if overlap_words else [part]
            else:
                current.append(part)
        if current:
            chunks.append("\n\n".join(part for part in current if part))
        return chunks

    def _split_words(self, text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        words = text.split()
        split_chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(len(words), start + chunk_size)
            split_chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = end - chunk_overlap
        return split_chunks

    def _merge_small_chunks(self, chunks: list[tuple[str | None, str]], min_chunk_tokens: int) -> list[tuple[str | None, str]]:
        if len(chunks) <= 1:
            return chunks
        merged: list[tuple[str | None, str]] = []
        index = 0
        while index < len(chunks):
            section, text = chunks[index]
            if estimate_tokens(text) < min_chunk_tokens and not should_preserve_small_chunk(text):
                if index + 1 < len(chunks):
                    next_section, next_text = chunks[index + 1]
                    merged.append((section or next_section, f"{text}\n\n{next_text}".strip()))
                    index += 2
                    continue
                if merged:
                    prev_section, prev_text = merged[-1]
                    merged[-1] = (prev_section, f"{prev_text}\n\n{text}".strip())
                    index += 1
                    continue
            merged.append((section, text))
            index += 1
        return merged

    def _build_chunk(self, document: ParsedDocument, chunks: list[RagChunk], text: str, section: str | None, min_chunk_tokens: int) -> RagChunk:
        candidates, _ = extract_oracle_object_candidates(text, MIN_CHUNK_OBJECT_CONFIDENCE)
        chunk_tables = [item.name for item in candidates if item.object_type == "table"]
        chunk_views = [item.name for item in candidates if item.object_type == "view"]
        chunk_packages = [item.name for item in candidates if item.object_type == "package"]
        chunk_procedures = [item.name for item in candidates if item.object_type == "procedure"]
        chunk_functions = [item.name for item in candidates if item.object_type == "function"]
        error_metadata = extract_error_metadata(text)
        chunk_errors = unique_sorted(error_metadata.error_codes + error_metadata.error_context_lines)
        chunk_keywords = _chunk_keywords(text, document.keywords)
        chunk_metadata = {
            "tables": chunk_tables,
            "packages": chunk_packages,
            "procedures": chunk_procedures,
            "functions": chunk_functions,
            "error_codes": error_metadata.error_codes,
            "error_context_lines": error_metadata.error_context_lines,
            "keywords": chunk_keywords,
        }
        confidence = _chunk_metadata_confidence(text, section, chunk_tables + chunk_packages + chunk_errors + chunk_keywords, min_chunk_tokens)
        return RagChunk(
            chunk_id=f"{document.doc_id}_{len(chunks) + 1:04d}",
            doc_id=document.doc_id,
            source_file=document.source_file,
            text=text,
            section=section,
            erp_module=document.detected_erp_module,
            doc_type=document.detected_doc_type,
            business_process=document.business_process,
            token_estimate=estimate_tokens(text),
            doc_tables=document.tables,
            doc_views=document.views,
            doc_packages=document.packages,
            doc_procedures=document.procedures,
            doc_functions=document.functions,
            doc_error_codes=document.error_codes,
            doc_error_context_lines=document.error_context_lines,
            doc_error_messages=document.error_messages,
            doc_keywords=document.keywords,
            chunk_tables=chunk_tables,
            chunk_views=chunk_views,
            chunk_packages=chunk_packages,
            chunk_procedures=chunk_procedures,
            chunk_functions=chunk_functions,
            concurrent_programs=document.concurrent_programs,
            chunk_error_codes=error_metadata.error_codes,
            chunk_error_context_lines=error_metadata.error_context_lines,
            chunk_error_messages=chunk_errors,
            chunk_keywords=chunk_keywords,
            rag_priority=infer_chunk_rag_priority(text, section, chunk_metadata),
            metadata_confidence=confidence,
        )


def should_preserve_small_chunk(text: str) -> bool:
    if re.search(r"\b(?:ORA|FRM|APP|REP|PLS|FND|FORM)-\d{3,6}\b", text, re.I):
        return True
    if re.search(r"```sql[\s\S]+?```", text, re.I) and estimate_tokens(text) > 40:
        return True
    table_rows = [line for line in text.splitlines() if line.strip().startswith("|") and line.strip().endswith("|")]
    return len(table_rows) >= 5


def infer_chunk_rag_priority(chunk_text: str, section: str | None, chunk_metadata: dict) -> str:
    token_count = estimate_tokens(chunk_text)
    section_name = (section or "").strip().upper()
    has_sql_block = bool(SQL_BLOCK_RE.search(chunk_text))
    has_objects = any(chunk_metadata.get(key) for key in ("tables", "packages", "procedures", "functions"))
    has_error_codes = bool(chunk_metadata.get("error_codes"))
    has_action = bool(ACTION_KEYWORD_RE.search(chunk_text))

    if has_sql_block and has_objects:
        return "high"
    if has_error_codes and has_action:
        return "high"
    if has_action and re.search(r"\b(?:diagnostic|validation|procedure|troubleshooting|cause|resolution)\b", chunk_text, re.I):
        return "high"
    if (
        section_name in GENERIC_LOW_PRIORITY_SECTIONS
        or (token_count < 80 and not has_objects and not has_error_codes and not has_action)
    ):
        return "low"
    return "medium"


def _chunk_keywords(text: str, doc_keywords: list[str]) -> list[str]:
    lower = text.lower()
    matches = [keyword for keyword in doc_keywords if keyword.lower() in lower]
    bind_vars = re.findall(r":([a-zA-Z][\w$#]*)", text)
    return sorted(set(matches + [value.upper() for value in bind_vars]))


def _chunk_metadata_confidence(text: str, section: str | None, local_signals: list[str], min_chunk_tokens: int) -> float:
    score = 1.0
    if not section:
        score -= 0.2
    if not local_signals:
        score -= 0.2
    if estimate_tokens(text) < min_chunk_tokens:
        score -= 0.2
    if _mostly_boilerplate(text):
        score -= 0.2
    return max(0.1, round(min(1.0, score), 2))


def _mostly_boilerplate(text: str) -> bool:
    lowered = text.lower()
    boilerplate_terms = ["copyright", "all rights reserved", "oracle support", "references", "appendix"]
    return sum(1 for term in boilerplate_terms if term in lowered) >= 2
