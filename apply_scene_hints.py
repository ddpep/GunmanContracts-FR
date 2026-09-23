#!/usr/bin/env python3
"""Translate the interaction hints that the game reads from its SCENES, not from the table.

    python apply_scene_hints.py --dry-run
    python apply_scene_hints.py --apply

Why this tool exists: some on-screen labels exist twice in the install - once in the `languages`
table (which `apply_text.py` translates) and once baked into a scene asset as the default text of a
TextMeshPro component. The game replaces the second one from the table when its lookup covers the
element, and leaves the baked English on screen when it does not. Measured case: standing in front
of a basement door, the objective came from the table (French) while the interaction hint stayed
English - a block that is half French, half English.

The repair is a raw byte replacement, and every replacement is **the same length** as the English it
replaces (the French is padded with trailing spaces, which no text field renders). Nothing else moves:
the string's length prefix stays valid, the object keeps its byte length, and the file's object table
is untouched. No re-serialization at all.

`scene_hints.json` carries the pairs. It is a small, explicit list on purpose: only the hints whose
English was measured inside a scene asset belong here, and a hint whose French would need more room
than the English is left alone rather than resized.
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data"
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, "scene_hints.json")
SCENES = ["sharedassets1.assets", "sharedassets2.assets", "sharedassets3.assets",
          "sharedassets4.assets", "globalgamemanagers"]


def game_running():
    """Raw bytes, never text=True: tasklist emits OEM on non-English systems."""
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq GunmanContracts.exe"],
                             capture_output=True, timeout=20).stdout or b""
    except Exception:
        return None
    return b"GunmanContracts" in out


def replace_in_bytes(raw, pairs):
    """Replace each English label with its French twin, in the raw file bytes.

    Both sides are written as a 4-byte little-endian length followed by the UTF-8 text, and the
    French is the same byte length as the English it replaces, so nothing else in the file moves:
    the length prefix stays valid and the object keeps its byte length. That is why the caller
    refuses any pair whose lengths differ, and why there is no re-serialization anywhere here.
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
        state = game_running()
        if state is None:
            print("WARNING: cannot check whether the game is running.")
        elif state:
            sys.exit("REFUSING: the game is running. Close it first.")

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
        backup = path + ".orig-backup-" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(path, backup)
        with open(path, "wb") as fh:
            fh.write(raw)
        print(f"    backup: {backup}")

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
