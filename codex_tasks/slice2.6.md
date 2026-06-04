# Codex Task: Slice 2.6 — Metadata Precision Refinement for RAGDocForge

## Project Name

RAGDocForge

## Slice Goal

Refine the metadata precision of the Slice 2.5 implementation.

Slice 2.5 successfully improved metadata quality by adding object extraction hardening, stopword filtering, chunk-level/document-level metadata separation, quality score caps, compact YAML front matter, and metadata sidecar export.

However, the latest generated output still has a few precision issues:

1. `ERR` is incorrectly extracted as a function from prose such as `Function Err Message`.
2. `FND_LOOKUPS` is missed from comma-separated SQL `FROM` clauses such as `FROM apps.gl_interface gi, apps.fnd_lookups fl`.
3. Error metadata mixes clean error codes with long prose/context lines.
4. Full document-level error lists are repeated inside every JSONL chunk, making `chunks.jsonl` too large and noisy.
5. Generic short chunks such as `References` and `Community Discussions` are not clearly marked as low priority.
6. LLM suggested sections now include grounding fields, but evidence mapping is too pessimistic; sections related to explicitly present error codes should be marked evidence-supported.

This slice must make the metadata more precise without adding new heavy dependencies or changing the overall app architecture.

---

# 1. Scope

## 1.1 In Scope

Implement the following:

```text
1. Prevent prose labels from being extracted as PL/SQL functions.
2. Improve SQL object extraction for comma-separated FROM clauses.
3. Split error metadata into error_codes and error_context_lines.
4. Compact repeated doc-level metadata in chunk JSONL.
5. Add low-priority tagging for generic reference/community chunks.
6. Improve LLM suggested-section evidence mapping.
7. Add regression tests for all precision fixes.
```

## 1.2 Out of Scope

Do not implement:

```text
Qdrant
Embeddings
Vector search
RAG chatbot
LangChain
LlamaIndex
OCR
Authentication
Persistent database
New UI framework
Background jobs
```

This is a narrow precision patch.

---

# 2. Files Likely to Modify

Modify or create:

```text
ragdocforge/
  analyzers/
    oracle_object_extractor.py
    metadata_extractor.py
    llm_gap_analyzer.py
    llm_document_analyzer.py
    llm_chunk_analyzer.py

  converters/
    chunker.py
    jsonl_exporter.py
    metadata_sidecar_exporter.py
    suggested_sections_exporter.py
    manifest_writer.py

  schemas/
    document_models.py
    chunk_models.py
    llm_analysis_models.py
    metadata_models.py

tests/
  test_plsql_function_precision.py
  test_sql_comma_from_extraction.py
  test_error_metadata_split.py
  test_jsonl_doc_metadata_compaction.py
  test_chunk_priority_refinement.py
  test_llm_evidence_mapping.py
```

If equivalent files already exist, extend them instead of duplicating logic.

---

# 3. Fix 1 — Prevent `ERR` and Other Prose Labels From Being Extracted as Functions

## 3.1 Current Problem

The app currently extracts:

```text
ERR
```

as a function from prose such as:

```text
Function Err Message
Function warning number
Function return status
```

This is wrong. These are document labels, not PL/SQL function definitions.

## 3.2 Required Behavior

Only extract functions from strong PL/SQL evidence.

Accepted function patterns:

```sql
CREATE OR REPLACE FUNCTION function_name
FUNCTION function_name(...)
FUNCTION function_name RETURN datatype
```

Do not extract from prose patterns like:

```text
Function Err Message
Function warning number
Function return status
Function name description
```

## 3.3 Implementation Requirements

Update:

```text
ragdocforge/analyzers/oracle_object_extractor.py
```

Add a stricter function extraction function:

```python
def extract_plsql_functions(text: str) -> list[OracleObjectCandidate]:
    ...
```

Rules:

```text
1. `CREATE OR REPLACE FUNCTION name` is strong evidence.
2. `FUNCTION name(` is strong evidence.
3. `FUNCTION name RETURN` is strong evidence.
4. `FUNCTION name Message` is not evidence.
5. `FUNCTION name Description` is not evidence.
6. `Function Err Message` must not extract ERR.
7. Function names without underscores are allowed only under strong PL/SQL signature evidence.
```

Add a denylist for prose-label followers after `FUNCTION <word>`:

```python
PROSE_FUNCTION_LABEL_FOLLOWERS = {
    "MESSAGE",
    "DESCRIPTION",
    "NUMBER",
    "STATUS",
    "FIELD",
    "VALUE",
    "NAME",
    "CODE",
    "TEXT",
    "TYPE"
}
```

If the token after the candidate function name is one of those followers and there is no `(` or `RETURN`, reject the candidate.

## 3.4 Acceptance Examples

Should extract:

```sql
CREATE OR REPLACE FUNCTION get_interface_status(p_group_id IN NUMBER)
RETURN VARCHAR2;
```

Expected:

```text
GET_INTERFACE_STATUS
```

Should extract:

```sql
FUNCTION validate_group RETURN BOOLEAN;
```

Expected:

```text
VALIDATE_GROUP
```

Should not extract:

```text
Function Err Message
```

Expected:

```text
No function extracted
```

Should not extract:

```text
Function Return Status
```

Expected:

```text
No function extracted
```

---

# 4. Fix 2 — Extract Comma-Separated SQL FROM Objects

## 4.1 Current Problem

The SQL parser extracts:

```text
GL_INTERFACE
```

from:

```sql
FROM apps.gl_interface gi,
     apps.fnd_lookups fl
```

but misses:

```text
FND_LOOKUPS
```

## 4.2 Required Behavior

Extract all valid table/view objects from comma-separated `FROM` lists.

Examples:

```sql
SELECT *
FROM apps.gl_interface gi,
     apps.fnd_lookups fl
WHERE gi.status = fl.lookup_code;
```

Expected:

```text
GL_INTERFACE
FND_LOOKUPS
```

Another example:

```sql
SELECT *
FROM gl_je_headers h, gl_je_lines l, gl_code_combinations gcc
WHERE h.je_header_id = l.je_header_id;
```

Expected:

```text
GL_JE_HEADERS
GL_JE_LINES
GL_CODE_COMBINATIONS
```

## 4.3 Implementation Requirements

Update:

```text
ragdocforge/analyzers/oracle_object_extractor.py
```

Add:

```python
def extract_from_clause_objects(text: str) -> list[OracleObjectCandidate]:
    ...
```

It must handle:

```text
FROM object alias
FROM schema.object alias
FROM object1 a, object2 b, object3 c
FROM object1, object2
FROM object1 o
JOIN object2 j
```

Stop parsing the `FROM` list when encountering SQL clause keywords:

```python
FROM_CLAUSE_TERMINATORS = {
    "WHERE", "GROUP", "ORDER", "HAVING", "UNION", "INTERSECT",
    "MINUS", "CONNECT", "START", "MODEL", "FETCH", "FOR"
}
```

Ignore subqueries for now, but do not crash:

```sql
FROM (
  SELECT ...
) x,
gl_interface gi
```

If subquery parsing is not supported, skip subquery block and still extract following valid tables when feasible.

## 4.4 Avoid Alias False Positives

From:

```sql
FROM apps.gl_interface gi,
     apps.fnd_lookups fl
```

Extract:

```text
GL_INTERFACE
FND_LOOKUPS
```

Do not extract aliases:

```text
GI
FL
```

From:

```sql
FROM gl_je_headers h
```

Extract:

```text
GL_JE_HEADERS
```

Do not extract:

```text
H
```

---

# 5. Fix 3 — Split Error Metadata Into Error Codes and Error Context Lines

## 5.1 Current Problem

The app currently stores both clean error codes and long prose messages in one `error_messages` field.

Examples of clean error codes:

```text
FRM-41830
APP-00268
ORA-00054
```

Examples of context/prose lines:

```text
CONCURRENT MANAGER ENCOUNTERED AN ERROR WHILE RUNNING SQL*PLUS...
CHECK THE DATABASE FOR INVALID OBJECTS...
IF THE DATA IS INVALID IT WILL NOT BE IMPORTED...
```

Both are useful, but they should not be treated the same.

## 5.2 Required Schema Changes

Update relevant schemas:

```text
ragdocforge/schemas/document_models.py
ragdocforge/schemas/chunk_models.py
ragdocforge/schemas/metadata_models.py
```

Add:

```python
error_codes: list[str] = []
error_context_lines: list[str] = []
```

Keep `error_messages` temporarily for backward compatibility, but treat it as deprecated.

Recommended compatibility behavior:

```text
error_messages = error_codes + error_context_lines
```

or expose it only in output where older code expects it.

## 5.3 Extraction Rules

Add or update:

```python
def extract_error_metadata(text: str) -> ErrorMetadata:
    ...
```

Create model:

```python
class ErrorMetadata(BaseModel):
    error_codes: list[str] = []
    error_context_lines: list[str] = []
```

### Error Codes

Extract code patterns:

```regex
\b(?:ORA|FRM|APP|REP|PLS|FND|FORM)-\d{3,6}\b
```

Normalize:

```text
Uppercase
Deduplicate
Preserve order of first appearance
```

Examples:

```text
ORA-00054
FRM-41830
APP-00268
REP-1419
PLS-00306
```

### Error Context Lines

Extract lines that contain useful failure context but are not just a code.

Triggers:

```text
completed with error
completed with warning
concurrent manager encountered an error
invalid object
not imported
failed
exception
unable to
cannot
ORA-
FRM-
APP-
REP-
PLS-
```

Rules:

```text
1. Keep line length between 15 and 300 characters.
2. Normalize whitespace.
3. Exclude pure headings like "Error" or "Warning".
4. Exclude duplicate lines.
5. If a line contains an error code plus message, keep full line in error_context_lines and code in error_codes.
```

Example:

```text
FRM-41830: List of Values contains no entries.
```

Expected:

```json
{
  "error_codes": ["FRM-41830"],
  "error_context_lines": ["FRM-41830: List of Values contains no entries."]
}
```

## 5.4 Output Updates

Update:

```text
metadata_sidecar.json
chunks.jsonl
quality_report.json
manifest.json if applicable
markdown extracted metadata section
UI chunk preview if applicable
```

Use:

```text
error_codes
error_context_lines
```

rather than only `error_messages`.

---

# 6. Fix 4 — Compact Repeated Doc-Level Metadata in Chunk JSONL

## 6.1 Current Problem

Every chunk currently repeats the full document-level object and error metadata. This makes `chunks.jsonl` large and noisy, especially when a document has many error context lines.

## 6.2 Required Behavior

Keep chunk-level metadata fully explicit.

Compact document-level metadata in each chunk.

Preferred structure:

```json
{
  "chunk_id": "journal_import_errors_0007",
  "doc_id": "journal_import_errors",
  "source_file": "journal_import_errors.md",
  "text": "...",
  "metadata": {
    "erp_module": "GL",
    "doc_type": "TROUBLESHOOTING_NOTE",
    "business_process": "Journal Import",
    "section": "Solution",
    "rag_priority": "high",
    "metadata_confidence": 0.92,
    "doc_level": {
      "metadata_ref": "metadata_sidecar.json#journal_import_errors",
      "tables_count": 4,
      "packages_count": 0,
      "procedures_count": 0,
      "functions_count": 0,
      "error_codes_count": 12,
      "error_context_lines_count": 95,
      "keywords_count": 20,
      "top_tables": ["GL_INTERFACE", "FND_LOOKUPS"],
      "top_error_codes": ["FRM-41830", "APP-00268", "ORA-00054"]
    },
    "chunk_level": {
      "tables": ["GL_INTERFACE"],
      "packages": [],
      "procedures": [],
      "functions": [],
      "error_codes": ["FRM-41830"],
      "error_context_lines": ["FRM-41830: List of Values contains no entries."],
      "keywords": ["group_id", "lookup_code"]
    }
  }
}
```

## 6.3 Configurable Full Metadata Option

Add an export option constant or setting:

```python
INCLUDE_FULL_DOC_METADATA_IN_CHUNKS = False
```

Default must be:

```text
False
```

If true, include full doc-level lists as before. But the default ZIP output must use compact doc-level metadata.

## 6.4 Sidecar Becomes Source of Full Metadata

`metadata_sidecar.json` must contain full document-level metadata.

`chunks.jsonl` should reference it through:

```text
metadata_sidecar.json#{doc_id}
```

---

# 7. Fix 5 — Add Low Priority for Generic Short Reference/Community Chunks

## 7.1 Current Problem

Some generic short chunks are structurally valid but low value for RAG answer generation.

Examples:

```text
References
Community Discussions
Related Links
Appendix
External Resources
```

These should not be removed, but should be marked lower priority.

## 7.2 Required Behavior

Add `rag_priority = "low"` for chunks whose section/title or text indicates generic reference material.

Create helper:

```python
def infer_chunk_rag_priority(chunk_text: str, section: str | None, chunk_metadata: dict) -> str:
    ...
```

Priority values:

```text
high
medium
low
```

## 7.3 Priority Rules

Set `high` when chunk contains:

```text
- SQL code block with valid Oracle objects
- Error code plus resolution/cause/action
- Diagnostic steps
- Validation steps
- Procedure steps
- Troubleshooting decision logic
```

Set `medium` for normal explanatory content.

Set `low` when section/title is one of:

```python
GENERIC_LOW_PRIORITY_SECTIONS = {
    "REFERENCES",
    "REFERENCE",
    "COMMUNITY DISCUSSIONS",
    "RELATED LINKS",
    "EXTERNAL RESOURCES",
    "APPENDIX",
    "SEE ALSO",
    "ADDITIONAL INFORMATION"
}
```

Also set low when:

```text
- Chunk has fewer than 80 tokens
- No chunk-level objects
- No error codes
- No procedure/action keywords
- Section is generic
```

Do not set low if the short chunk contains an error code or SQL block.

---

# 8. Fix 6 — Improve LLM Suggested-Section Evidence Mapping

## 8.1 Current Problem

LLM suggestions include grounding fields but often mark everything as:

```text
evidence_supported: false
requires_sme_confirmation: true
confidence: high
```

This is safe but loses useful distinction.

If a suggested section is about an error code actually present in the source, then the suggestion should be partially evidence-supported.

Example source contains:

```text
FRM-41830: List of Values contains no entries.
```

Suggested section:

```text
Specific Error Code Analysis - FRM-41830
```

Expected:

```json
{
  "evidence_supported": true,
  "requires_sme_confirmation": true,
  "source_evidence": [
    "FRM-41830: List of Values contains no entries."
  ],
  "confidence": "medium"
}
```

The existence of the error is evidence-supported. The proposed remediation may still require SME confirmation.

## 8.2 Implementation Requirements

Add post-processing after LLM suggested sections are generated.

Create:

```python
def enrich_suggested_sections_with_evidence(
    suggested_sections: list[LLMSuggestedSection],
    parsed_document: ParsedDocument,
    metadata_sidecar_entry: dict | None = None,
) -> list[LLMSuggestedSection]:
    ...
```

Rules:

```text
1. If section_title or suggested_content mentions an error code present in parsed_document.error_codes, set evidence_supported=true.
2. Add matching context lines from parsed_document.error_context_lines to source_evidence.
3. If section is a missing standard section inferred from absence, keep evidence_supported=false.
4. Operational recommendations should keep requires_sme_confirmation=true.
5. If evidence_supported=true but remediation details are inferred, confidence should usually be medium, not high.
6. If the source directly contains both the error and clear resolution text, confidence may be high.
```

## 8.3 Standard Missing Sections

For generic missing sections such as:

```text
Validation Steps
Rollback and Recovery Procedures
Performance Tuning Recommendations
Configuration Options
Security Validation Best Practices
```

Default:

```json
{
  "evidence_supported": false,
  "requires_sme_confirmation": true,
  "confidence": "medium"
}
```

## 8.4 Suggested Sections Markdown Export

Update `suggested_sections.md` so evidence-supported sections clearly show evidence.

Example:

```markdown
### High: Specific Error Code Analysis - FRM-41830

Confidence: medium  
Evidence supported: true  
Requires SME confirmation: true  

Source evidence:
- FRM-41830: List of Values contains no entries.

Reason needed:
The source mentions FRM-41830 but does not provide complete cause, resolution, and validation guidance.

Suggested draft content:
...
```

---

# 9. Metadata Sidecar Updates

Update:

```text
ragdocforge/converters/metadata_sidecar_exporter.py
```

Sidecar should include:

```json
{
  "documents": [
    {
      "doc_id": "journal_import_errors",
      "source_file": "journal_import_errors.md",
      "title": "Journal Import Errors",
      "erp_module": "GL",
      "doc_type": "TROUBLESHOOTING_NOTE",
      "business_process": "Journal Import",
      "metadata_confidence": 0.91,
      "oracle_objects": {
        "tables": [
          {
            "name": "GL_INTERFACE",
            "confidence": 0.9,
            "evidence_type": "sql_from",
            "evidence": "FROM apps.gl_interface"
          },
          {
            "name": "FND_LOOKUPS",
            "confidence": 0.9,
            "evidence_type": "sql_from",
            "evidence": "FROM apps.fnd_lookups"
          }
        ],
        "packages": [],
        "procedures": [],
        "functions": []
      },
      "error_codes": [
        "FRM-41830",
        "APP-00268",
        "ORA-00054"
      ],
      "error_context_lines": [
        "FRM-41830: List of Values contains no entries.",
        "APP-00268: Unable to find period.",
        "ORA-00054: resource busy and acquire with NOWAIT specified."
      ],
      "keywords": [
        "journal import",
        "group_id",
        "accounting period"
      ]
    }
  ]
}
```

Keep candidate confidence/evidence for Oracle objects.

---

# 10. Manifest Updates

Update manifest with Slice 2.6 metadata:

```json
{
  "metadata_precision_refinement_enabled": true,
  "error_metadata_mode": "split_error_codes_and_context_lines",
  "chunk_doc_metadata_mode": "compact_ref_with_counts",
  "include_full_doc_metadata_in_chunks": false,
  "llm_evidence_postprocessing_enabled": true
}
```

For each document entry, include:

```json
{
  "doc_id": "journal_import_errors",
  "error_codes_count": 12,
  "error_context_lines_count": 95,
  "doc_level_metadata_ref": "metadata_sidecar.json#journal_import_errors"
}
```

---

# 11. UI Updates

Keep UI changes minimal.

## 11.1 Document Analysis Tab

Add or update columns:

```text
error_codes_count
error_context_lines_count
tables_count
functions_count
metadata_confidence
```

## 11.2 Chunk Preview Tab

Show:

```text
chunk_error_codes
chunk_error_context_lines_preview
chunk_tables
chunk_functions
rag_priority
metadata_confidence
doc_metadata_ref
```

Do not display huge doc-level error lists in the dataframe.

## 11.3 LLM Suggested Sections Tab

Show:

```text
priority
section_title
confidence
evidence_supported
requires_sme_confirmation
source_evidence
reason_needed
suggested_content
```

---

# 12. Tests

## 12.1 Test: PL/SQL Function Precision

Create:

```text
tests/test_plsql_function_precision.py
```

Test:

```python
def test_function_err_message_not_extracted():
    text = "Function Err Message"
    result = extract_oracle_objects(text)
    assert "ERR" not in result.functions
```

Also test:

```text
Function Return Status
Function Warning Number
```

Positive test:

```sql
CREATE OR REPLACE FUNCTION get_interface_status(p_group_id IN NUMBER)
RETURN VARCHAR2 IS
BEGIN
  RETURN 'VALID';
END;
```

Expected:

```text
GET_INTERFACE_STATUS
```

---

## 12.2 Test: SQL Comma FROM Extraction

Create:

```text
tests/test_sql_comma_from_extraction.py
```

Test:

```sql
SELECT gi.status, fl.meaning
FROM apps.gl_interface gi,
     apps.fnd_lookups fl
WHERE gi.status = fl.lookup_code;
```

Expected tables:

```text
GL_INTERFACE
FND_LOOKUPS
```

Also test:

```sql
SELECT *
FROM gl_je_headers h, gl_je_lines l, gl_code_combinations gcc
```

Expected:

```text
GL_JE_HEADERS
GL_JE_LINES
GL_CODE_COMBINATIONS
```

Ensure aliases are not extracted:

```text
GI
FL
H
L
GCC
```

---

## 12.3 Test: Error Metadata Split

Create:

```text
tests/test_error_metadata_split.py
```

Input:

```text
FRM-41830: List of Values contains no entries.
APP-00268: Unable to find period.
Concurrent Manager encountered an error while running SQL*Plus.
If the data is invalid it will not be imported.
```

Expected:

```text
error_codes:
- FRM-41830
- APP-00268

error_context_lines:
- FRM-41830: List of Values contains no entries.
- APP-00268: Unable to find period.
- Concurrent Manager encountered an error while running SQL*Plus.
- If the data is invalid it will not be imported.
```

---

## 12.4 Test: JSONL Doc Metadata Compaction

Create:

```text
tests/test_jsonl_doc_metadata_compaction.py
```

Expected chunk JSONL metadata:

```text
metadata.doc_level.metadata_ref exists
metadata.doc_level.error_context_lines_count exists
metadata.doc_level.top_error_codes exists
metadata.doc_level.error_context_lines full list does not exist by default
metadata.chunk_level.error_context_lines exists
```

Confirm:

```text
include_full_doc_metadata_in_chunks defaults to false
```

---

## 12.5 Test: Chunk Priority Refinement

Create:

```text
tests/test_chunk_priority_refinement.py
```

Test low priority:

```markdown
## References

Oracle General Ledger User Guide.
Community discussion thread.
```

Expected:

```text
rag_priority = low
```

Test not low priority:

```markdown
## FRM-41830

FRM-41830: List of Values contains no entries.

Resolution:
Validate the lookup setup and rerun the process.
```

Expected:

```text
rag_priority = high or medium, not low
```

Test SQL block:

````markdown
```sql
SELECT * FROM gl_interface WHERE group_id = :group_id;
````

````

Expected:

```text
rag_priority = high or medium, not low
````

---

## 12.6 Test: LLM Evidence Mapping

Create:

```text
tests/test_llm_evidence_mapping.py
```

Input parsed document has:

```text
error_codes = ["FRM-41830"]
error_context_lines = ["FRM-41830: List of Values contains no entries."]
```

Suggested section:

```text
Specific Error Code Analysis - FRM-41830
```

Expected:

```text
evidence_supported = true
requires_sme_confirmation = true
source_evidence contains FRM-41830 line
confidence = medium unless direct resolution exists
```

Generic suggested section:

```text
Rollback and Recovery Procedures
```

Expected:

```text
evidence_supported = false
requires_sme_confirmation = true
confidence = medium
```

---

# 13. Acceptance Criteria

Slice 2.6 is complete when:

```text
1. `ERR` is no longer extracted as a function from “Function Err Message”.
2. Valid PL/SQL functions are still extracted from strong signatures.
3. `FND_LOOKUPS` is extracted from comma-separated FROM clauses.
4. Aliases such as GI, FL, H, L, GCC are not extracted as objects.
5. Error metadata is split into error_codes and error_context_lines.
6. metadata_sidecar.json contains full error_codes and error_context_lines.
7. chunks.jsonl uses compact doc-level metadata references by default.
8. Full document-level error lists are not repeated in every chunk by default.
9. Chunk-level metadata still contains local error codes/context lines where present.
10. Generic reference/community chunks are marked rag_priority=low.
11. Error-code and SQL chunks are not incorrectly downgraded to low.
12. LLM suggested sections referencing present error codes are marked evidence_supported=true.
13. Generic missing-section suggestions remain evidence_supported=false.
14. suggested_sections.md displays evidence fields clearly.
15. Manifest includes Slice 2.6 metadata flags.
16. Existing Slice 1, 2, and 2.5 tests still pass.
17. All new Slice 2.6 tests pass.
```

---

# 14. Suggested Implementation Order

Implement in this order:

```text
1. Add error metadata schema/model with error_codes and error_context_lines.
2. Update error extraction to split codes and context lines.
3. Add tests for error metadata split.
4. Harden function extraction to reject prose labels like Function Err Message.
5. Add tests for PL/SQL function precision.
6. Improve FROM clause extraction for comma-separated table lists.
7. Add tests for comma-separated FROM extraction and alias rejection.
8. Update ParsedDocument and RagChunk models with error_codes/error_context_lines.
9. Update metadata sidecar exporter.
10. Update chunker to populate chunk-local error_codes and error_context_lines.
11. Update JSONL exporter to compact doc-level metadata with metadata_ref/counts/top lists.
12. Add tests for JSONL compaction.
13. Add chunk rag_priority inference for generic reference/community chunks.
14. Add tests for chunk priority refinement.
15. Add LLM suggested section evidence post-processor.
16. Update suggested sections markdown exporter.
17. Add tests for LLM evidence mapping.
18. Update manifest writer with Slice 2.6 flags.
19. Update minimal UI columns.
20. Run full pytest suite and fix regressions.
```

---

# 15. Manual Validation Scenario

Use a test document named:

```text
journal_import_errors.md
```

Containing:

````markdown
# Summary

Function Err Message should not become a PL/SQL function.

```sql
SELECT gi.status, fl.meaning
FROM apps.gl_interface gi,
     apps.fnd_lookups fl
WHERE gi.status = fl.lookup_code;
````

FRM-41830: List of Values contains no entries.
APP-00268: Unable to find period.
ORA-00054: resource busy and acquire with NOWAIT specified.

## References

Oracle General Ledger User Guide.
Community Discussions.

````

Expected output:

```text
Title:
Journal Import Errors

Tables:
GL_INTERFACE
FND_LOOKUPS

Functions:
No ERR function

Error codes:
FRM-41830
APP-00268
ORA-00054

Error context lines:
Full lines containing those errors

chunks.jsonl:
metadata.doc_level.metadata_ref exists
metadata.doc_level counts exist
metadata.chunk_level contains only local metadata

References chunk:
rag_priority=low

Suggested section for FRM-41830:
evidence_supported=true
requires_sme_confirmation=true
source_evidence contains the FRM-41830 line
````

---

# 16. Design Principle

Prefer precision over recall.

For this tool, bad metadata is worse than missing metadata. Downstream RAG systems will use Oracle table names, package names, error codes, and module metadata for routing, filtering, reranking, and answer grounding. Therefore:

```text
Do not include uncertain object names as authoritative retrieval metadata.
```

When uncertain, place information in context text or sidecar notes rather than high-confidence metadata fields.
