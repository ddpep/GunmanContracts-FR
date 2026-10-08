#!/usr/bin/env python3
"""Read the game's own text table back and compare it with this repository.

    python tools/verify_game_text.py

Read-only: nothing is written. It answers one question - what the installed game
displays today, against what `data/fr_strings.json` says should be displayed.

The French slot is FR_SLOT (3). The German slot (2) is compared only with
--overwrite-de, the fallback install that writes French over Deutsch: otherwise it
holds German and every line would be reported as different.
"""
import argparse
import json
import os
import sys

from common import DATA, DE_SLOT, EOL, FR_SLOT, load_table

HERE = os.path.dirname(os.path.abspath(__file__))
STRINGS = os.path.join(HERE, "..", "data", "fr_strings.json")


def repo_state():
    """Report the local revision, catalog changes and lag against the known upstream ref."""
    import subprocess

    def git(*a):
        try:
            return subprocess.run(["git", "-C", HERE, *a], capture_output=True, text=True,
                                  encoding="utf-8", timeout=20).stdout.strip()
        except Exception:
            return ""

    head = git("rev-parse", "--short", "HEAD")
    dirty = git("status", "--porcelain", os.path.join("..", "data", "fr_strings.json"))
    behind = git("rev-list", "--count", "HEAD..@{u}")
    line = f"  data/fr_strings.json: revision {head or 'not in a repository'}"
    if dirty:
        line += " + UNCOMMITTED CHANGES"
    if behind not in ("", "0"):
        line += f" | BEHIND by {behind} commit(s) vs the known remote: 'git fetch' before concluding"
    print(line)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data", nargs="?", default=DATA)
    ap.add_argument("--overwrite-de", action="store_true",
                    help="the install used the Deutsch fallback: compare the DE slot too")
    args = ap.parse_args()

    repo_state()
    french = json.load(open(STRINGS, encoding="utf-8"))
    _, _, asset = load_table(args.data)

    lines = asset.m_Script.split(EOL)
    total = fr_ok = fr_ko = de_ok = de_ko = missing = 0
    differences = []
    for i, line in enumerate(lines):
        if i == 0:
            continue
        fields = line.split("|")
        if len(fields) <= FR_SLOT:
            continue
        key = fields[0]
        if key not in french:
            continue
        total += 1
        expected = french[key]
        if fields[FR_SLOT] == expected:
            fr_ok += 1
        else:
            fr_ko += 1
            if len(differences) < 8:
                differences.append(("FR", key, fields[FR_SLOT], expected))
        if not args.overwrite_de:
            continue
        if fields[DE_SLOT] == expected:
            de_ok += 1
        else:
            de_ko += 1
            if len(differences) < 8:
                differences.append(("DE", key, fields[DE_SLOT], expected))

    print(f"  repo lines present in the game table: {total}")
    print()
    print("  scope: this compares only the keys of data/fr_strings.json that the table already carries.")
    print("  it does NOT verify the out-of-table lines (add_out_of_table_lines.py) nor the scene")
    print("  hints (apply_scene_hints.py). A clean result here is not proof of a complete install.")
    print(f"  FR slot (3) identical to the repo: {fr_ok} | different: {fr_ko}")
    if args.overwrite_de:
        print(f"  DE slot (2) identical to the repo: {de_ok} | different: {de_ko}")
    if not total:
        print("  WARNING: no comparable line - the text is probably not installed.")
    for slot, key, found, expected in differences:
        print(f"    [{slot}] {key[:34]:34s}")
        print(f"         game   : {found[:88]}")
        print(f"         repo   : {expected[:88]}")
    return 1 if (not total or fr_ko or de_ko) else 0


if __name__ == "__main__":
    sys.exit(main())
