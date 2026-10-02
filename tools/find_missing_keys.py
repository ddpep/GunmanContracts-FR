#!/usr/bin/env python3
"""Find where a displayed string comes from: the text table, or baked into an asset.

    python tools/find_missing_keys.py "CONTRACTS" "AMBIENT OCCLUSION"

Read-only. For each searched string it answers, in order:

1. does the game's `languages` TextAsset carry it - in which column, under which key, and
   what does our repository say for that key (empty value? same as English?);
2. if the table does not carry it, is the literal still present in the game's binaries
   (a hardcoded label in a scene, a prefab or a TextMeshPro object), and in which file.

A key present in the table but untranslated is a line to add to `data/fr_strings.json`;
a string found in a binary is baked into an asset and no table edit will move it.
"""
import argparse
import json
import os
import sys

DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data"
HERE = os.path.dirname(os.path.abspath(__file__))
STRINGS = os.path.join(HERE, "..", "data", "fr_strings.json")

# Assets worth scanning for a baked literal. The .resS payloads hold audio, not text.
SUFFIXES = (".assets", ".resource", ".dat", ".unity3d", ".bytes", ".json")
NAMES = ("globalgamemanagers", "globalgamemanagers.assets", "data.unity3d")


def table(data_dir=None):
    import UnityPy

    target = os.path.join(data_dir or DATA, "resources.assets")
    env = UnityPy.load(target)
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        d = obj.read()
        if getattr(d, "m_Name", "") == "languages":
            return d.m_Script
    return None


def scan_binaries(needles, case_sensitive=False, data_dir=None):
    """Byte-level search: a literal baked in an asset is stored as plain ASCII (or UTF-16).

    Case-insensitive by default; pass case_sensitive=True when hunting a DISPLAYED
    LABEL (an all-caps on-screen "CONTRACTS" is not proved by the table's "Contracts").
    """
    found = {}
    files = []
    for root, _, names in os.walk(data_dir or DATA):
        for n in names:
            path = os.path.join(root, n)
            if n in NAMES or n.lower().endswith(SUFFIXES):
                files.append(path)
    for path in files:
        try:
            if os.path.getsize(path) > 600 * 1024 * 1024:
                continue
            with open(path, "rb") as fh:
                blob = fh.read()
        except OSError:
            continue
        haystack = blob if case_sensitive else blob.lower()
        for needle in needles:
            target = needle if case_sensitive else needle.lower()
            encodings = []
            for enc in ("utf-8", "utf-16-le"):
                if target.encode(enc) in haystack:
                    encodings.append(enc)
            if encodings:
                found.setdefault(needle, []).append((os.path.basename(path), os.path.getsize(path),
                                                     ", ".join(encodings)))
    return found, len(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("needles", nargs="+")
    ap.add_argument("--case-sensitive", "--sensible", dest="case_sensitive", action="store_true",
                    help="case-sensitive (look for a displayed label, not a word); "
                         "--sensible is kept as an alias")
    ap.add_argument("--data", default=DATA)
    args = ap.parse_args()

    script = table(args.data)
    if script is None:
        sys.exit("TextAsset 'languages' not found - unexpected game build")
    lines = script.split("\r\n")
    header = lines[0].split("|") if lines else []
    print(f"  game table: {len(lines) - 1} lines, {len(header)} columns")
    print(f"  columns   : {header}")
    repo = json.load(open(STRINGS, encoding="utf-8"))
    print()

    for needle in args.needles:
        lowered = needle.lower()
        print(f"  === {needle} ===")
        seen = 0
        for i, line in enumerate(lines):
            if i == 0 or lowered not in line.lower():
                continue
            fields = line.split("|")
            key = fields[0]
            seen += 1
            if seen <= 6:
                print(f"    line {i} | key: {key}")
                for j, v in enumerate(fields):
                    if j == 0:
                        continue
                    marker = " <<<" if lowered in v.lower() else ""
                    print(f"        col {j:2d}: {v[:70]}{marker}")
                expected = repo.get(key)
                print(f"        repo   : {expected if expected is not None else '(key absent from the repo)'}")
        if seen:
            print(f"    -> present in the table on {seen} line(s): it is a key, not a hardcoded string")
        else:
            print("    -> absent from the table: hardcoded string likely")
        print()

    print("  === searching the game's binaries for hardcoded text ===")
    found, n = scan_binaries(args.needles, case_sensitive=args.case_sensitive, data_dir=args.data)
    print(f"  {n} candidate file(s) scanned")
    for needle in args.needles:
        hits = found.get(needle, [])
        if not hits:
            print(f"    {needle}: not found in plain text (assembled text, or outside the scanned files)")
            continue
        print(f"    {needle}: {len(hits)} file(s)")
        for name, size, encodings in hits[:6]:
            print(f"        {name}  ({size / 1024 / 1024:.1f} MB, {encodings})")


if __name__ == "__main__":
    main()
