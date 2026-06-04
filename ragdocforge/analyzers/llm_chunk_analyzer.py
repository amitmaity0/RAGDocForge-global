import json
from pathlib import Path

from pydantic import BaseModel, Field

from ragdocforge.llm.json_utils import validate_or_warn
from ragdocforge.llm.provider import LLMProvider, LLMProviderError
from ragdocforge.schemas.chunk_models import RagChunk
from ragdocforge.schemas.llm_analysis_models import LLMChunkCritique


class _ChunkCritiqueList(BaseModel):
    chunk_critiques: list[LLMChunkCritique] = Field(default_factory=list)


class LLMChunkAnalyzer:
    def __init__(self, provider: LLMProvider, max_chunks_to_review: int = 12) -> None:
        self.provider = provider
        self.max_chunks_to_review = max_chunks_to_review
        self.system_prompt = _read_prompt("llm_chunk_review.md")

    def analyze(self, chunks: list[RagChunk], warnings: list[str]) -> list[LLMChunkCritique]:
        if not chunks:
            return []
        review_chunks = chunks[: self.max_chunks_to_review]
        try:
            payload = self.provider.generate_json(
                self.system_prompt,
                self._build_user_prompt(review_chunks),
                "LLMChunkCritiqueList",
                max_tokens=1024,
            )
        except LLMProviderError as exc:
            warnings.append(str(exc))
            return []
        normalized = self._normalize_payload(payload, review_chunks)
        result = validate_or_warn(_ChunkCritiqueList, normalized, warnings)
        return result.chunk_critiques if isinstance(result, _ChunkCritiqueList) else []

    def _build_user_prompt(self, chunks: list[RagChunk]) -> str:
        return json.dumps(
            {
                "task": "Return exactly one JSON object with key chunk_critiques. Create one critique per input chunk_id.",
                "required_schema": {
                    "chunk_critiques": [
                        {
                            "chunk_id": "must match an input chunk_id",
                            "retrieval_usefulness_score": "integer 0-5",
                            "answerability_score": "integer 0-5",
                            "chunk_issue_summary": "string",
                            "missing_metadata": ["string"],
                            "improved_chunk_title": "string or null",
                            "suggested_keywords": ["string"],
                            "should_split": "boolean",
                            "should_merge_with_neighbors": "boolean",
                        }
                    ]
                },
                "chunks": [self._compact_chunk(chunk) for chunk in chunks],
            },
            indent=2,
        )

    def _normalize_payload(self, payload: dict, chunks: list[RagChunk]) -> dict:
        critiques = payload.get("chunk_critiques", [])
        if critiques and len(critiques) == 1 and critiques[0].get("chunk_id") == "mock_chunk_0001":
            critiques = [{**critiques[0], "chunk_id": chunk.chunk_id} for chunk in chunks]
        return {"chunk_critiques": critiques}

    def _compact_chunk(self, chunk: RagChunk) -> dict:
        payload = chunk.model_dump()
        payload["text"] = chunk.text[:1200]
        return payload


def _read_prompt(name: str) -> str:
    return (Path(__file__).resolve().parents[1] / "prompts" / name).read_text(encoding="utf-8")
