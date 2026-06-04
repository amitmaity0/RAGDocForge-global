from pathlib import Path

from ragdocforge.config import AppSettings
from ragdocforge.utils.file_utils import is_allowed_extension, safe_copy_upload_to_workdir, sanitize_filename, validate_upload_batch


def test_sanitize_filename_removes_path_traversal():
    assert sanitize_filename("../../secret.sql") == "secret.sql"
    assert sanitize_filename("bad name?.md") == "bad_name_.md"


def test_unsupported_extension_rejected():
    assert is_allowed_extension("diagnostic.sql")
    assert not is_allowed_extension("payload.exe")


def test_max_files_limit_enforced(tmp_path):
    files = []
    for index in range(2):
        path = tmp_path / f"sample_{index}.md"
        path.write_text("sample", encoding="utf-8")
        files.append(str(path))

    errors = validate_upload_batch(files, AppSettings(max_files_per_batch=1))

    assert any("Too many files" in error for error in errors)


def test_safe_copy_preserves_sanitized_basename(tmp_path):
    source = tmp_path / "bad name.md"
    source.write_text("sample", encoding="utf-8")
    workdir = tmp_path / "work"
    workdir.mkdir()

    copied = safe_copy_upload_to_workdir(str(source), workdir)

    assert copied == workdir / "bad_name.md"
    assert copied.read_text(encoding="utf-8") == "sample"
