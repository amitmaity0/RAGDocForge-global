-- Purpose: diagnose Oracle EBS GL Journal Import interface rows for a specific group.
-- Bind variables: :group_id is the Journal Import group identifier.
-- Expected output: interface rows with status and accounting context for support review.
-- Safety: read-only SELECT statement; do not modify Oracle EBS base tables.

SELECT status,
       group_id,
       set_of_books_id,
       accounting_date,
       user_je_source_name
FROM gl_interface
WHERE group_id = :group_id;
