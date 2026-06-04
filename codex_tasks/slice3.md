# Codex Task: Slice 3 — Hugging Face Spaces Packaging + Public Demo Polish for RAGDocForge

## Project Name

RAGDocForge

## Slice Goal

Prepare the existing RAGDocForge Gradio application for a polished Hugging Face Spaces deployment and public demo experience.

Slices 1 and 2 already provide:

* Deterministic document parsing
* RAG quality scoring
* Markdown conversion
* JSONL chunk generation
* ZIP export
* Optional LLM qualitative analysis
* Mock/Ollama/OpenAI-compatible LLM providers

Slice 3 must make the project suitable for public demo use on Hugging Face Spaces while preserving local/private usability.

This slice focuses on:

1. Hugging Face Spaces compatibility
2. Public demo UX polish
3. Example document workflow
4. Safer public-hosted behavior
5. Lightweight dependency validation
6. Documentation polish
7. Deployment verification
8. Demo screenshots and sample outputs

---

# 1. Important Scope Rules

## 1.1 Do Not Add RAG Runtime Yet

Do not implement:

```text
Qdrant
Embeddings
Vector search
RAG chatbot
Document ingestion into vector stores
LangChain
LlamaIndex
Background ingestion jobs
Persistent database
Authentication
User accounts
```

Those belong to later slices.

## 1.2 Public Demo Must Be Safe by Default

The hosted Hugging Face Space must default to:

```text
LLM Provider: disabled
```

or:

```text
LLM Provider: mock
```

Do not require API keys for the public demo.

The public Space should demonstrate analysis, conversion, chunking, and mock qualitative review without sending uploaded content to external providers.

## 1.3 Preserve Local Advanced Mode

Local/private users should still be able to use:

```text
Ollama
OpenAI-compatible endpoint
```

through environment variables or UI fields, as implemented in Slice 2.

---

# 2. Required Deployment Files

Ensure the root project contains:

```text
app.py
requirements.txt
README.md
.env.example
LICENSE
```

## 2.1 Root `app.py`

The root `app.py` must be Hugging Face Spaces-compatible.

It should:

```python
from ragdocforge.app import demo

if __name__ == "__main__":
    demo.launch()
```

or equivalent.

The Gradio app object should be named:

```text
demo
```

inside:

```text
ragdocforge/app.py
```

This keeps app startup compatible with both:

```bash
python app.py
```

and Hugging Face Spaces.

## 2.2 requirements.txt

Keep requirements lightweight.

Allowed:

```text
gradio>=5.0.0
pydantic>=2.0.0
python-docx>=1.1.0
pymupdf>=1.24.0
sqlparse>=0.5.0
pandas>=2.0.0
pyyaml>=6.0.0
pytest>=8.0.0
python-dotenv>=1.0.0
httpx>=0.27.0
```

Do not add:

```text
torch
transformers
sentence-transformers
qdrant-client
langchain
llama-index
openai
opencv-python
faiss
```

## 2.3 README Hugging Face Metadata

Update the top of `README.md` with Spaces metadata:

```yaml
---
title: RAGDocForge
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
---
```

Adjust `sdk_version` to match the installed Gradio version if needed.

## 2.4 LICENSE

Add:

```text
Apache-2.0
```

unless an existing license is already present.

---

# 3. Public Demo Mode

Add a public demo mode controlled by environment variable:

```bash
RAGDOCFORGE_PUBLIC_DEMO_MODE=true
```

Default behavior:

```text
false locally
true when explicitly set in Hugging Face Space
```

When public demo mode is enabled:

```text
- Show strong privacy warning.
- Default LLM provider to mock or disabled.
- Hide or collapse API key fields by default.
- Disable persistent storage.
- Disable writing uploaded raw documents outside temporary directories.
- Prevent full raw document text from appearing in logs.
- Limit max upload size if feasible.
- Limit max files per batch if feasible.
- Limit max characters sent to LLM analysis.
```

Recommended limits:

```bash
RAGDOCFORGE_MAX_FILES_PER_BATCH=5
RAGDOCFORGE_MAX_UPLOAD_MB_PER_FILE=10
RAGDOCFORGE_LLM_MAX_DOC_CHARS=12000
RAGDOCFORGE_LLM_MAX_CHUNKS_TO_REVIEW=8
```

If a limit is exceeded, show a controlled UI warning instead of crashing.

---

# 4. UI Polish Requirements

Update the Gradio UI to feel like a public product demo.

## 4.1 Header

Add a clear header:

```text
RAGDocForge — Enterprise RAG Document Quality Analyzer
```

Subtitle:

```text
Upload SOPs, SQL, PL/SQL, Oracle EBS notes, and design documents. Analyze RAG readiness, convert to structured markdown, generate JSONL chunks, and receive improvement suggestions.
```

## 4.2 Privacy Warning

Add a visible warning near upload:

```text
Privacy warning: Do not upload confidential enterprise documents to a public hosted demo. Use local/private deployment for sensitive files.
```

If LLM is enabled:

```text
LLM warning: When LLM analysis is enabled, document content may be sent to the selected provider. Use Ollama for local/private processing.
```

## 4.3 Public Demo Badge

If `RAGDOCFORGE_PUBLIC_DEMO_MODE=true`, show:

```text
Public Demo Mode Enabled
```

Also show:

```text
This Space is for demonstration with sample or non-confidential documents only.
```

## 4.4 Example Buttons

Add buttons:

```text
Load Sample SOP
Load Sample SQL
Load Sample PL/SQL
Load All Samples
```

These should populate the workflow using bundled example files from:

```text
examples/
```

The user should be able to run the full workflow without uploading any file.

## 4.5 Better Result Summary

After analysis, show a concise summary panel:

```text
Documents processed: 3
Documents failed: 0
Chunks created: 42
Average quality score: 76
Readiness: GOOD
LLM analysis: mock
Export ZIP: ready
```

## 4.6 Quality Score Visualization

Add a simple table or dataframe with:

```text
source_file
doc_type
erp_module
quality_score
readiness_level
blocking_issues_count
warnings_count
chunks_created
```

Do not add heavy charting dependencies.

## 4.7 Empty State UX

Before analysis, each output tab should show clear empty-state text:

```text
Upload documents or load sample files, then click Analyze.
```

## 4.8 Controlled Error UX

If file parsing fails:

```text
- Show the file name.
- Show a short error message.
- Continue processing other files.
- Do not expose stack traces in the UI by default.
```

Add optional developer/debug mode:

```bash
RAGDOCFORGE_DEBUG=true
```

If debug is true, allow expanded exception details in logs or UI.

---

# 5. Example Documents

Create or improve bundled example files.

Directory:

```text
examples/
  sample_gl_journal_import_sop.md
  sample_gl_diagnostic_sql.sql
  sample_custom_plsql_package.pks
  sample_low_quality_note.txt
```

## 5.1 Sample SOP

Must include:

```text
GL module
Journal Import process
Purpose
Scope
Prerequisites
Procedure
Diagnostic SQL
Validation
Known Errors
Rollback/Recovery
References
```

## 5.2 Sample SQL

Must include:

```sql
SELECT ...
FROM gl_interface
WHERE group_id = :group_id
```

Include comments describing:

```text
purpose
bind variables
expected output
safety/read-only status
```

## 5.3 Sample PL/SQL

Must include:

```sql
CREATE OR REPLACE PACKAGE xxgl_journal_diag_pkg AS
  PROCEDURE diagnose_group(p_group_id IN NUMBER);
  FUNCTION get_interface_status(p_group_id IN NUMBER) RETURN VARCHAR2;
END xxgl_journal_diag_pkg;
/
```

## 5.4 Low-Quality Note

Create intentionally weak text to demonstrate scoring:

```text
Journal import is broken. Check the table and rerun it. Sometimes period issue. Fix data.
```

This should score significantly lower than the SOP.

---

# 6. Sample Output Artifacts

Create:

```text
demo_outputs/
  sample_quality_report.json
  sample_manifest.json
  sample_chunks.jsonl
  sample_suggested_sections.md
```

These should be generated from bundled examples or manually created to match the schema.

Purpose:

```text
- README documentation
- Demo validation
- Regression reference
```

Do not include confidential data.

---

# 7. README Improvements

Update README to include:

## 7.1 Clear Positioning

```text
RAGDocForge is a lightweight Gradio application for preparing enterprise documents for high-quality RAG ingestion.
```

Mention supported document types:

```text
SOPs
SQL
PL/SQL
Oracle EBS notes
Functional designs
Technical designs
Troubleshooting notes
FAQs
```

## 7.2 Feature List

Include:

```text
- Multi-file upload
- PDF/DOCX/TXT/MD/SQL/PLSQL parsing
- Oracle EBS metadata extraction
- SQL/PLSQL object detection
- Deterministic RAG-readiness scoring
- RAG-ready markdown conversion
- JSONL chunk generation
- Optional LLM qualitative analysis
- ZIP export
- Hugging Face Spaces-ready Gradio UI
```

## 7.3 Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 7.4 Hugging Face Spaces Deployment

Explain:

```text
1. Create a new Hugging Face Space.
2. Choose Gradio SDK.
3. Upload repository files.
4. Set RAGDOCFORGE_PUBLIC_DEMO_MODE=true in Space secrets/variables.
5. Keep LLM provider disabled or mock for public demo.
```

## 7.5 Provider Configuration

Document:

```text
disabled
mock
ollama
openai_compatible
```

Include `.env.example`.

## 7.6 Privacy Warning

Add:

```text
Do not upload confidential documents to a public Space. Use local/private deployment for sensitive enterprise content.
```

## 7.7 Limitations

Mention:

```text
- No OCR in current slice
- No vector DB ingestion yet
- No embeddings yet
- No RAG chatbot yet
- PDF extraction quality depends on embedded text
- LLM suggestions should be reviewed by a human
```

---

# 8. Environment Configuration

Update `.env.example`:

```bash
# Runtime mode
RAGDOCFORGE_PUBLIC_DEMO_MODE=false
RAGDOCFORGE_DEBUG=false

# Upload limits
RAGDOCFORGE_MAX_FILES_PER_BATCH=5
RAGDOCFORGE_MAX_UPLOAD_MB_PER_FILE=10

# LLM provider
RAGDOCFORGE_LLM_PROVIDER=disabled

# OpenAI-compatible endpoint
RAGDOCFORGE_OPENAI_BASE_URL=https://api.openai.com/v1
RAGDOCFORGE_OPENAI_API_KEY=
RAGDOCFORGE_OPENAI_MODEL=gpt-4.1-mini

# Ollama
RAGDOCFORGE_OLLAMA_BASE_URL=http://localhost:11434
RAGDOCFORGE_OLLAMA_MODEL=qwen2.5:7b

# LLM runtime safety
RAGDOCFORGE_LLM_TIMEOUT_SECONDS=60
RAGDOCFORGE_LLM_MAX_DOC_CHARS=12000
RAGDOCFORGE_LLM_MAX_CHUNKS_TO_REVIEW=8
```

---

# 9. Internal Runtime Settings Module

Create:

```text
ragdocforge/config.py
```

Use this for centralized runtime settings.

Example model:

```python
from pydantic import BaseModel

class AppSettings(BaseModel):
    public_demo_mode: bool = False
    debug: bool = False
    max_files_per_batch: int = 5
    max_upload_mb_per_file: int = 10
    llm_provider: str = "disabled"
    llm_timeout_seconds: int = 60
    llm_max_doc_chars: int = 12000
    llm_max_chunks_to_review: int = 8
```

Load from environment using `os.getenv`.

Do not fail if `.env` is missing.

---

# 10. File Handling Hardening

Ensure uploaded files are handled safely.

Requirements:

```text
- Sanitize uploaded filenames.
- Do not trust original file paths.
- Copy files into a temporary work directory.
- Delete temporary work directories after processing if possible.
- Keep only generated outputs needed for Gradio downloads.
- Prevent path traversal such as ../../secret.txt.
- Enforce allowed extensions.
- Enforce max files per batch.
- Enforce per-file size limit if file size is available.
```

Create or update:

```text
ragdocforge/utils/file_utils.py
```

Functions:

```python
def sanitize_filename(filename: str) -> str:
    ...

def is_allowed_extension(filename: str) -> bool:
    ...

def validate_upload_batch(files: list, settings: AppSettings) -> list[str]:
    ...

def safe_copy_upload_to_workdir(upload_file, workdir: Path) -> Path:
    ...
```

---

# 11. Logging Hardening

Update:

```text
ragdocforge/utils/logging_utils.py
```

Requirements:

```text
- Log structured status messages.
- Do not log raw document text.
- Do not log full prompts.
- Do not log API keys.
- Include doc_id, source_file, status, warnings_count, duration.
- Debug mode may include exception type and short message, but not full document content.
```

---

# 12. Export Improvements

Ensure ZIP filenames are stable and safe.

ZIP structure:

```text
ragdocforge_outputs/
  markdown/
    sample_gl_journal_import_sop.md
    sample_gl_diagnostic_sql.md
    sample_custom_plsql_package.md
    sample_low_quality_note.md

  chunks.jsonl
  quality_report.json
  llm_analysis_report.json
  suggested_sections.md
  manifest.json
```

Add a `README_OUTPUTS.md` inside the ZIP explaining:

```text
- What each file contains
- How to use chunks.jsonl for RAG ingestion
- How to review suggested_sections.md
```

Create:

```text
ragdocforge/converters/output_readme_writer.py
```

---

# 13. CI / Local Verification

Add a lightweight local verification script:

```text
scripts/verify_spaces_ready.py
```

This script should check:

```text
- app.py exists at repo root
- requirements.txt exists
- README.md exists
- README has HF metadata header
- examples directory exists
- no banned dependencies in requirements.txt
- importing app.py does not fail
- demo object exists
```

Command:

```bash
python scripts/verify_spaces_ready.py
```

Add this to README.

Optional: add GitHub Actions later, but do not require it in this slice.

---

# 14. Tests

Add or update tests:

```text
tests/test_config.py
tests/test_file_utils.py
tests/test_public_demo_mode.py
tests/test_examples.py
tests/test_zip_structure.py
```

## 14.1 Config Tests

Test:

```text
defaults load correctly
env vars override defaults
boolean env parsing works
integer env parsing works
missing .env does not fail
```

## 14.2 File Utility Tests

Test:

```text
sanitize filename removes path traversal
unsupported extension rejected
max files limit enforced
safe copy preserves only sanitized basename
```

## 14.3 Public Demo Mode Tests

Test:

```text
public demo mode defaults LLM provider safely
API key field is not required
sample files can be loaded
upload limits are enforced
```

## 14.4 Example Tests

Test:

```text
all example files exist
examples process successfully through deterministic pipeline
low-quality note scores lower than sample SOP
sample SQL detects GL_INTERFACE
sample PL/SQL detects package/procedure/function
```

## 14.5 ZIP Structure Tests

Test generated ZIP contains:

```text
ragdocforge_outputs/markdown/
ragdocforge_outputs/chunks.jsonl
ragdocforge_outputs/quality_report.json
ragdocforge_outputs/manifest.json
ragdocforge_outputs/README_OUTPUTS.md
```

If LLM enabled with mock provider, test ZIP also contains:

```text
ragdocforge_outputs/llm_analysis_report.json
ragdocforge_outputs/suggested_sections.md
```

---

# 15. Hugging Face Spaces Runtime Notes

The app should not assume local disk persistence.

Requirements:

```text
- Use temp directories.
- Avoid long-running background tasks.
- Avoid multiprocessing unless necessary.
- Avoid large memory usage.
- Avoid loading ML models at import time.
- Avoid network calls during startup.
- App should import quickly.
```

The Gradio app should be constructed at import time, but expensive processing should only happen when user clicks Analyze.

---

# 16. Definition of Done

Slice 3 is complete when:

```text
1. `python app.py` starts the app locally.
2. Root `app.py` exposes the Gradio app correctly for Hugging Face Spaces.
3. README has valid Hugging Face Spaces metadata.
4. Public demo mode can be enabled with `RAGDOCFORGE_PUBLIC_DEMO_MODE=true`.
5. Public demo mode defaults to disabled or mock LLM provider.
6. UI displays privacy warning and public demo badge.
7. User can load bundled sample files without uploading anything.
8. Sample files process successfully.
9. Low-quality sample scores lower than the full SOP sample.
10. Export ZIP includes README_OUTPUTS.md.
11. Upload filenames are sanitized.
12. Unsupported file types and oversized batches are rejected gracefully.
13. Logs do not include raw document text, prompts, or API keys.
14. `python scripts/verify_spaces_ready.py` passes.
15. `pytest` passes.
16. requirements.txt contains no banned heavy dependencies.
17. No vector DB, embeddings, RAG chatbot, auth, or persistent DB is added.
```

---

# 17. Suggested Implementation Order

Implement in this order:

```text
1. Add central config module.
2. Add/update root app.py for Spaces compatibility.
3. Add public demo mode settings.
4. Harden file utilities.
5. Add upload batch validation.
6. Add public demo UI header, warning, and badge.
7. Add sample files.
8. Add sample loading buttons.
9. Add result summary panel.
10. Improve empty-state UI.
11. Improve controlled error messages.
12. Add ZIP README_OUTPUTS.md.
13. Update ZIP structure.
14. Add demo_outputs sample artifacts.
15. Update README with HF metadata and full documentation.
16. Add LICENSE.
17. Add .env.example updates.
18. Add verify_spaces_ready.py.
19. Add tests.
20. Run pytest and verify script.
```

---

# 18. Acceptance Test Scenario

## Test A: Local Startup

Run:

```bash
python app.py
```

Expected:

```text
- Gradio app starts.
- Header shows RAGDocForge.
- Upload tab displays privacy warning.
- LLM provider defaults to disabled unless configured otherwise.
```

## Test B: Public Demo Mode

Run:

```bash
RAGDOCFORGE_PUBLIC_DEMO_MODE=true python app.py
```

Expected:

```text
- Public Demo Mode badge appears.
- LLM provider defaults to disabled or mock.
- API key fields are not required.
- Privacy warning is prominent.
```

## Test C: Sample Workflow

Click:

```text
Load All Samples
Analyze
```

Expected:

```text
- All bundled examples process successfully.
- SOP receives higher score than low-quality note.
- SQL detects GL_INTERFACE.
- PL/SQL detects package/procedure/function.
- Chunks are generated.
- ZIP is downloadable.
```

## Test D: Export ZIP

Download ZIP.

Expected ZIP structure:

```text
ragdocforge_outputs/
  markdown/
  chunks.jsonl
  quality_report.json
  manifest.json
  README_OUTPUTS.md
```

If mock LLM is enabled:

```text
ragdocforge_outputs/
  llm_analysis_report.json
  suggested_sections.md
```

## Test E: Spaces Verification

Run:

```bash
python scripts/verify_spaces_ready.py
```

Expected:

```text
spaces_ready_status=passed
```

## Test F: Tests

Run:

```bash
pytest
```

Expected:

```text
All tests pass.
```

