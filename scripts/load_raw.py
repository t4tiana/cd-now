"""Load every CDnow source line into a local DuckDB raw table."""

from collections.abc import Iterator
import json
from pathlib import Path
import sys

import duckdb

from source_manifest import measure_source


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = REPOSITORY_ROOT / "CDNOW_data" / "CDNOW_master.txt"
MANIFEST_PATH = REPOSITORY_ROOT / "docs" / "source_manifest.json"
DATABASE_PATH = REPOSITORY_ROOT / "data" / "cdnow.duckdb"
TRANSFER_PATH = REPOSITORY_ROOT / "data" / "raw_lines.ndjson"
REPORT_PATH = REPOSITORY_ROOT / "reports" / "raw_load.json"
DATASET = "cdnow_raw"


def parse_line(line_number: int, original_line: str) -> dict[str, int | str | None]:
    """Keep the original line and split only records with exactly four fields."""
    fields = original_line.split()
    field_count = len(fields)
    if field_count == 4:
        status = "four_fields"
        reason = None
        customer_id, transaction_date, cd_count, dollar_value = fields
    else:
        status = "blank" if field_count == 0 else "short" if field_count < 4 else "extra"
        reason = f"expected 4 fields; found {field_count}"
        customer_id = transaction_date = cd_count = dollar_value = None

    return {
        "source_line_number": line_number,
        "original_line": original_line,
        "field_count": field_count,
        "parse_status": status,
        "parse_reason": reason,
        "customer_id_raw": customer_id,
        "transaction_date_raw": transaction_date,
        "cd_count_raw": cd_count,
        "dollar_value_raw": dollar_value,
    }


def iter_source_records(source_path: Path) -> Iterator[dict[str, int | str | None]]:
    """Read every physical source line, preserving its original terminator."""
    with source_path.open("r", encoding="utf-8", newline="") as source:
        for line_number, original_line in enumerate(source, start=1):
            yield parse_line(line_number, original_line)


def write_transfer_file(source_path: Path, transfer_path: Path) -> None:
    """Serialize raw records as a temporary newline-delimited JSON file."""
    with transfer_path.open("w", encoding="utf-8", newline="\n") as transfer:
        for record in iter_source_records(source_path):
            transfer.write(json.dumps(record, ensure_ascii=False) + "\n")


def load() -> dict[str, int | str]:
    """Replace the raw table, create queryable views, and reconcile counts."""
    current_manifest = measure_source(SOURCE_PATH)
    saved_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if current_manifest != saved_manifest:
        raise ValueError("Source file differs from docs/source_manifest.json")

    print("Source manifest verified; loading raw lines.", file=sys.stderr, flush=True)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_transfer_file(SOURCE_PATH, TRANSFER_PATH)
    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute("BEGIN TRANSACTION")
        connection.execute(f"CREATE SCHEMA IF NOT EXISTS {DATASET}")
        connection.execute(f"DROP VIEW IF EXISTS {DATASET}.rejected_lines")
        connection.execute(f"DROP VIEW IF EXISTS {DATASET}.parsed_lines")
        connection.execute(f"DROP VIEW IF EXISTS {DATASET}.malformed_lines")
        connection.execute(f"DROP VIEW IF EXISTS {DATASET}.four_field_lines")
        connection.execute(f"DROP TABLE IF EXISTS {DATASET}.source_lines")
        connection.execute(
            f"""CREATE TABLE {DATASET}.source_lines (
                source_line_number BIGINT,
                original_line VARCHAR,
                field_count INTEGER,
                parse_status VARCHAR,
                parse_reason VARCHAR,
                customer_id_raw VARCHAR,
                transaction_date_raw VARCHAR,
                cd_count_raw VARCHAR,
                dollar_value_raw VARCHAR
            )"""
        )
        connection.execute(
            f"COPY {DATASET}.source_lines FROM ? (FORMAT JSON)", [str(TRANSFER_PATH)]
        )
        connection.execute(
            f"""CREATE OR REPLACE VIEW {DATASET}.malformed_lines AS
                SELECT * FROM {DATASET}.source_lines WHERE parse_status <> 'four_fields'"""
        )
        connection.execute(
            f"""CREATE OR REPLACE VIEW {DATASET}.four_field_lines AS
                SELECT * FROM {DATASET}.source_lines WHERE parse_status = 'four_fields'"""
        )
        raw_count, distinct_lines, four_field_count, malformed_count = connection.execute(
            f"""SELECT count(*), count(DISTINCT source_line_number),
                       count(*) FILTER (WHERE parse_status = 'four_fields'),
                       count(*) FILTER (WHERE parse_status <> 'four_fields')
                FROM {DATASET}.source_lines"""
        ).fetchone()

        if raw_count != current_manifest["line_count"]:
            raise ValueError("Raw row count does not match physical source lines")
        if distinct_lines != raw_count:
            raise ValueError("Source line numbers are not unique in the raw table")
        if four_field_count + malformed_count != raw_count:
            raise ValueError("Four-field and malformed counts do not reconcile")
        connection.execute("COMMIT")

    report = {
        "source_sha256": current_manifest["sha256"],
        "input_lines": current_manifest["line_count"],
        "raw_rows": raw_count,
        "distinct_source_lines": distinct_lines,
        "four_field_rows": four_field_count,
        "malformed_rows": malformed_count,
        "database": "data/cdnow.duckdb",
        "raw_table": f"{DATASET}.source_lines",
        "four_field_view": f"{DATASET}.four_field_lines",
        "malformed_view": f"{DATASET}.malformed_lines",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(load(), indent=2))
