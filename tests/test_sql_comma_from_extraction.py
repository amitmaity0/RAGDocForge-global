from ragdocforge.analyzers.oracle_object_extractor import extract_from_clause_objects, extract_oracle_object_candidates


def test_extracts_comma_separated_from_objects_without_aliases():
    text = """
    SELECT gi.status, fl.meaning
    FROM apps.gl_interface gi, apps.fnd_lookups fl
    WHERE gi.status = fl.lookup_code;

    SELECT *
    FROM gl_je_headers h, gl_je_lines l, gl_code_combinations gcc
    WHERE h.je_header_id = l.je_header_id;
    """

    objects = extract_from_clause_objects(text)
    names = {candidate.name for candidate in objects}

    assert {"GL_INTERFACE", "FND_LOOKUPS", "GL_JE_HEADERS", "GL_JE_LINES", "GL_CODE_COMBINATIONS"} <= names
    assert {"GI", "FL", "H", "L", "GCC"}.isdisjoint(names)


def test_full_extractor_includes_comma_from_tables():
    candidates, _ = extract_oracle_object_candidates("SELECT * FROM gl_je_headers h, gl_je_lines l WHERE 1=1")

    assert {"GL_JE_HEADERS", "GL_JE_LINES"} <= {candidate.name for candidate in candidates}


def test_does_not_extract_from_objects_from_prose():
    candidates = extract_from_clause_objects("Function Err Message: Preparing main_prep from main_stmt")

    assert candidates == []
