
he application should do **three things**:

1.  **Analyze document quality**
2.  **Convert documents into RAG-ready structured markdown/JSONL**
3.  **Suggest missing content to improve retrieval and answer quality**

Hugging Face Spaces is a reasonable hosting target. Spaces supports Gradio apps for hosted ML demos, and Gradio provides file upload components and a flexible `Blocks` API for custom multi-tab apps.

## Recommended product design

Call it something like:

**RAGDocForge — Enterprise RAG Document Optimizer**

or for your EBS niche:

**EBS RAG Document Forge**

The app should support:

```
Input:- PDF- DOCX- TXT- MD- SQL- PL/SQL- CSV / XLSX laterOutput:- Clean RAG markdown- Chunked JSONL- Metadata manifest- Quality score report- Gap analysis report- Suggested improvements- Optional Qdrant ingestion preview
```

## Core workflow

### 1. Upload document set

Use Gradio `File` with multiple uploads. Gradio’s file component supports generic file uploads and can return uploaded file paths to Python.

The UI should allow the user to choose:

```
ERP Module:- GL- AP- AR- PO- INV- OM- HRMS- GenericDocument Type:- SOP- SQL- PL/SQL Package- Functional Design- Technical Design- Oracle Documentation- Troubleshooting Note- FAQ- Runbook- Error Catalog
```

### 2. Extract raw content

Codex should implement separate parsers:

```
PDF       -> pymupdf / pypdfDOCX      -> python-docxTXT/MD    -> direct readSQL/PLSQL -> sqlparse + regex metadata extractionHTML      -> beautifulsoup4, optionalXLSX      -> openpyxl, later
```

For PDFs, I would avoid OCR in v1 unless needed. Start with text extraction, then add OCR fallback later.

### 3. Classify document structure

The app should detect:

```
- Title- Module- Business process- Document type- Source system- Tables/views/packages mentioned- Concurrent programs- Error messages- Parameters- Setup steps- Resolution steps- Validation SQL- Assumptions- Prerequisites- Warnings- Known gaps
```

### 4. Score document quality

Use a scoring rubric, not just a generic LLM summary.

Example dimensions:

Dimension

Score

Meaning

Chunkability

0–5

Can this be split cleanly?

Metadata completeness

0–5

Does it identify module, process, object names?

Operational usefulness

0–5

Can support engineers act on it?

Retrieval specificity

0–5

Does it contain searchable terms/errors/tables?

Grounding quality

0–5

Does it include source evidence and examples?

Procedure completeness

0–5

Are steps, prerequisites, and validation included?

SQL safety/context

0–5

Are SQL purpose, inputs, risk, and expected output clear?

Ambiguity risk

0–5

Lower ambiguity = higher score

Then output:

```
{  "overall_score": 78,  "rag_readiness": "good_but_needs_metadata",  "blocking_issues": [    "Missing ERP module metadata",    "SQL queries lack purpose and expected output",    "Troubleshooting section has symptoms but no validation steps"  ],  "recommended_actions": [    "Add error-message variants",    "Add expected concurrent request statuses",    "Add table/view glossary",    "Add safe read-only SQL examples"  ]}
```

## RAG-ready output format

Your converted document should not just be “cleaned text.” It should become structured source-backed markdown.

Example:

```
---doc_id: gl_journal_import_errors_v1title: GL Journal Import Error Troubleshootingerp_module: GLbusiness_process: Journal Importdoc_type: sopsource_file: JournalImport.pdfsource_section: Import Error Handlingversion: 1.0owner: supportrag_priority: hightags:  - journal import  - GL_INTERFACE  - GL_JE_HEADERS  - concurrent program  - period not open---# GL Journal Import Error Troubleshooting## PurposeUse this document to diagnose and resolve Oracle EBS General Ledger Journal Import errors.## When to useUse when Journal Import completes with warning/error or imported journals are not visible in the expected ledger/period.## Key Oracle Objects| Object | Type | Purpose ||---|---|---|| GL_INTERFACE | Table | Staging table for journal import || GL_JE_HEADERS | Table | Journal header table || GL_JE_LINES | Table | Journal lines table |## Common Symptoms### Symptom: Journal Import completed with errorsPossible causes:- Invalid accounting period- Invalid ledger- Invalid account combination- Missing required interface columns## Diagnostic SQL```sqlSELECT status, request_id, group_id, set_of_books_id, accounting_dateFROM gl_interfaceWHERE group_id = :group_id;
```

Expected result:

-   `STATUS` should indicate import state.
-   Rows with error status require review of interface error columns or import log.

## Resolution Steps

1.  Confirm ledger and period.
2.  Validate accounting date.
3.  Check invalid code combinations.
4.  Rerun Journal Import after correction.

## Validation

Confirm records are created in:

-   GL_JE_HEADERS
-   GL_JE_LINES

```
This format is far better for retrieval than raw PDF text.## Chunk JSONL outputFor ingestion, generate one JSON object per chunk:```json{  "chunk_id": "gl_journal_import_errors_v1_0004",  "doc_id": "gl_journal_import_errors_v1",  "text": "Diagnostic SQL for Journal Import errors...",  "metadata": {    "erp_module": "GL",    "doc_type": "sop",    "business_process": "Journal Import",    "source_file": "JournalImport.pdf",    "section": "Diagnostic SQL",    "tables": ["GL_INTERFACE", "GL_JE_HEADERS", "GL_JE_LINES"],    "keywords": ["journal import", "group_id", "request_id"],    "rag_priority": "high"  }}
```

This will plug directly into your existing Qdrant ingestion pipeline later.

## Content improvement suggestions should be category-specific

The app should not give generic advice like “add more details.” It should produce targeted missing-content recommendations.

### For SOP documents

Check for:

```
- Purpose- Scope- Prerequisites- Step-by-step procedure- Decision points- Screens/navigation- Expected result- Failure scenarios- Validation SQL- Rollback/recovery steps- Owner/version/date
```

### For SQL documents

Check for:

```
- Business purpose- Required bind parameters- Read-only vs DML risk- Tables/views used- ERP module- Expected row count- Expected output interpretation- Example question this SQL answers- Safety notes
```

### For Oracle docs

Check for:

```
- Is it too generic?- Is module/context explicit?- Does it include your local EBS setup/version?- Does it map Oracle terminology to support questions?- Does it contain examples from your environment?
```

### For design documents

Check for:

```
- Business process- Functional flow- Technical components- Tables/packages/interfaces- Concurrent programs- Dependencies- Error handling- Support diagnostics- Known customizations
```

## Recommended Gradio app tabs

Use Gradio `Blocks`, because it gives better layout control than a simple `Interface`. Gradio’s `Blocks` API is intended for custom layouts, multi-step flows, and event-driven apps.

```
Tab 1: Upload & Settings- File upload- ERP module- Document type- Target output format- LLM provider settingsTab 2: Document Analysis- Extracted text preview- Detected metadata- Quality score- Issues tableTab 3: RAG Conversion- Clean markdown output- Chunk preview- Metadata previewTab 4: Improvement Suggestions- Missing sections- Recommended additions- Suggested SQL/context additions- Example rewritten sectionsTab 5: Export- Download markdown- Download JSONL chunks- Download quality report- Download manifest
```

## Suggested architecture

```
ragdocforge/  app.py  requirements.txt  README.md  ragdocforge/    parsers/      pdf_parser.py      docx_parser.py      text_parser.py      sql_parser.py    analyzers/      document_classifier.py      metadata_extractor.py      quality_scorer.py      gap_analyzer.py      sql_context_analyzer.py    converters/      markdown_converter.py      chunker.py      jsonl_exporter.py      manifest_writer.py    llm/      provider.py      openai_provider.py      ollama_provider.py      hf_provider.py    schemas/      document_models.py      quality_models.py      chunk_models.py    prompts/      classify_document.md      analyze_quality.md      suggest_improvements.md      rewrite_rag_markdown.md    utils/      file_utils.py      token_utils.py      logging_utils.py  examples/    sample_sop.md    sample_sql.sql  tests/    test_parsers.py    test_chunker.py    test_quality_scorer.py
```

## Important design decision

Do **not** make the LLM responsible for everything.

Use deterministic code for:

```
- File parsing- Section detection- SQL object extraction- Chunk splitting- Metadata schema validation- Score calculation- Export generation
```

Use the LLM for:

```
- Document classification- Ambiguity detection- Missing-content suggestions- Rewriting into cleaner RAG markdown- Generating examples- Summarizing document purpose
```

That gives you repeatability and prevents hallucinated structure.

## LLM provider strategy

For your local version:

```
Provider 1: Ollama- qwen2.5 / qwen3 / gemma3- Good for local private documentsProvider 2: OpenAI-compatible API- Best quality for hosted/private deploymentProvider 3: Hugging Face Inference API- Optional for Spaces
```

For Hugging Face public service, be careful with private EBS documents. Public users may upload sensitive documents, so the app should show a warning and ideally avoid storing files permanently.

## Hugging Face deployment structure

For a Gradio Space, use:

```
app.pyrequirements.txtREADME.md
```

Hugging Face Spaces supports Gradio SDK configuration through the Space metadata, and additional dependencies are typically installed from `requirements.txt`.

Example `README.md` header:

```
---title: RAGDocForgeemoji: 📄colorFrom: bluecolorTo: indigosdk: gradiosdk_version: 5.0.0app_file: app.pypinned: falselicense: apache-2.0---
```

You may need to adjust the Gradio version based on current HF runtime compatibility. Build errors on Spaces are commonly caused by dependency installation failures, missing app files, import errors, or the app failing to start cleanly.

## MVP feature list for Codex

Build v1 with these features:

```
1. Multi-file upload2. Parse PDF, DOCX, MD, TXT, SQL3. Detect document type4. Extract metadata5. Score RAG readiness6. Generate structured markdown7. Generate JSONL chunks8. Generate quality report9. Generate improvement suggestions10. Download ZIP output11. Run locally and on Hugging Face Spaces
```

Avoid adding vector DB, login, OCR, or Qdrant ingestion in v1. Those can be v2.

## What the quality analyzer should flag

Examples:

```
Critical:- No clear module or business process- No source/object metadata- SQL has DML/DDL risk- Procedure lacks validation- Document is too generic for support useHigh:- Missing error messages- Missing screenshots/navigation- Missing expected output- Missing bind parameter explanations- Missing troubleshooting decision treeMedium:- Long sections need splitting- Duplicate boilerplate- Weak title- Inconsistent terminologyLow:- Formatting cleanup- Add glossary- Add tags
```
