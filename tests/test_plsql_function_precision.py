from ragdocforge.analyzers.oracle_object_extractor import extract_oracle_object_candidates, extract_plsql_functions


def test_rejects_prose_function_labels():
    text = """
    Function Err Message describes the import issue.
    Function Return Status is informational.
    Function Warning Number should not become a PL/SQL function.
    """

    candidates, _ = extract_oracle_object_candidates(text)

    assert "ERR" not in {candidate.name for candidate in candidates}
    assert not [candidate for candidate in candidates if candidate.object_type == "function"]


def test_extracts_only_strong_plsql_function_patterns():
    text = """
    CREATE OR REPLACE FUNCTION xxgl_validate_period RETURN VARCHAR2 IS BEGIN RETURN 'Y'; END;
    FUNCTION xxgl_format_message(p_message VARCHAR2) RETURN VARCHAR2;
    FUNCTION xxgl_get_status RETURN VARCHAR2;
    Function Err Message
    """

    functions = extract_plsql_functions(text)
    names = {candidate.name for candidate in functions}

    assert {"XXGL_VALIDATE_PERIOD", "XXGL_FORMAT_MESSAGE", "XXGL_GET_STATUS"} <= names
    assert "ERR" not in names
