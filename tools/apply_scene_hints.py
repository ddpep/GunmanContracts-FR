#!/usr/bin/env python3
"""Translate the interaction hints that the game reads from its SCENES, not from the table.

    python tools/apply_scene_hints.py --dry-run
    python tools/apply_scene_hints.py --apply

Some on-screen labels exist twice: in the `languages` table (translated by
`apply_text.py`) and baked into a scene asset as a TextMeshPro default text. The
game only replaces the baked one when its table lookup covers the element, so
those hints stay English without this pass.

The repair is a raw byte replacement: each French label is the same byte length as
the English it replaces (padded with trailing spaces, which no text field renders),
so nothing else in the file moves and there is no re-serialization.

`data/scene_hints.json` carries the pairs, and only measured hints belong there.
"""
import argparse
import json
import os
import sys

from common import DATA, backup, refuse_if_running, write_replacing

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, "..", "data", "scene_hints.json")
SCENES = ["sharedassets1.assets", "sharedassets2.assets", "sharedassets3.assets",
          "sharedassets4.assets", "globalgamemanagers"]


def replace_in_bytes(raw, pairs):
    """Replace each English label with its French twin in the raw file bytes.

    Both sides are a 4-byte little-endian length followed by UTF-8 text; equal byte
    lengths are enforced by the caller, so nothing else in the file moves.
    """
    replacements = []
    for key, pair in pairs.items():
        needle = len(pair["en"]).to_bytes(4, "little") + pair["en"].encode("utf-8")
        replacement = len(pair["fr"]).to_bytes(4, "little") + pair["fr"].encode("utf-8")
        n = raw.count(needle)
        if n:
            raw = raw.replace(needle, replacement)
            replacements.append((key, n))
    return raw, replacements


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data", nargs="?", default=DATA)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        sys.exit("choose --dry-run or --apply")

    pairs = {k: v for k, v in json.load(open(PLAN, encoding="utf-8")).items()
             if not k.startswith("_")}
    for key, pair in pairs.items():
        if len(pair["fr"].encode("utf-8")) != len(pair["en"].encode("utf-8")):
            sys.exit(f"REFUSED: {key} - the French is not the same length as the English "
                     f"({len(pair['fr'].encode('utf-8'))} bytes vs {len(pair['en'].encode('utf-8'))})")

    if args.apply:
        refuse_if_running()

    total = 0
    for name in SCENES:
        path = os.path.join(args.data, name)
        if not os.path.exists(path):
            continue
        raw = open(path, "rb").read()
        raw, replacements = replace_in_bytes(raw, pairs)
        if not replacements:
            continue
        total += sum(n for _, n in replacements)
        print(f"  {name}")
        for key, n in replacements:
            print(f"    {key:14s} {n} occurrence(s): {pairs[key]['en']!r} -> {pairs[key]['fr']!r}")
        if args.dry_run:
            continue
        backup(path)
        write_replacing(path, raw)

    print()
    if args.dry_run:
        print(f"  --dry-run: {total} occurrence(s) to replace, nothing was written.")
        return
    print(f"  {total} occurrence(s) replaced.")

    # re-read from disk: the French is there, the English is gone
    for name in SCENES:
        path = os.path.join(args.data, name)
        if not os.path.exists(path):
            continue
        reread = open(path, "rb").read()
        for key, pair in pairs.items():
            if pair["fr"].encode("utf-8") in reread:
                remaining = reread.count(len(pair["en"]).to_bytes(4, "little") + pair["en"].encode("utf-8"))
                state = "clean" if remaining == 0 else f"WARNING: {remaining} English remaining"
                print(f"    reread {name:22s} {key:14s} {state}")


if __name__ == "__main__":
    main()
