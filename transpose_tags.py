#!/usr/bin/env python3
"""Preview and transpose tagged columns in a CSV file.

Examples:
    python3 transpose_tags.py preview data.csv Note1 Note2
    python3 transpose_tags.py generate data.csv Product Service --columns Note1 Note2
    python3 transpose_tags.py generate data.csv Product Restriction --columns Note1 Note2 --keep DocID PublishedDate --output output.csv

Both commands accept one to ten exact source-column names. Generate parses
only the columns supplied with --columns. By default, all other columns are
copied; --keep limits which ordinary source columns are retained.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


__version__ = "1.6.0"


TAG_RE = re.compile(
    r'''^\s*([^=;]+?)\s*=\s*(?:"((?:[^"\\]|\\.)*)"|(.*?))\s*$'''
)
DATE_FORMATS = (
    "%B %d, %Y",
    "%b %d, %Y",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%d-%b-%Y",
    "%d-%b-%y",
)
MAX_COLUMNS = 10
MAX_ATTRIBUTES = 10


@dataclass(frozen=True)
class Tag:
    key: str
    value: str
    raw: str


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise ValueError(f"CSV file does not exist: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header row: {path}")
        headers = list(reader.fieldnames)
        if len(headers) != len(set(headers)):
            raise ValueError("CSV contains duplicate column names")
        return headers, list(reader)


def parse_tags(value: str, *, location: str) -> list[Tag]:
    tags: list[Tag] = []
    seen: set[str] = set()
    for part in value.split(";"):
        raw = part.strip()
        if not raw:
            continue
        match = TAG_RE.match(raw)
        if not match:
            raise ValueError(f"{location}: invalid tag {raw!r}")
        key = match.group(1).strip()
        parsed = match.group(2) if match.group(2) is not None else match.group(3)
        value_text = parsed.strip()

        # The current data contract assumes that an attribute occurs no more
        # than once within an individual cell. Define merge behavior here if
        # duplicate attributes must be supported in the future.
        if key in seen:
            raise ValueError(f"{location}: duplicate attribute {key!r}")
        seen.add(key)
        tags.append(Tag(key=key, value=value_text, raw=raw))
    return tags


def selected_columns(
    headers: Sequence[str], requested: Sequence[str], *, command: str
) -> list[str]:
    if not requested:
        raise ValueError("provide at least one column name")
    if len(requested) > MAX_COLUMNS:
        raise ValueError(
            f"{command} accepts at most {MAX_COLUMNS} column names"
        )
    duplicates = [name for name in requested if requested.count(name) > 1]
    if duplicates:
        raise ValueError("column names must be unique")
    missing = [name for name in requested if name not in headers]
    if missing:
        raise ValueError("column(s) not found: " + ", ".join(missing))
    return list(requested)


def selected_keep_columns(
    headers: Sequence[str],
    requested: Sequence[str] | None,
    tag_columns: Sequence[str],
) -> list[str]:
    if requested is None:
        return [header for header in headers if header not in tag_columns]
    if not requested:
        raise ValueError("--keep requires at least one column name")
    duplicates = [name for name in requested if requested.count(name) > 1]
    if duplicates:
        raise ValueError("keep column names must be unique")
    missing = [name for name in requested if name not in headers]
    if missing:
        raise ValueError("keep column(s) not found: " + ", ".join(missing))
    overlap = [name for name in requested if name in tag_columns]
    if overlap:
        raise ValueError(
            "column(s) cannot be both parsed and kept: " + ", ".join(overlap)
        )
    return list(requested)


def parsed_cells(
    rows: Sequence[dict[str, str]], columns: Sequence[str]
) -> Iterable[tuple[int, str, str, list[Tag]]]:
    for row_number, row in enumerate(rows, start=2):
        for column in columns:
            raw = (row.get(column) or "").strip()
            if raw:
                yield row_number, column, raw, parse_tags(
                    raw, location=f"row {row_number}, column {column!r}"
                )


def sort_keys(counts: Counter[str], first_seen: dict[str, int]) -> list[str]:
    return sorted(counts, key=lambda key: (-counts[key], first_seen[key]))


def print_summary(title: str, total: int, counts: Counter[str], order: list[str]) -> None:
    print(title)
    print(f"Total entries: {total}")
    print()
    width = max([len("Attribute"), *(len(key) for key in order)])
    count_width = max([len("Count"), *(len(str(counts[key])) for key in order)])
    print(f"{'Attribute':<{width}}  {'Count':>{count_width}}  Percentage")
    if not order:
        print(f"{'(none)':<{width}}  {0:>{count_width}}         0%")
    else:
        for key in order:
            percentage = counts[key] / total * 100 if total else 0
            print(
                f"{key:<{width}}  {counts[key]:>{count_width}}  "
                f"{percentage:>9.0f}%"
            )


def preview(path: Path, requested_columns: Sequence[str]) -> int:
    headers, rows = read_csv(path)
    columns = selected_columns(headers, requested_columns, command="preview")
    row_counts: Counter[str] = Counter()
    entry_counts: Counter[str] = Counter()
    first_seen: dict[str, int] = {}
    rows_with_entries: set[int] = set()
    keys_by_row: dict[int, set[str]] = {}
    entry_total = 0

    for row_number, _, _, tags in parsed_cells(rows, columns):
        entry_total += 1
        rows_with_entries.add(row_number)
        row_keys = keys_by_row.setdefault(row_number, set())
        for tag in tags:
            first_seen.setdefault(tag.key, len(first_seen))
            entry_counts[tag.key] += 1
            row_keys.add(tag.key)

    for row_keys in keys_by_row.values():
        row_counts.update(row_keys)

    all_keys = set(row_counts) | set(entry_counts)
    for key in all_keys:
        first_seen.setdefault(key, len(first_seen))

    print_summary(
        "Across source rows",
        len(rows_with_entries),
        row_counts,
        sort_keys(row_counts, first_seen),
    )
    print()
    print_summary(
        "After transposing entries",
        entry_total,
        entry_counts,
        sort_keys(entry_counts, first_seen),
    )
    return 0


def format_value(key: str, value: str) -> str:
    if not key.lower().endswith("date"):
        return value
    for date_format in DATE_FORMATS:
        try:
            parsed = datetime.strptime(value, date_format)
            # Avoid the Unix-only %-d directive so this works on Windows too.
            return f"{parsed.day}-{parsed.strftime('%b-%y')}"
        except ValueError:
            pass
    return value


def generate(
    path: Path,
    requested_attributes: Sequence[str],
    requested_columns: Sequence[str],
    requested_keep: Sequence[str] | None,
    output: Path | None,
) -> int:
    if not requested_attributes:
        raise ValueError("generate requires at least one attribute")
    if len(requested_attributes) > MAX_ATTRIBUTES:
        raise ValueError(
            f"generate accepts at most {MAX_ATTRIBUTES} attributes"
        )
    if len(requested_attributes) != len(set(requested_attributes)):
        raise ValueError("attributes must be unique")

    headers, rows = read_csv(path)
    tag_columns = selected_columns(headers, requested_columns, command="generate")
    source_headers = selected_keep_columns(headers, requested_keep, tag_columns)

    entries = list(parsed_cells(rows, tag_columns))
    available = {tag.key for _, _, _, tags in entries for tag in tags}
    valid = [name for name in requested_attributes if name in available]
    invalid = [name for name in requested_attributes if name not in available]
    if invalid:
        print(
            "Warning: attribute(s) not found and ignored: " + ", ".join(invalid),
            file=sys.stderr,
        )
    if not valid:
        print("No output generated because none of the attributes were found.", file=sys.stderr)
        return 1

    output_headers = [
        *source_headers,
        *valid,
        "EntryRem",
        "OriginalCol",
        "EntryOriginal",
    ]
    output_path = output or path.with_name(f"{path.stem}_generated.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    entry_lookup: dict[tuple[int, str], tuple[str, list[Tag]]] = {
        (row_number, column): (raw, tags)
        for row_number, column, raw, tags in entries
    }
    selected = set(valid)
    written = 0
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_headers)
        writer.writeheader()
        for row_number, row in enumerate(rows, start=2):
            for column in tag_columns:
                entry = entry_lookup.get((row_number, column))
                if entry is None:
                    continue
                raw, tags = entry
                values = {tag.key: tag.value for tag in tags}
                remainder = "\n".join(
                    f"{tag.raw};" for tag in tags if tag.key not in selected
                )
                output_row = {header: row.get(header, "") for header in source_headers}
                output_row.update(
                    {
                        attribute: format_value(attribute, values.get(attribute, ""))
                        for attribute in valid
                    }
                )
                output_row["EntryRem"] = remainder
                output_row["OriginalCol"] = column
                output_row["EntryOriginal"] = raw
                writer.writerow(output_row)
                written += 1

    print(f"Generated {written} entries: {output_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview and transpose semicolon-delimited tags in CSV columns."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    preview_parser = commands.add_parser("preview")
    preview_parser.add_argument("csv_file", type=Path)
    preview_parser.add_argument("columns", nargs="+", metavar="COLUMN")

    generate_parser = commands.add_parser("generate")
    generate_parser.add_argument("csv_file", type=Path)
    generate_parser.add_argument("attributes", nargs="+", metavar="ATTRIBUTE")
    generate_parser.add_argument(
        "--columns", "-c", nargs="+", required=True, metavar="COLUMN"
    )
    generate_parser.add_argument("--keep", nargs="+", metavar="COLUMN")
    generate_parser.add_argument("--output", "-o", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "preview":
            return preview(args.csv_file, args.columns)
        return generate(
            args.csv_file,
            args.attributes,
            args.columns,
            args.keep,
            args.output,
        )
    except (OSError, ValueError, csv.Error) as exc:
        parser.print_usage(sys.stderr)
        print(f"{parser.prog}: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    status = main()
    try:
        import sfi  # type: ignore[import-not-found]  # Available inside Stata.
    except ImportError:
        sys.exit(status)
    if status:
        raise RuntimeError(f"command failed with status {status}")
