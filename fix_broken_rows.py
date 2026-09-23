#!/usr/bin/env python3
"""Repair rows of the game's language table that are split by a bare line feed.

The table uses CRLF row separators. Bare LF characters inside a row can make
the game drop the entry. Replace them with spaces in key-like, pipe-delimited
rows of the `languages` TextAsset, leaving other text unchanged.

The repaired table is saved by reserializing the asset with UnityPy. This is
not a raw byte patch and does not guarantee unchanged file size or offsets.
"""
import argparse
import datetime
import os
import re
import shutil
import sys

DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data"

KEY = re.compile(r"^[A-Za-z0-9_\-]{2,}$")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", default=DATA, help="path to GunmanContracts_Data")
    parser.add_argument("--dry-run", action="store_true", help="report the broken rows and stop")
    return parser.parse_args(argv)


def find_languages(env):
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        if getattr(data, "m_Name", "") == "languages":
            return data
    return None


def game_running():
    """Return whether the game is running, or None if it cannot be checked."""
    import subprocess
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq GunmanContracts.exe"],
                             capture_output=True, timeout=20).stdout or b""
    except Exception:
        return None
    return b"GunmanContracts" in out


def broken_rows(script):
    """Yield (index, row) for every table row holding a bare line feed."""
    for i, row in enumerate(script.split("\r\n")):
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
    import UnityPy

    target = os.path.join(args.data, "resources.assets")
    if not os.path.exists(target):
        sys.exit("game not found at " + target)

    env = UnityPy.load(target)
    asset = find_languages(env)
    if asset is None:
        sys.exit("TextAsset 'languages' not found - unexpected game build")

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

    state = game_running()
    if state is None:
        print("WARNING: could not check whether the game is running - verify by hand.")
    elif state:
        sys.exit("REFUSING to write: the game is running. Close it first.")

    backup = target + ".orig-backup-" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(target, backup)
    print("backup:", backup)

    rows = script.split("\r\n")
    repaired = 0
    for i, row in found:
        before = len(row.split("|"))
        fixed = row.replace("\n", " ")
        assert len(fixed.split("|")) == before, "field count changed - aborting"
        rows[i] = fixed
        repaired += 1
    script = "\r\n".join(rows)

    assert not list(broken_rows(script)), "rows still split - aborting"

    asset.m_Script = script
    asset.save()
    blob = env.file.save()
    if len(blob) < 500_000_000:
        sys.exit("REFUSING to write: suspicious output size %d" % len(blob))
    with open(target, "wb") as fh:
        fh.write(blob)
    print("rows repaired:", repaired)


if __name__ == "__main__":
    main()
