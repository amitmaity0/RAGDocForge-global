CREATE OR REPLACE PACKAGE xxgl_journal_diag_pkg AS
  PROCEDURE diagnose_group(p_group_id IN NUMBER);
  FUNCTION get_interface_status(p_group_id IN NUMBER) RETURN VARCHAR2;
END xxgl_journal_diag_pkg;
/
