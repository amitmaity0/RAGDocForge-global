# Codex Task: Slice 1 — Deterministic MVP for RAGDocForge

## Project Name

RAGDocForge

## Slice Goal

Build the first deterministic MVP of a standalone Gradio-based Python application that analyzes uploaded enterprise documents and converts them into RAG-ready artifacts.

This slice must not require any LLM provider. It should use deterministic parsing, metadata extraction, heuristic scoring, markdown conversion, chunking, and ZIP export.

The app should support Oracle EBS-style documents such as SOPs, SQL scripts, PL/SQL files, functional designs, technical designs, troubleshooting notes, FAQs, and Oracle documentation.

The final app must run locally using:

```bash
python app.py
```

It should also be deployable later to Hugging Face Spaces with a simple `app.py`, `requirements.txt`, and `README.md`.

---

# 1. Core Functional Requirements

## 1.1 Gradio Web UI

Implement a Gradio `Blocks` application with the following tabs:

### Tab 1: Upload & Settings

Fields:

* Multi-file upload
* Optional ERP module selector
* Optional document type selector
* Optional business process text input
* Chunk size input
* Chunk overlap input
* Analyze button

Supported ERP modules:

```text
GL
AP
AR
PO
INV
OM
HRMS
FA
CM
SYSADMIN
GENERIC
UNKNOWN
```

Supported document types:

```text
SOP
SQL
PLSQL
ORACLE_DOC
FUNCTIONAL_DESIGN
TECHNICAL_DESIGN
TROUBLESHOOTING_NOTE
FAQ
UNKNOWN
```

Supported file extensions:

```text
.pdf
.docx
.txt
.md
.sql
.pls
.pkb
.pks
```

### Tab 2: Document Analysis

Display:

* Uploaded file list
* Detected document type
* Detected ERP module
* Extracted title
* Extracted headings
* Extracted Oracle objects
* Extracted SQL tables/views
* Extracted PL/SQL packages/procedures/functions
* Extracted error messages
* Quality score
* Strengths
* Blocking issues
* Warnings

### Tab 3: RAG Markdown Preview

Display converted markdown output for selected document.

The markdown must include YAML front matter.

### Tab 4: Chunk Preview

Display chunk table with:

```text
chunk_id
doc_id
source_file
section
erp_module
doc_type
token_estimate
tables
packages
procedures
error_messages
text_preview
```

### Tab 5: Export

Provide downloadable files:

```text
cleaned markdown files
chunks.jsonl
quality_report.json
manifest.json
all_outputs.zip
```

---

# 2. Required Project Structure

Create the following structure:

```text
ragdocforge/
  app.py
  requirements.txt
  README.md

  ragdocforge/
    __init__.py

    schemas/
      __init__.py
      document_models.py
      quality_models.py
      chunk_models.py
      export_models.py

    parsers/
      __init__.py
      base_parser.py
      pdf_parser.py
      docx_parser.py
      text_parser.py
      sql_parser.py
      parser_router.py

    analyzers/
      __init__.py
      metadata_extractor.py
      document_classifier.py
      quality_scorer.py
      oracle_object_extractor.py
      gap_analyzer.py

    converters/
      __init__.py
      markdown_converter.py
      chunker.py
      jsonl_exporter.py
      manifest_writer.py
      zip_exporter.py

    utils/
      __init__.py
      file_utils.py
      text_utils.py
      token_utils.py
      logging_utils.py

  tests/
    test_text_parser.py
    test_sql_parser.py
    test_metadata_extractor.py
    test_quality_scorer.py
    test_chunker.py

  examples/
    sample_sop.md
    sample_sql.sql
    sample_plsql.pks
```

---

# 3. Data Models

Use `pydantic` models.

## 3.1 ParsedDocument

Create in:

```text
ragdocforge/schemas/document_models.py
```

Model:

```python
class ParsedDocument(BaseModel):
    doc_id: str
    source_file: str
    file_extension: str
    raw_text: str
    title: str | None = None
    headings: list[str] = []
    detected_erp_module: str = "UNKNOWN"
    detected_doc_type: str = "UNKNOWN"
    user_erp_module: str | None = None
    user_doc_type: str | None = None
    business_process: str | None = None
    tables: list[str] = []
    views: list[str] = []
    packages: list[str] = []
    procedures: list[str] = []
    functions: list[str] = []
    concurrent_programs: list[str] = []
    error_messages: list[str] = []
    keywords: list[str] = []
    warnings: list[str] = []
```

## 3.2 QualityReport

Create in:

```text
ragdocforge/schemas/quality_models.py
```

Model:

```python
class QualityDimensionScore(BaseModel):
    name: str
    score: int
    max_score: int = 5
    explanation: str

class QualityReport(BaseModel):
    doc_id: str
    source_file: str
    overall_score: int
    readiness_level: str
    dimensions: list[QualityDimensionScore]
    strengths: list[str]
    blocking_issues: list[str]
    warnings: list[str]
    recommended_actions: list[str]
    missing_sections: list[str]
```

Readiness levels:

```text
EXCELLENT
GOOD
NEEDS_IMPROVEMENT
POOR
NOT_RAG_READY
```

## 3.3 RagChunk

Create in:

```text
ragdocforge/schemas/chunk_models.py
```

Model:

```python
class RagChunk(BaseModel):
    chunk_id: str
    doc_id: str
    source_file: str
    text: str
    section: str | None = None
    erp_module: str
    doc_type: str
    business_process: str | None = None
    token_estimate: int
    tables: list[str] = []
    views: list[str] = []
    packages: list[str] = []
    procedures: list[str] = []
    functions: list[str] = []
    concurrent_programs: list[str] = []
    error_messages: list[str] = []
    keywords: list[str] = []
    rag_priority: str = "medium"
```

---

# 4. Parser Requirements

## 4.1 Parser Router

Create:

```text
ragdocforge/parsers/parser_router.py
```

It must select parser based on file extension.

Unsupported files should not crash the batch. Return a clear warning.

## 4.2 PDF Parser

Create:

```text
ragdocforge/parsers/pdf_parser.py
```

Use `pymupdf` if available.

Requirements:

* Extract text page by page.
* Preserve page breaks with markers:

```text
<!-- page: 1 -->
```

* If text extraction fails, return a warning.
* Do not implement OCR in Slice 1.

## 4.3 DOCX Parser

Create:

```text
ragdocforge/parsers/docx_parser.py
```

Use `python-docx`.

Extract:

* Paragraph text
* Heading-style paragraphs if available
* Tables as markdown-style rows where feasible

## 4.4 TXT / MD Parser

Create:

```text
ragdocforge/parsers/text_parser.py
```

Requirements:

* Read UTF-8 with fallback to latin-1
* Preserve markdown headings
* Normalize line endings

## 4.5 SQL / PL/SQL Parser

Create:

```text
ragdocforge/parsers/sql_parser.py
```

Requirements:

* Read file as text
* Extract likely:

  * table names
  * view names
  * package names
  * procedure names
  * function names
  * bind variables
  * DML/DDL risk indicators

Detect risky statements:

```text
INSERT
UPDATE
DELETE
MERGE
DROP
TRUNCATE
ALTER
CREATE
GRANT
REVOKE
EXECUTE IMMEDIATE
```

This slice does not need to block risky SQL, but it must flag them in warnings.

---

# 5. Metadata Extraction

Create:

```text
ragdocforge/analyzers/metadata_extractor.py
```

Extract:

## 5.1 Title

Detection order:

1. First markdown heading
2. First DOCX heading
3. First non-empty line under 120 characters
4. Filename stem fallback

## 5.2 Headings

Detect headings from:

```text
# Markdown headings
ALL CAPS lines
Numbered headings like 1. Overview, 2.1 Setup
Common document headings
```

Common heading names:

```text
Purpose
Scope
Overview
Prerequisites
Procedure
Steps
Setup
Troubleshooting
Known Issues
Resolution
Validation
SQL
Diagnostic SQL
Rollback
References
Appendix
```

## 5.3 ERP Module Detection

Use deterministic keyword mapping.

Example:

```python
ERP_MODULE_KEYWORDS = {
    "GL": [
        "general ledger",
        "journal import",
        "gl_interface",
        "gl_je_headers",
        "gl_je_lines",
        "ledger",
        "accounting period",
        "chart of accounts"
    ],
    "AP": [
        "accounts payable",
        "invoice workbench",
        "ap_invoices_all",
        "payment batch",
        "supplier invoice"
    ],
    "AR": [
        "accounts receivable",
        "ra_customer_trx_all",
        "receipt",
        "customer transaction"
    ],
    "PO": [
        "purchase order",
        "po_headers_all",
        "po_lines_all",
        "requisition"
    ],
    "INV": [
        "inventory",
        "mtl_system_items",
        "onhand quantity",
        "material transaction"
    ],
    "OM": [
        "order management",
        "oe_order_headers_all",
        "sales order",
        "order line"
    ],
    "HRMS": [
        "per_all_people_f",
        "assignment",
        "payroll",
        "employee"
    ]
}
```

If multiple modules match, choose the highest count and store secondary module candidates in keywords or warnings.

## 5.4 Document Type Detection

Use deterministic rules:

```text
.sql extension -> SQL
.pks/.pkb/.pls -> PLSQL
Contains CREATE OR REPLACE PACKAGE -> PLSQL
Contains SELECT ... FROM heavily -> SQL
Contains step/procedure/prerequisite/validation -> SOP
Contains BR100/MD050/functional requirement -> FUNCTIONAL_DESIGN
Contains technical design/interface/package/table mapping -> TECHNICAL_DESIGN
Contains error/resolution/root cause/symptom -> TROUBLESHOOTING_NOTE
Contains Q:/A: or FAQ -> FAQ
Contains Oracle documentation style terms -> ORACLE_DOC
```

Manual user-selected values should override detected values.

---

# 6. Oracle Object Extraction

Create:

```text
ragdocforge/analyzers/oracle_object_extractor.py
```

Extract with regex and normalization.

## 6.1 Tables and Views

Patterns:

```text
FROM table_name
JOIN table_name
UPDATE table_name
INTO table_name
DELETE FROM table_name
MERGE INTO table_name
```

Oracle object names may include:

```text
GL_INTERFACE
AP_INVOICES_ALL
PO_HEADERS_ALL
XX_CUSTOM_TABLE
schema.table_name
```

Normalize to uppercase and deduplicate.

## 6.2 Packages

Patterns:

```text
CREATE OR REPLACE PACKAGE package_name
CREATE OR REPLACE PACKAGE BODY package_name
package_name.procedure_name
```

## 6.3 Procedures

Patterns:

```text
CREATE OR REPLACE PROCEDURE procedure_name
PROCEDURE procedure_name
```

## 6.4 Functions

Patterns:

```text
CREATE OR REPLACE FUNCTION function_name
FUNCTION function_name
```

## 6.5 Error Messages

Extract lines containing:

```text
ORA-
FRM-
APP-
REP-
Concurrent Manager
completed with error
completed with warning
invalid
failed
exception
```

Keep error lines under reasonable length.

---

# 7. Quality Scoring

Create:

```text
ragdocforge/analyzers/quality_scorer.py
```

The score must be deterministic and explainable.

## 7.1 Dimensions

Each dimension gets 0–5.

### Dimension 1: Metadata Completeness

Score based on presence of:

```text
title
erp_module
doc_type
business_process
source_file
tables/packages/procedures when applicable
```

### Dimension 2: Chunkability

Score based on:

```text
headings present
reasonable section lengths
not one giant paragraph
markdown/doc structure exists
```

### Dimension 3: Retrieval Specificity

Score based on presence of:

```text
Oracle object names
error messages
business process terms
module-specific terms
specific parameters
concurrent program names
```

### Dimension 4: Operational Usefulness

Score based on:

```text
steps
actions
diagnostics
expected results
validation
troubleshooting
```

### Dimension 5: Grounding Quality

Score based on:

```text
source filename
section names
explicit examples
SQL snippets
screens/navigation references
```

### Dimension 6: Procedure Completeness

Score based on:

```text
purpose
scope
prerequisites
procedure
validation
rollback
known issues
```

### Dimension 7: SQL Safety and Context

For SQL/PLSQL docs, score based on:

```text
read-only indicators
bind variables explained
DML/DDL warnings
purpose/context
expected output
```

For non-SQL docs, score neutral unless SQL exists inside the document.

### Dimension 8: Ambiguity Risk

Higher score means lower ambiguity.

Score based on:

```text
clear title
clear module
clear audience
clear process
few vague references like "run this", "check the table", "fix issue"
```

## 7.2 Overall Score

Calculate:

```python
overall_score = round(sum(dimension_scores) / max_possible * 100)
```

## 7.3 Readiness Level

```text
90–100: EXCELLENT
75–89: GOOD
60–74: NEEDS_IMPROVEMENT
40–59: POOR
0–39: NOT_RAG_READY
```

## 7.4 Blocking Issue Rules

Add blocking issues for:

```text
raw_text too short
no title
unknown ERP module
unknown document type
no headings and text length > 1500 chars
SQL file with no detected tables/views/packages
SOP-like document with no procedure/steps
troubleshooting-like document with no resolution/validation
```

## 7.5 Recommended Actions

Generate deterministic recommendations.

Examples:

```text
Add ERP module and business process metadata.
Add a Purpose section.
Add a Prerequisites section.
Add Validation SQL or expected result checks.
Add error-message variants users may search for.
Add table/view glossary.
Add bind parameter explanations for SQL.
Add expected output interpretation.
Split long sections with descriptive headings.
Add rollback or recovery steps.
```

---

# 8. RAG Markdown Conversion

Create:

```text
ragdocforge/converters/markdown_converter.py
```

Each document should be converted to markdown with YAML front matter.

Example output:

```markdown
---
doc_id: gl_journal_import_errors_v1
title: GL Journal Import Error Troubleshooting
source_file: JournalImport.pdf
erp_module: GL
doc_type: SOP
business_process: Journal Import
rag_priority: high
tables:
  - GL_INTERFACE
  - GL_JE_HEADERS
packages: []
procedures: []
error_messages:
  - "Journal Import completed with error"
---

# GL Journal Import Error Troubleshooting

## Source Summary

- Source file: JournalImport.pdf
- ERP module: GL
- Document type: SOP
- Business process: Journal Import

## Extracted Oracle Objects

### Tables and Views

- GL_INTERFACE
- GL_JE_HEADERS

## Original Content

...
```

Requirements:

* Preserve meaningful headings.
* Normalize whitespace.
* Avoid deleting source content.
* Add extracted metadata sections before original content.
* Include warnings if document quality is poor.

---

# 9. Chunking

Create:

```text
ragdocforge/converters/chunker.py
```

## 9.1 Chunking Strategy

Use deterministic heading-aware chunking.

Priority:

1. Split by markdown headings.
2. If section too large, split by paragraphs.
3. If paragraph too large, split by approximate token count.
4. Preserve overlap.

Default values:

```text
chunk_size_tokens = 700
chunk_overlap_tokens = 100
```

Token estimator can be approximate:

```python
token_estimate = max(1, len(text.split()) * 1.3)
```

No hard dependency on `tiktoken` in Slice 1.

## 9.2 Chunk Metadata

Each chunk must inherit document-level metadata:

```text
doc_id
source_file
erp_module
doc_type
business_process
tables
views
packages
procedures
functions
concurrent_programs
error_messages
keywords
```

If a section contains a specific table or error message, include it in that chunk metadata.

## 9.3 Chunk ID Format

```text
{doc_id}_{chunk_index:04d}
```

Example:

```text
gl_journal_import_errors_v1_0001
```

---

# 10. JSONL Export

Create:

```text
ragdocforge/converters/jsonl_exporter.py
```

Output one JSON object per line.

File:

```text
chunks.jsonl
```

Each line should serialize one `RagChunk`.

---

# 11. Manifest Export

Create:

```text
ragdocforge/converters/manifest_writer.py
```

Generate:

```text
manifest.json
```

Fields:

```json
{
  "batch_id": "timestamp_or_uuid",
  "created_at": "ISO timestamp",
  "documents_processed": 3,
  "documents_failed": 0,
  "chunks_created": 42,
  "supported_file_types": [".pdf", ".docx", ".txt", ".md", ".sql", ".pls", ".pkb", ".pks"],
  "outputs": {
    "markdown_dir": "markdown/",
    "chunks_jsonl": "chunks.jsonl",
    "quality_report": "quality_report.json"
  },
  "documents": [
    {
      "doc_id": "example_doc_v1",
      "source_file": "example.pdf",
      "erp_module": "GL",
      "doc_type": "SOP",
      "quality_score": 78,
      "chunks_created": 12
    }
  ]
}
```

---

# 12. ZIP Export

Create:

```text
ragdocforge/converters/zip_exporter.py
```

The ZIP should contain:

```text
markdown/
  doc1.md
  doc2.md

chunks.jsonl
quality_report.json
manifest.json
```

Use Python `zipfile`.

Temporary output directories should be created safely using `tempfile`.

---

# 13. Gradio Behavior

## 13.1 Analyze Button

When user clicks Analyze:

1. Create temporary working directory.
2. Save uploaded files to working directory.
3. Parse each file.
4. Extract metadata.
5. Classify document.
6. Extract Oracle objects.
7. Score quality.
8. Convert to markdown.
9. Create chunks.
10. Generate JSONL.
11. Generate quality report.
12. Generate manifest.
13. Generate ZIP.
14. Update all UI tabs.

## 13.2 Error Handling

One bad document must not fail the full batch.

For failed documents:

* Record failure in manifest.
* Show warning in UI.
* Continue processing remaining documents.

## 13.3 Output UI

Return:

* Analysis dataframe
* Quality report JSON
* Markdown preview
* Chunk dataframe
* Downloadable ZIP file

---

# 14. Requirements

Create `requirements.txt`:

```text
gradio>=5.0.0
pydantic>=2.0.0
python-docx>=1.1.0
pymupdf>=1.24.0
sqlparse>=0.5.0
pandas>=2.0.0
pyyaml>=6.0.0
pytest>=8.0.0
```

Avoid heavy ML dependencies in Slice 1.

Do not add:

```text
torch
transformers
sentence-transformers
qdrant-client
openai
langchain
llama-index
```

Those are for later slices.

---

# 15. README Requirements

Create a practical `README.md`.

Include:

```text
Project overview
Features
Supported file types
Local install
Run command
Example workflow
Output artifact description
Limitations of Slice 1
Hugging Face Spaces readiness note
Privacy warning
```

Privacy warning:

```text
Do not upload confidential enterprise documents to a public hosted Space. This app is intended for local/private use unless deployed in a secured environment.
```

---

# 16. Tests

Implement tests using `pytest`.

## 16.1 Parser Tests

Test:

```text
TXT parser reads simple text
MD parser preserves headings
SQL parser extracts tables
PLSQL parser extracts package/procedure/function names
Unsupported extension returns controlled warning
```

## 16.2 Metadata Tests

Test:

```text
title extraction from heading
ERP module detection for GL_INTERFACE
document type detection for SQL file
document type detection for SOP-like text
```

## 16.3 Quality Scorer Tests

Test:

```text
well-structured SOP scores higher than unstructured text
SQL with table names scores higher than SQL without context
missing ERP module creates warning/blocking issue
```

## 16.4 Chunker Tests

Test:

```text
heading-aware splitting
chunk overlap
chunk metadata inheritance
unique chunk IDs
JSONL serialization
```

---

# 17. Definition of Done

Slice 1 is complete when:

```text
1. python app.py starts the Gradio app successfully.
2. User can upload multiple supported files.
3. App parses PDF, DOCX, TXT, MD, SQL, PLS/PKB/PKS files.
4. App displays document analysis table.
5. App displays deterministic quality score and issues.
6. App generates RAG-ready markdown with YAML front matter.
7. App generates chunk preview.
8. App exports ZIP containing markdown files, chunks.jsonl, quality_report.json, and manifest.json.
9. One bad file does not fail the full batch.
10. Tests pass with pytest.
11. No LLM dependency exists in Slice 1.
12. requirements.txt remains lightweight and Hugging Face Spaces-friendly.
```

---

# 18. Important Constraints

Do not implement the following in Slice 1:

```text
LLM rewriting
OpenAI/Ollama/Hugging Face API calls
Qdrant ingestion
Embeddings
Semantic similarity scoring
OCR
Authentication
User accounts
Persistent storage
Database backend
Background jobs
Advanced UI theming
```

These belong to later slices.

---

# 19. Suggested Implementation Order

Implement in this exact order:

```text
1. Create project structure.
2. Add pydantic schemas.
3. Implement text parser.
4. Implement SQL/PLSQL parser.
5. Implement DOCX parser.
6. Implement PDF parser.
7. Implement parser router.
8. Implement Oracle object extractor.
9. Implement metadata extractor.
10. Implement document classifier.
11. Implement quality scorer.
12. Implement markdown converter.
13. Implement chunker.
14. Implement JSONL exporter.
15. Implement manifest writer.
16. Implement ZIP exporter.
17. Implement Gradio app.
18. Add tests.
19. Add README.
20. Run pytest and fix failures.
```

---

# 20. Example Acceptance Test Scenario

Create sample files:

```text
examples/sample_sop.md
examples/sample_sql.sql
examples/sample_plsql.pks
```

Run:

```bash
python app.py
```

Upload the sample files.

Expected result:

```text
- All files are processed.
- GL module is detected for GL_INTERFACE content.
- SQL document type is detected for .sql file.
- PLSQL document type is detected for .pks/.pkb file.
- Quality scores are displayed.
- Markdown preview contains YAML front matter.
- chunks.jsonl contains one JSON object per chunk.
- all_outputs.zip downloads successfully.
- pytest passes.
```

