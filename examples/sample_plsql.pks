create or replace package xx_gl_support_pkg as
  procedure validate_journal_batch(p_group_id in number);
  function journal_error_count(p_group_id in number) return number;
end xx_gl_support_pkg;
