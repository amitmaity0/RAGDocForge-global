
## Remaining minor issues

This is now good enough to proceed, but I would still note a few refinements.

### 1. Some table names may be false positives or low-confidence

These are extracted:

```
GL_INTERFACE_CONTROLGL_STORAGE_PARAMETERS
```

They may be valid Oracle references from the source text, but I would verify whether they came from real SQL/object references or from prose.

Not a blocker, because they have SQL update evidence:

```
"evidence_type": "sql_update"
```

But later you may want to classify them as:

```
referenced_object
```

versus:

```
primary_support_object
```

For this document, the primary objects are clearly:

```
GL_INTERFACEFND_LOOKUPS
```

### 2. Chunk count is still high

Current:

```
chunks_created: 79
```

This is acceptable for a long Oracle troubleshooting note, especially because many chunks are error-specific. But for ingestion, you may later add a mode:

```
error_catalog_chunking = true
```

where each chunk is shaped as:

```
Error codeSymptomCauseResolutionValidationReference
```

That can improve support-answer quality.

### 3. Some low-priority chunks are correctly marked, but one may need review

The output now marks some chunks as:

```
rag_priority: low
```

Examples include:

```
ReferencesCommunity Discussions
```

Good.

One chunk titled:

```
G-3) Translation problems
```

is also marked low. That may be okay if it is mostly a reference note, but if it contains an actual known issue/resolution, it should probably be `medium`.

Not a blocker.

### 4. `metadata_confidence` is only 0.7

The document-level metadata confidence is:

```
"metadata_confidence": 0.7
```

That is acceptable, but it reflects that the document still has incomplete or noisy source structure. Good to keep it visible.