# Codex Task: Slice 2 — LLM Qualitative Analyzer for RAGDocForge

## Project Name

RAGDocForge

## Slice Goal

Extend the existing deterministic Slice 1 Gradio application with an optional LLM-assisted qualitative analysis layer.

Slice 1 already performs deterministic parsing, metadata extraction, quality scoring, RAG markdown conversion, chunking, and ZIP export.

Slice 2 must add optional LLM capabilities for:

1. Document quality critique
2. Missing-content gap analysis
3. RAG-readiness improvement suggestions
4. Suggested rewritten sections
5. Better metadata suggestions
6. Example support questions the document should answer
7. Chunk-level retrieval usefulness review

The LLM must be optional. The app must still work in deterministic-only mode with no API key and no local model.

---

# 1. Important Scope Rules

## 1.1 Slice 2 Adds LLM Analysis Only

Do not replace the deterministic Slice 1 pipeline.

Slice 2 should run after Slice 1 has produced:

```text
ParsedDocument
QualityReport
RAG markdown
RagChunk list
manifest
ZIP export
```

LLM analysis should enrich the existing output, not become the primary parser or scorer.

## 1.2 No Vector DB Yet

Do not implement:

```text
Qdrant
Embeddings
Semantic search
RAG retrieval runtime
Document ingestion into vector stores
LangChain
LlamaIndex
```

Those belong to later slices.

## 1.3 No Required Cloud Dependency

The app must run without OpenAI, Ollama, or Hugging Face Inference.

Default mode:

```text
LLM Provider: Disabled / Deterministic Only
```

When disabled, the app should behave exactly like Slice 1.

---

# 2. Required New Capabilities

## 2.1 LLM Provider Abstraction

Add a provider abstraction layer.

Create:

```text
ragdocforge/llm/
  __init__.py
  provider.py
  openai_compatible_provider.py
  ollama_provider.py
  mock_provider.py
```

### Provider Interface

Create an abstract base class or protocol:

```python
class LLMProvider(Protocol):
    provider_name: str

    def is_configured(self) -> bool:
        ...

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict:
        ...

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        ...
```

### Supported Providers

Implement:

```text
disabled
mock
ollama
openai_compatible
```

Provider behavior:

| Provider          | Purpose                                     |
| ----------------- | ------------------------------------------- |
| disabled          | No LLM calls                                |
| mock              | Test mode with deterministic fake responses |
| ollama            | Local/private analysis                      |
| openai_compatible | OpenAI-compatible HTTP endpoint             |

Do not add the official OpenAI SDK in Slice 2. Use `httpx` or `requests` for OpenAI-compatible `/v1/chat/completions`.

---

# 3. Configuration

Add environment-based configuration.

Create or update:

```text
.env.example
```

Fields:

```bash
RAGDOCFORGE_LLM_PROVIDER=disabled

# For OpenAI-compatible endpoints
RAGDOCFORGE_OPENAI_BASE_URL=https://api.openai.com/v1
RAGDOCFORGE_OPENAI_API_KEY=
RAGDOCFORGE_OPENAI_MODEL=gpt-4.1-mini

# For Ollama
RAGDOCFORGE_OLLAMA_BASE_URL=http://m4.local:11438
RAGDOCFORGE_OLLAMA_MODEL=gemma3

# Runtime safety
RAGDOCFORGE_LLM_TIMEOUT_SECONDS=60
RAGDOCFORGE_LLM_MAX_DOC_CHARS=20000
RAGDOCFORGE_LLM_MAX_CHUNKS_TO_REVIEW=12
```

Add dependency:

```text
python-dotenv>=1.0.0
httpx>=0.27.0
```

Update `requirements.txt`.

---

# 4. New Schemas

Create:

```text
ragdocforge/schemas/llm_analysis_models.py
```

## 4.1 LLMDocumentCritique

```python
class LLMDocumentCritique(BaseModel):
    doc_id: str
    source_file: str
    summary: str
    rag_readiness_assessment: str
    main_strengths: list[str]
    major_weaknesses: list[str]
    missing_context: list[str]
    missing_sections: list[str]
    metadata_improvements: list[str]
    retrieval_risk_factors: list[str]
    hallucination_risk_factors: list[str]
    recommended_additions: list[str]
    rewritten_title: str | None = None
    suggested_tags: list[str] = []
    support_questions_answerable: list[str] = []
    support_questions_not_answerable: list[str] = []
```

## 4.2 LLMSuggestedSection

```python
class LLMSuggestedSection(BaseModel):
    section_title: str
    reason_needed: str
    suggested_content: str
    priority: Literal["critical", "high", "medium", "low"]
```

## 4.3 LLMChunkCritique

```python
class LLMChunkCritique(BaseModel):
    chunk_id: str
    retrieval_usefulness_score: int
    answerability_score: int
    chunk_issue_summary: str
    missing_metadata: list[str]
    improved_chunk_title: str | None = None
    suggested_keywords: list[str] = []
    should_split: bool = False
    should_merge_with_neighbors: bool = False
```

## 4.4 LLMAnalysisBundle

```python
class LLMAnalysisBundle(BaseModel):
    doc_id: str
    source_file: str
    provider_name: str
    document_critique: LLMDocumentCritique | None = None
    suggested_sections: list[LLMSuggestedSection] = []
    chunk_critiques: list[LLMChunkCritique] = []
    raw_provider_warnings: list[str] = []
```

---

# 5. Prompt Files

Create:

```text
ragdocforge/prompts/
  llm_document_critique.md
  llm_gap_analysis.md
  llm_chunk_review.md
  llm_section_rewrite.md
```

Prompt files must be plain markdown templates.

---

# 6. LLM Analysis Modules

Create:

```text
ragdocforge/analyzers/llm_document_analyzer.py
ragdocforge/analyzers/llm_gap_analyzer.py
ragdocforge/analyzers/llm_chunk_analyzer.py
```

## 6.1 LLM Document Analyzer

Input:

```text
ParsedDocument
QualityReport
RAG markdown
```

Output:

```text
LLMDocumentCritique
```

It should ask the LLM to evaluate:

```text
- Is this document useful as a RAG source?
- What important context is missing?
- What support questions can this document answer?
- What support questions can it not answer?
- What metadata should be added?
- What retrieval or hallucination risks exist?
- What title/tags would improve retrieval?
```

## 6.2 LLM Gap Analyzer

Input:

```text
ParsedDocument
QualityReport
LLMDocumentCritique
```

Output:

```text
list[LLMSuggestedSection]
```

It should suggest concrete missing sections.

Examples:

```text
Purpose
Scope
Prerequisites
Diagnostic SQL
Validation Steps
Expected Output
Rollback Steps
Known Error Messages
Table/Object Glossary
Concurrent Program Parameters
Environment Assumptions
```

Each suggested section must include:

```text
section_title
reason_needed
suggested_content
priority
```

The `suggested_content` should be usable as a draft but must not invent unsupported environment-specific facts.

It may include placeholders such as:

```text
[Confirm ledger name]
[Add concurrent request name]
[Insert validated SQL]
[Confirm responsibility/navigation path]
```

## 6.3 LLM Chunk Analyzer

Input:

```text
list[RagChunk]
```

Output:

```text
list[LLMChunkCritique]
```

Only analyze the first `RAGDOCFORGE_LLM_MAX_CHUNKS_TO_REVIEW` chunks per document.

The LLM should assess:

```text
- Is this chunk independently retrievable?
- Does it contain enough context?
- Are metadata fields missing?
- Should the chunk be split?
- Should it be merged?
- What keywords should be added?
- What title would improve chunk retrievability?
```

---

# 7. JSON Output and Validation

All LLM calls must request JSON.

Each response must be validated using Pydantic.

If validation fails:

1. Try to extract the first valid JSON object from the response.
2. Validate again.
3. If still invalid, record a provider warning.
4. Do not fail the entire batch.

Create:

```text
ragdocforge/llm/json_utils.py
```

Functions:

```python
def extract_first_json_object(text: str) -> dict | None:
    ...

def validate_or_warn(model_cls: type[BaseModel], payload: dict, warnings: list[str]) -> BaseModel | None:
    ...
```

---

# 8. UI Changes

Update Gradio UI.

## 8.1 Upload & Settings Tab

Add LLM settings panel:

```text
Enable LLM qualitative analysis: checkbox
LLM provider: dropdown
Model name: textbox
Base URL: textbox
API key: password textbox
Max document characters: number
Max chunks to review: number
```

Provider dropdown:

```text
disabled
mock
ollama
openai_compatible
```

Default:

```text
disabled
```

If disabled, LLM fields may stay visible but no call should run.

## 8.2 New Tab: LLM Quality Review

Add a tab after deterministic quality report.

Display:

```text
Provider used
Document critique JSON
Main strengths
Major weaknesses
Missing context
Retrieval risk factors
Hallucination risk factors
Recommended additions
Support questions answerable
Support questions not answerable
```

## 8.3 New Tab: Suggested Sections

Display a table:

```text
priority
section_title
reason_needed
suggested_content
```

## 8.4 Chunk Preview Enhancement

Add optional LLM chunk critique columns:

```text
retrieval_usefulness_score
answerability_score
chunk_issue_summary
suggested_keywords
should_split
should_merge_with_neighbors
```

## 8.5 Export Changes

Add export files:

```text
llm_analysis_report.json
suggested_sections.md
```

Update ZIP structure:

```text
markdown/
  doc1.md
  doc2.md

chunks.jsonl
quality_report.json
llm_analysis_report.json
suggested_sections.md
manifest.json
```

---

# 9. Suggested Sections Markdown Export

Create:

```text
ragdocforge/converters/suggested_sections_exporter.py
```

Output:

```text
suggested_sections.md
```

Format:

````markdown
# Suggested Content Improvements

## Source: JournalImport.pdf

### Critical: Diagnostic SQL

Reason needed:
The document describes Journal Import errors but does not provide validated SQL to identify failed interface rows.

Suggested content:
```markdown
## Diagnostic SQL

Use this section to add validated read-only SQL queries for identifying failed Journal Import rows.

[Insert validated SQL query here]

Expected output:
[Describe expected result columns and interpretation]
````

````

---

# 10. Manifest Changes

Extend `manifest.json` with:

```json
{
  "llm_analysis_enabled": true,
  "llm_provider": "ollama",
  "llm_model": "qwen2.5:7b",
  "llm_documents_analyzed": 3,
  "llm_chunk_critiques_created": 12,
  "llm_provider_warnings": []
}
````

If disabled:

```json
{
  "llm_analysis_enabled": false,
  "llm_provider": "disabled"
}
```

---

# 11. OpenAI-Compatible Provider

Implement:

```text
ragdocforge/llm/openai_compatible_provider.py
```

Use `/v1/chat/completions`.

Request:

```json
{
  "model": "MODEL_NAME",
  "messages": [
    {"role": "system", "content": "SYSTEM_PROMPT"},
    {"role": "user", "content": "USER_PROMPT"}
  ],
  "temperature": 0.1,
  "max_tokens": 2048
}
```

Requirements:

```text
- Use API key if provided.
- Support custom base URL.
- Timeout must be configurable.
- Raise controlled provider warnings, not raw stack traces.
- Extract content from choices[0].message.content.
```

---

# 12. Ollama Provider

Implement:

```text
ragdocforge/llm/ollama_provider.py
```

Use Ollama chat endpoint:

```text
POST /api/chat
```

Payload:

```json
{
  "model": "qwen2.5:7b",
  "messages": [
    {"role": "system", "content": "SYSTEM_PROMPT"},
    {"role": "user", "content": "USER_PROMPT"}
  ],
  "stream": false,
  "options": {
    "temperature": 0.1
  }
}
```

Requirements:

```text
- Support custom base URL.
- Timeout configurable.
- Extract message.content.
- Handle unavailable Ollama gracefully.
```

---

# 13. Mock Provider

Implement:

```text
ragdocforge/llm/mock_provider.py
```

This must return valid deterministic sample JSON for tests.

Use this provider in tests so no external service is needed.

---

# 14. Safety and Privacy Requirements

Add UI warning:

```text
Do not upload confidential enterprise documents to a public hosted Space. Use local/private deployment for sensitive documents.
```

LLM warning:

```text
When LLM analysis is enabled, document text may be sent to the selected model provider. Use Ollama for local/private processing.
```

Do not log full document text.

Logs may include:

```text
doc_id
source_file
provider
status
duration
warnings
```

Logs must not include:

```text
raw_text
full prompt
API key
uploaded file content
```

---

# 15. Prompting Requirements

Prompts must instruct the LLM:

```text
- Return only valid JSON.
- Do not include markdown fences.
- Do not invent unsupported facts.
- Use placeholders for missing enterprise-specific details.
- Identify missing information explicitly.
- Treat the source as incomplete unless evidence is present.
- Keep recommendations practical for enterprise RAG.
```

The system prompt should emphasize:

```text
You are analyzing enterprise Oracle EBS support documents for RAG readiness. Your task is to identify whether the document is complete, specific, well-grounded, retrievable, and safe to use as a support knowledge source.
```

---

# 16. LLM Input Construction

Limit document text sent to LLM.

Use:

```text
RAGDOCFORGE_LLM_MAX_DOC_CHARS
```

Default:

```text
20000
```

Input should include:

```text
source_file
detected title
detected ERP module
detected doc type
business process
detected headings
detected tables/views/packages/procedures
deterministic quality report
truncated document text
```

Do not send binary content or file metadata beyond what is needed.

---

# 17. Requirements Update

Update `requirements.txt`:

```text
httpx>=0.27.0
python-dotenv>=1.0.0
```

Do not add heavy ML dependencies.

Do not add:

```text
openai
langchain
llama-index
transformers
torch
sentence-transformers
qdrant-client
```

---

# 18. Tests

Add tests:

```text
tests/test_llm_json_utils.py
tests/test_mock_provider.py
tests/test_llm_document_analyzer.py
tests/test_llm_gap_analyzer.py
tests/test_llm_chunk_analyzer.py
```

## 18.1 JSON Utils Tests

Test:

```text
valid JSON passes
JSON inside markdown fence can be extracted
invalid JSON returns warning
array/object extraction handles surrounding text
```

## 18.2 Mock Provider Tests

Test:

```text
mock provider returns valid document critique JSON
mock provider returns valid suggested sections JSON
mock provider returns valid chunk critique JSON
```

## 18.3 Analyzer Tests

Use mock provider.

Test:

```text
document analyzer returns LLMDocumentCritique
gap analyzer returns list of LLMSuggestedSection
chunk analyzer returns list of LLMChunkCritique
provider failure does not crash batch
validation failure records warning
```

---

# 19. Definition of Done

Slice 2 is complete when:

```text
1. Existing Slice 1 deterministic flow still works with LLM disabled.
2. User can enable LLM qualitative analysis from the UI.
3. User can select disabled, mock, ollama, or openai_compatible provider.
4. Mock provider works without any external service.
5. Ollama provider can call a local Ollama model when configured.
6. OpenAI-compatible provider can call a /v1/chat/completions endpoint when configured.
7. LLM output is validated with Pydantic.
8. Invalid LLM output does not crash the app.
9. UI shows LLM document critique.
10. UI shows suggested missing sections.
11. Chunk preview includes optional LLM critique fields.
12. Export ZIP includes llm_analysis_report.json and suggested_sections.md.
13. Manifest records whether LLM analysis was enabled.
14. Tests pass with pytest.
15. No full document text, prompts, or API keys are logged.
16. No vector DB, embeddings, LangChain, or LlamaIndex dependencies are introduced.
```

---

# 20. Suggested Implementation Order

Implement in this order:

```text
1. Add LLM schemas.
2. Add provider interface.
3. Add mock provider.
4. Add JSON extraction and validation utilities.
5. Add OpenAI-compatible provider.
6. Add Ollama provider.
7. Add prompt templates.
8. Add LLM document analyzer.
9. Add LLM gap analyzer.
10. Add LLM chunk analyzer.
11. Add suggested sections markdown exporter.
12. Extend manifest writer.
13. Extend ZIP exporter.
14. Extend Gradio UI settings.
15. Add LLM Quality Review tab.
16. Add Suggested Sections tab.
17. Add optional LLM critique columns to chunk preview.
18. Add .env.example.
19. Add tests.
20. Run pytest and fix failures.
```

---

# 21. Acceptance Test Scenario

Run:

```bash
python app.py
```

Upload:

```text
examples/sample_sop.md
examples/sample_sql.sql
examples/sample_plsql.pks
```

Test 1: LLM disabled

Expected:

```text
- App behaves like Slice 1.
- No LLM output files are required.
- Manifest says llm_analysis_enabled=false.
```

Test 2: Mock provider enabled

Expected:

```text
- LLM Quality Review tab shows deterministic mock critique.
- Suggested Sections tab shows mock suggested sections.
- Chunk Preview includes mock critique fields.
- ZIP contains llm_analysis_report.json.
- ZIP contains suggested_sections.md.
- Manifest says llm_analysis_enabled=true and llm_provider=mock.
```

Test 3: Ollama provider enabled

Expected if Ollama is running:

```text
- App calls local Ollama endpoint.
- Valid JSON response is parsed.
- Provider errors are shown as warnings, not crashes.
```

Test 4: OpenAI-compatible provider enabled

Expected if endpoint and API key are configured:

```text
- App calls /v1/chat/completions.
- Valid JSON response is parsed.
- Provider errors are shown as warnings, not crashes.
```

