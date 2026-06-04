from ragdocforge.converters.chunker import infer_chunk_rag_priority


def test_sql_block_with_oracle_objects_is_high_priority():
    priority = infer_chunk_rag_priority(
        "```sql\nSELECT * FROM gl_interface;\n```",
        "Diagnostics",
        {"tables": ["GL_INTERFACE"], "packages": [], "procedures": [], "functions": [], "error_codes": [], "error_context_lines": [], "keywords": []},
    )

    assert priority == "high"


def test_short_generic_chunk_without_signals_is_low_priority():
    priority = infer_chunk_rag_priority(
        "See related links for more information.",
        "References",
        {"tables": [], "packages": [], "procedures": [], "functions": [], "error_codes": [], "error_context_lines": [], "keywords": []},
    )

    assert priority == "low"


def test_short_error_resolution_chunk_is_not_low_priority():
    priority = infer_chunk_rag_priority(
        "ORA-00054 resolution: rerun the Journal Import after the lock clears.",
        "References",
        {"tables": [], "packages": [], "procedures": [], "functions": [], "error_codes": ["ORA-00054"], "error_context_lines": [], "keywords": []},
    )

    assert priority == "high"
