#!/usr/bin/env python3
"""Add or update subtitles whose clip names are absent from the original text table.

    python tools/add_out_of_table_lines.py --dry-run
    python tools/add_out_of_table_lines.py --apply

Read translations from `data/fr_strings_out_of_table.json`, keyed by exact clip names.
Write French into DE and FR; leave EN empty because no source text is provided.
Update existing rows in place and append missing rows without shifting existing indices.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_OF_TABLE = os.path.join(HERE, "..", "data", "fr_strings_out_of_table.json")
DE_SLOT = 2
FR_SLOT = 3
FIELDS = 11


def find_languages(env):
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        if getattr(data, "m_Name", "") == "languages":
            return data
    return None


def game_running():
    import subprocess
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq GunmanContracts.exe"],
                             capture_output=True, timeout=20).stdout or b""
    except Exception:
        return None
    return b"GunmanContracts" in out


def row(key, fr):
    """key | EN(empty) | DE | FR | ES | PL | CH | JP | RU | (empty) | end"""
    f = [""] * FIELDS
    f[0] = key
    f[DE_SLOT] = fr
    f[FR_SLOT] = fr
    f[-1] = "end"
    return "|".join(f)


def sync_rows(lines, targets):
    """Return (new_lines, to_add, updated).

    Keep existing row indices stable. Append missing rows before trailing empty lines.
    """
    end = len(lines)
    while end > 0 and not lines[end - 1].strip():
        end -= 1
    out, updated, seen = [], [], set()
    for line in lines[:end]:
        f = line.split("|")
        k = f[0]
        if k in targets and len(f) > FR_SLOT:
            seen.add(k)
            if f[FR_SLOT] != targets[k] or f[DE_SLOT] != targets[k]:
                out.append(row(k, targets[k]))
                updated.append((k, f[FR_SLOT], targets[k]))
                continue
        out.append(line)
    to_add = sorted((c, v) for c, v in targets.items() if c not in seen)
    return out + [row(c, v) for c, v in to_add] + lines[end:], to_add, updated


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data", nargs="?", default=DATA)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        sys.exit("choose --dry-run or --apply")
    import UnityPy

    targets = json.load(open(OUT_OF_TABLE, encoding="utf-8"))
    target = os.path.join(args.data, "resources.assets")
    if not os.path.exists(target):
        sys.exit("game not found at " + target)
    if args.apply:
        state = game_running()
        if state is None:
            print("WARNING: cannot check whether the game is running.")
        elif state:
            sys.exit("REFUSING: the game is running. Close it first.")

    env = UnityPy.load(target)
    asset = find_languages(env)
    if asset is None:
        sys.exit("TextAsset 'languages' not found - unexpected game build")

    lines = asset.m_Script.split("\r\n")
    new_lines, to_add, updated = sync_rows(lines, targets)
    already = len(targets) - len(to_add)
    print(f"  lines to add: {len(to_add)}   (already present: {already})")
    for c, v in to_add[:6]:
        print(f"    + {c[:44]:44s} {v[:52]}")
    if to_add:
        print("    ...")
    print(f"  lines to UPDATE: {len(updated)}")
    for c, old, new in updated[:8]:
        print(f"    ~ {c[:40]:40s} {old[:40]!r} -> {new[:40]!r}")

    if args.dry_run:
        print("\n  --dry-run: nothing was written.")
        return

    backup = target + ".orig-backup-" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(target, backup)
    print("\n  backup:", backup)

    asset.m_Script = "\r\n".join(new_lines)
    asset.save()
    blob = env.file.save()
    if len(blob) < 500_000_000:
        sys.exit("REFUSING to write: suspicious output size %d" % len(blob))
    with open(target, "wb") as fh:
        fh.write(blob)
    print(f"  lines added: {len(to_add)} | lines updated: {len(updated)}"
          f"   (table total: {len(new_lines) - 1})")


if __name__ == "__main__":
    main()
