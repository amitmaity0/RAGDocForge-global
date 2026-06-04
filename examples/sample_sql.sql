-- Purpose: inspect Journal Import interface rows by group id.
select status, request_id, group_id, set_of_books_id, accounting_date
from gl_interface
where group_id = :group_id;
