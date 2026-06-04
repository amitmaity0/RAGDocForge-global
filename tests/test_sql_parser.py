from ragdocforge.parsers.sql_parser import SqlParser


def test_sql_parser_extracts_tables_and_risk(tmp_path):
    path = tmp_path / "query.sql"
    path.write_text("select * from gl_interface where group_id = :group_id;\nupdate gl_interface set status = 'E';", encoding="utf-8")

    document = SqlParser().parse(str(path))

    assert "GL_INTERFACE" in document.tables
    assert "GROUP_ID" in document.keywords
    assert any("UPDATE" in warning for warning in document.warnings)


def test_plsql_parser_extracts_package_procedure_and_function(tmp_path):
    path = tmp_path / "pkg.pks"
    path.write_text(
        """
        create or replace package xx_ap_support_pkg as
          procedure validate_invoice(p_invoice_id in number);
          function invoice_error_count(p_invoice_id in number) return number;
        end xx_ap_support_pkg;
        """,
        encoding="utf-8",
    )

    document = SqlParser().parse(str(path))

    assert document.detected_doc_type == "PLSQL"
    assert "XX_AP_SUPPORT_PKG" in document.packages
    assert "VALIDATE_INVOICE" in document.procedures
    assert "INVOICE_ERROR_COUNT" in document.functions
