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

# RAGDocForge

RAGDocForge is a lightweight Gradio application for preparing enterprise documents for high-quality RAG ingestion. It focuses on deterministic parsing, Oracle EBS metadata extraction, RAG-readiness scoring, structured markdown conversion, JSONL chunk generation, and exportable review artifacts.

Supported content includes SOPs, SQL, PL/SQL, Oracle EBS notes, functional designs, technical designs, troubleshooting notes, and FAQs.

## Features

- Multi-file upload and bundled sample-file workflow.
- PDF, DOCX, TXT, MD, SQL, and PL/SQL-style parsing.
- Oracle EBS metadata extraction with hardened object filtering.
- SQL and PL/SQL object detection, including comma-separated `FROM` clauses and strict function signatures.
- Split error metadata with `error_codes` and `error_context_lines`.
- Deterministic RAG-readiness scoring with raw score, final capped score, readiness level, and cap reasons.
- RAG-ready markdown conversion.
- JSONL chunk generation with separate `metadata.doc_level` and `metadata.chunk_level`.
- Optional LLM qualitative analysis through `disabled`, `mock`, `ollama`, or `openai_compatible` providers.
- Hugging Face Spaces-ready Gradio UI with public-demo mode.
- ZIP export with manifest, sidecar metadata, quality report, chunks, suggested sections, and output README.

## Privacy

Do not upload confidential documents to a public Space. Use local/private deployment for sensitive enterprise content.

When LLM analysis is enabled, document content may be sent to the selected provider. Use Ollama for local/private processing, or keep the provider set to `disabled`/`mock` for public demos.

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Run tests and Spaces checks:

```bash
python -m pytest -q
python scripts/verify_spaces_ready.py
```

## Hugging Face Spaces Deployment

1. Create a new Hugging Face Space.
2. Choose the Gradio SDK.
3. Upload the repository files.
4. Set `RAGDOCFORGE_PUBLIC_DEMO_MODE=true` in Space variables.
5. Keep `RAGDOCFORGE_LLM_PROVIDER=disabled` or `mock` for public demos.

The root `app.py` imports `demo` from `ragdocforge.app`, so the app works with both `python app.py` and Hugging Face Spaces.

## Public Demo Mode

Enable:

```bash
RAGDOCFORGE_PUBLIC_DEMO_MODE=true
```

Public demo mode:

- Shows a public-demo badge and prominent privacy warning.
- Defaults the LLM provider to a safe public mode.
- Hides the API key field by default.
- Enforces upload count and per-file size limits.
- Avoids persistent uploaded document storage.
- Keeps raw document text, prompts, and API keys out of logs.

## Provider Configuration

Copy `.env.example` to `.env` for local/private use.

```bash
RAGDOCFORGE_LLM_PROVIDER=disabled
RAGDOCFORGE_LLM_PROVIDER=mock
RAGDOCFORGE_LLM_PROVIDER=ollama
RAGDOCFORGE_LLM_PROVIDER=openai_compatible
```

Ollama:

```bash
RAGDOCFORGE_OLLAMA_BASE_URL=http://localhost:11434
RAGDOCFORGE_OLLAMA_MODEL=qwen2.5:7b
```

OpenAI-compatible endpoint:

```bash
RAGDOCFORGE_OPENAI_BASE_URL=https://api.openai.com/v1
RAGDOCFORGE_OPENAI_API_KEY=
RAGDOCFORGE_OPENAI_MODEL=gpt-4.1-mini
```

## Sample Workflow

The UI includes:

- Load Sample SOP
- Load Sample SQL
- Load Sample PL/SQL
- Load All Samples

Bundled examples live in `examples/`:

- `sample_gl_journal_import_sop.md`
- `sample_gl_diagnostic_sql.sql`
- `sample_custom_plsql_package.pks`
- `sample_low_quality_note.txt`

Reference artifacts live in `demo_outputs/`.

## ZIP Output Layout

Downloaded ZIP files use:

```text
ragdocforge_outputs/
  markdown/
  chunks.jsonl
  quality_report.json
  metadata_sidecar.json
  llm_analysis_report.json
  suggested_sections.md
  output_summary.md
  manifest.json
  README_OUTPUTS.md
```

`chunks.jsonl` is ready for later RAG ingestion. It stores compact document-level references in `metadata.doc_level` and local chunk retrieval metadata in `metadata.chunk_level`.

## Limitations

- No OCR in the current slice.
- No vector DB ingestion yet.
- No embeddings yet.
- No RAG chatbot yet.
- PDF extraction quality depends on embedded text.
- LLM suggestions should be reviewed by a human.

## License

Apache-2.0
