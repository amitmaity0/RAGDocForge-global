# GL Journal Import Support SOP

## Purpose

Use this SOP to diagnose Oracle EBS General Ledger Journal Import issues for the GL module and the Journal Import business process.

## Scope

This procedure applies to support analysis of interface rows staged in `GL_INTERFACE` before and after Journal Import processing.

## Prerequisites

- Read-only database access for diagnostic SQL.
- Oracle EBS responsibility with access to Journal Import requests.
- Known `GROUP_ID`, ledger, source, and accounting period.

## Procedure

1. Confirm the concurrent request status for Journal Import.
2. Identify the source and `GROUP_ID` used by the feeder system.
3. Review rejected rows in `GL_INTERFACE`.
4. Correct source data or interface rows according to approved support procedures.
5. Rerun Journal Import after validation checks pass.

## Diagnostic SQL

```sql
SELECT status, group_id, set_of_books_id, accounting_date
FROM gl_interface
WHERE group_id = :group_id;
```

Expected output: rows with error status require correction before rerun. The query is read-only and safe for support diagnostics.

## Validation

- Confirm no rejected rows remain in `GL_INTERFACE` for the target `GROUP_ID`.
- Confirm journals were created in `GL_JE_HEADERS` and `GL_JE_LINES`.
- Confirm the Journal Import Execution Report completes without error.

## Known Errors

- ORA-00054: resource busy and acquire with NOWAIT specified.
- FRM-41830: List of Values contains no entries.
- APP-00268: Please specify a valid printer.

## Rollback/Recovery

If incorrect journals are created, follow approved reversal or deletion procedures for unposted journals. Do not update Oracle base tables directly.

## References

- Oracle General Ledger User Guide.
- Internal support runbook for Journal Import recovery.
