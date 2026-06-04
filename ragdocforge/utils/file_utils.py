from pathlib import Path
import re
import shutil

from ragdocforge.config import AppSettings
from ragdocforge.utils.text_utils import stable_slug

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".sql", ".pls", ".pkb", ".pks"}


def build_doc_id(path: str) -> str:
    return stable_slug(Path(path).stem)


def extension_for(path: str) -> str:
    return Path(path).suffix.lower()


def sanitize_filename(filename: str) -> str:
    name = Path(str(filename)).name
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    if not safe:
        safe = "upload"
    stem = Path(safe).stem[:120] or "upload"
    suffix = Path(safe).suffix.lower()
    return f"{stem}{suffix}"


def is_allowed_extension(filename: str) -> bool:
    return extension_for(sanitize_filename(filename)) in ALLOWED_EXTENSIONS


def validate_upload_batch(files: list, settings: AppSettings) -> list[str]:
    errors: list[str] = []
    if len(files) > settings.max_files_per_batch:
        errors.append(f"Too many files selected. Maximum allowed is {settings.max_files_per_batch}.")
    for file_obj in files:
        source_path = uploaded_path(file_obj)
        filename = sanitize_filename(source_path)
        if not is_allowed_extension(filename):
            errors.append(f"Unsupported file type for {filename}.")
            continue
        size_bytes = uploaded_size_bytes(file_obj, source_path)
        if size_bytes is not None:
            max_bytes = settings.max_upload_mb_per_file * 1024 * 1024
            if size_bytes > max_bytes:
                errors.append(f"{filename} exceeds the {settings.max_upload_mb_per_file} MB per-file limit.")
    return errors


def safe_copy_upload_to_workdir(upload_file, workdir: Path) -> Path:
    source_path = Path(uploaded_path(upload_file))
    safe_name = sanitize_filename(source_path.name)
    if not is_allowed_extension(safe_name):
        raise ValueError(f"Unsupported file type for {safe_name}.")
    destination = workdir / safe_name
    if source_path.exists() and source_path.is_file():
        shutil.copy2(source_path, destination)
        return destination
    raise FileNotFoundError(f"Uploaded file could not be found: {safe_name}")


def uploaded_path(file_obj) -> str:
    if isinstance(file_obj, dict):
        return str(file_obj.get("path") or file_obj.get("name") or file_obj)
    return file_obj.name if hasattr(file_obj, "name") else str(file_obj)


def uploaded_size_bytes(file_obj, source_path: str | None = None) -> int | None:
    if isinstance(file_obj, dict) and isinstance(file_obj.get("size"), int):
        return int(file_obj["size"])
    path = Path(source_path or uploaded_path(file_obj))
    try:
        return path.stat().st_size if path.exists() else None
    except OSError:
        return None
