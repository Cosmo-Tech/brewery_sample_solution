#!/usr/bin/env python3
"""Compare data-loading durations from a folder of csm-orc run logs (.txt)."""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

TIMESTAMP_FORMAT = "%Y/%m/%d-%H:%M:%S"
TIMESTAMP_PATTERN = re.compile(r"^\[(\d{4}/\d{2}/\d{2}-\d{2}:\d{2}:\d{2})\]")
TARGET_PATTERN = re.compile(r"^Target:\s*(\S+)\s*\(([\d,]+) bytes\)")

TEMPLATE_COL = "Run template"
SIZE_COL = "Data size"
NEW_DURATION_COL = "New command duration (s)"
OLD_DURATION_COL = "Old command duration (s)"
COLUMNS = [TEMPLATE_COL, SIZE_COL, NEW_DURATION_COL, OLD_DURATION_COL]

# Run template -> (step that starts the load, step whose SUCCESS ends it, result column)
TEMPLATES = {
    "pass_through": ("load-csv-to-postgres", "load-csv-to-postgres", NEW_DURATION_COL),
    "pass_through_old_command": ("load_results_to_store", "send_results_to_psql", OLD_DURATION_COL),
}


def parse_log(log_path: Path) -> dict | None:
    """Return one table row for the log, or None if it matches no known run template."""
    starts: dict[str, datetime] = {}
    successes: dict[str, datetime] = {}
    size_label = None
    size_bytes = None

    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        target_match = TARGET_PATTERN.match(line.strip())
        if target_match:
            size_label = target_match.group(1)
            size_bytes = int(target_match.group(2).replace(",", ""))
            continue

        timestamp_match = TIMESTAMP_PATTERN.match(line)
        if not timestamp_match:
            continue
        timestamp = datetime.strptime(timestamp_match.group(1), TIMESTAMP_FORMAT)
        message = line[timestamp_match.end():]

        start_match = re.search(r"Starting step (\S+)", message)
        if start_match:
            starts.setdefault(start_match.group(1), timestamp)
            continue

        success_match = re.search(r"(\S+) \(SUCCESS\)", message)
        if success_match:
            successes[success_match.group(1)] = timestamp

    for template, (start_step, end_step, column) in TEMPLATES.items():
        if start_step not in starts:
            continue
        row = {
            "file": log_path.name,
            "size_bytes": size_bytes,
            TEMPLATE_COL: template,
            SIZE_COL: size_label,
            NEW_DURATION_COL: None,
            OLD_DURATION_COL: None,
        }
        # Runs without the SUCCESS line (failed or truncated) keep an empty duration.
        if end_step in successes:
            row[column] = (successes[end_step] - starts[start_step]).total_seconds()
        return row
    return None


def build_dataframe(log_folder: Path) -> pd.DataFrame:
    rows = []
    for log_path in sorted(log_folder.glob("*.txt")):
        row = parse_log(log_path)
        if row is None:
            print(f"Ignoré (aucun run template reconnu) : {log_path.name}", file=sys.stderr)
            continue
        if row[NEW_DURATION_COL] is None and row[OLD_DURATION_COL] is None:
            print(f"Run sans SUCCESS final, durée vide : {log_path.name}", file=sys.stderr)
        rows.append(row)

    df = pd.DataFrame(rows, columns=["file", "size_bytes", *COLUMNS])
    df = df.sort_values(["size_bytes", TEMPLATE_COL, "file"], na_position="last")
    return df[COLUMNS].reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_folder", type=Path, help="Dossier contenant les fichiers log .txt")
    parser.add_argument("--csv", type=Path, help="Enregistre aussi le tableau dans ce fichier CSV")
    args = parser.parse_args()

    if not args.log_folder.is_dir():
        parser.error(f"dossier introuvable : {args.log_folder}")

    df = build_dataframe(args.log_folder)
    if df.empty:
        print("Aucun log exploitable trouvé.", file=sys.stderr)
        return 1

    print(df.to_string(index=False, na_rep="-"))
    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"Tableau enregistré dans {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
