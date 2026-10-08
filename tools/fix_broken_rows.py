#!/usr/bin/env python3
"""Repair rows of the game's language table that are split by a bare line feed.

The table uses CRLF row separators. Bare LF characters inside a row can make
the game drop the entry. Replace them with spaces in key-like, pipe-delimited
rows of the `languages` TextAsset, leaving other text unchanged.

The repaired table is saved by reserializing the asset with UnityPy. This is
not a raw byte patch and does not guarantee unchanged file size or offsets.
"""
import argparse
import re

from common import DATA, EOL, load_table, refuse_if_running, save_table

KEY = re.compile(r"^[A-Za-z0-9_\-]{2,}$")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", default=DATA, help="path to GunmanContracts_Data")
    parser.add_argument("--dry-run", action="store_true", help="report the broken rows and stop")
    return parser.parse_args(argv)


def broken_rows(script):
    """Yield (index, row) for every table row holding a bare line feed."""
    for i, row in enumerate(script.split(EOL)):
        if "\n" not in row:
            continue
        if row.count("|") < 3:
            continue
        fields = row.split("|")
        if not KEY.match(fields[0].strip()):
            continue
        yield i, row


def main():
    args = parse_args()
    path, env, asset = load_table(args.data)

    script = asset.m_Script
    found = list(broken_rows(script))
    total = sum(row.count("\n") for _, row in found)
    print("rows split by a bare line feed:", len(found))
    print("stray line feeds to repair:", total)
    for i, row in found:
        fields = row.split("|")
        print("  row %-6d %-42s %d LF" % (i, fields[0][:42], row.count("\n")))
    if not found:
        print("nothing to repair.")
        return
    if args.dry_run:
        print("dry run - no write.")
        return

    refuse_if_running()

    rows = script.split(EOL)
    repaired = 0
    for i, row in found:
        before = len(row.split("|"))
        fixed = row.replace("\n", " ")
        assert len(fixed.split("|")) == before, "field count changed - aborting"
        rows[i] = fixed
        repaired += 1
    script = EOL.join(rows)

    assert not list(broken_rows(script)), "rows still split - aborting"

    save_table(path, env, asset, rows)
    print("rows repaired:", repaired)


if __name__ == "__main__":
    main()
