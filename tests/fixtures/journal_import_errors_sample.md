# Summary

How to retrieve General Ledger Interface error codes in Oracle R12?

## Solution

In Oracle General Ledger, users can review Journal Import errors using the GL_INTERFACE table.

The error can occur when the accounting period is not open. This is a general warning and can be resolved by checking setup.

```sql
SELECT status, group_id, set_of_books_id
FROM gl_interface
WHERE group_id = :group_id;
```

```sql
SELECT lookup_code, meaning
FROM fnd_lookup_values
WHERE lookup_type = 'IMPORT_ERROR';
```

FRM-41830: List of Values contains no entries.
APP-00268: Unable to find period.
ORA-00054: resource busy and acquire with NOWAIT specified.

## References

Oracle General Ledger User Guide.
