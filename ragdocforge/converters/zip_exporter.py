from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


class ZipExporter:
    def write(self, files: list[str], zip_path: str) -> str:
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
            for file_path in files:
                path = Path(file_path)
                if path.exists():
                    arcname = _archive_name(path)
                    archive.write(path, arcname=arcname)
        return zip_path


def _archive_name(path: Path) -> str:
    if path.suffix.lower() == ".md" and path.name not in {"README_OUTPUTS.md", "suggested_sections.md", "output_summary.md"}:
        return f"ragdocforge_outputs/markdown/{path.name}"
    return f"ragdocforge_outputs/{path.name}"
