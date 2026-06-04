from pydantic import BaseModel, Field


class ExportBundle(BaseModel):
    output_dir: str
    markdown_files: list[str] = Field(default_factory=list)
    chunks_jsonl: str
    quality_report_json: str
    manifest_json: str
    zip_file: str
