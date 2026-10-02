"""Focused tests for the lossless physical-line parser."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from load_raw import iter_source_records, parse_line


def test_four_fields_preserve_original_text_and_leading_zeroes() -> None:
    original = "00001\t19970101  1   11.77\r\n"
    parsed = parse_line(7, original)

    assert parsed["source_line_number"] == 7
    assert parsed["original_line"] == original
    assert parsed["field_count"] == 4
    assert parsed["parse_status"] == "four_fields"
    assert parsed["parse_reason"] is None
    assert parsed["customer_id_raw"] == "00001"
    assert parsed["transaction_date_raw"] == "19970101"
    assert parsed["cd_count_raw"] == "1"
    assert parsed["dollar_value_raw"] == "11.77"


def test_malformed_lines_are_retained_with_reasons() -> None:
    for source, expected_status, count in [
        (" \r\n", "blank", 0),
        ("00001 19970101 1\n", "short", 3),
        ("00001 19970101 1 11.77 extra\n", "extra", 5),
    ]:
        parsed = parse_line(3, source)
        assert parsed["original_line"] == source
        assert parsed["parse_status"] == expected_status
        assert parsed["field_count"] == count
        assert parsed["parse_reason"] == f"expected 4 fields; found {count}"
        assert parsed["customer_id_raw"] is None
        assert parsed["dollar_value_raw"] is None


def test_reader_keeps_line_numbers_and_terminators(tmp_path: Path) -> None:
    source = tmp_path / "small.txt"
    source.write_bytes(b"00001 19970101 1 11.77\r\n\r\n00002 19970102 2 20.00\n")

    records = list(iter_source_records(source))

    assert [record["source_line_number"] for record in records] == [1, 2, 3]
    assert [record["parse_status"] for record in records] == [
        "four_fields",
        "blank",
        "four_fields",
    ]
    assert records[0]["original_line"] == "00001 19970101 1 11.77\r\n"
    assert records[1]["original_line"] == "\r\n"
    assert records[2]["original_line"] == "00002 19970102 2 20.00\n"
