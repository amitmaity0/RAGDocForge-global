from ragdocforge.parsers.text_parser import TextParser


def test_text_parser_preserves_markdown_heading(tmp_path):
    path = tmp_path / "note.md"
    path.write_text("# Purpose\r\nText", encoding="utf-8")

    document = TextParser().parse(str(path))

    assert document.raw_text == "# Purpose\nText"
    assert document.file_extension == ".md"
