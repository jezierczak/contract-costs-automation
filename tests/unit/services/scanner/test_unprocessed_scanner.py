from contract_costs.services.scanner.unprocessed_scanner import scan_unprocessed


def test_scan_unprocessed_returns_pdf_and_xml_only(tmp_path) -> None:
    (tmp_path / "a.pdf").write_text("x", encoding="utf-8")
    (tmp_path / "b.xml").write_text("x", encoding="utf-8")
    (tmp_path / "c.txt").write_text("x", encoding="utf-8")

    found = scan_unprocessed(tmp_path)
    names = {p.name for p in found}

    assert names == {"a.pdf", "b.xml"}

