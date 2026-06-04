from pathlib import Path
import importlib.util
import sys


REQUIRED_FILES = ["app.py", "requirements.txt", "README.md", ".env.example", "LICENSE"]
BANNED_DEPENDENCIES = {
    "torch",
    "transformers",
    "sentence-transformers",
    "qdrant-client",
    "langchain",
    "llama-index",
    "openai",
    "opencv-python",
    "faiss",
}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    failures: list[str] = []

    for filename in REQUIRED_FILES:
        if not (repo_root / filename).exists():
            failures.append(f"missing_required_file={filename}")

    readme = (repo_root / "README.md").read_text(encoding="utf-8") if (repo_root / "README.md").exists() else ""
    if not readme.startswith("---") or "sdk: gradio" not in readme or "app_file: app.py" not in readme:
        failures.append("readme_missing_hugging_face_metadata")

    if not (repo_root / "examples").is_dir():
        failures.append("missing_examples_directory")

    requirements = (repo_root / "requirements.txt").read_text(encoding="utf-8").lower() if (repo_root / "requirements.txt").exists() else ""
    for banned in BANNED_DEPENDENCIES:
        if any(line.split("==")[0].split(">=")[0].strip() == banned for line in requirements.splitlines() if line.strip() and not line.startswith("#")):
            failures.append(f"banned_dependency={banned}")

    try:
        spec = importlib.util.spec_from_file_location("ragdocforge_root_app", repo_root / "app.py")
        if spec is None or spec.loader is None:
            failures.append("app_import_spec_failed")
        else:
            module = importlib.util.module_from_spec(spec)
            sys.path.insert(0, str(repo_root))
            spec.loader.exec_module(module)
            if not hasattr(module, "demo"):
                failures.append("demo_object_missing")
    except Exception as exc:  # pragma: no cover - script reports failure details
        failures.append(f"app_import_failed={type(exc).__name__}:{str(exc)[:160]}")

    if failures:
        print("spaces_ready_status=failed")
        for failure in failures:
            print(failure)
        return 1
    print("spaces_ready_status=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
