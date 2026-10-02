#!/usr/bin/env python3
"""One-command install: French texts + a French entry in the game's language menu.

    python install.py                  # texts + loaderless menu patch (recommended)
    python install.py --dry-run        # report what would be written, write nothing
    python install.py --no-menu        # texts only
    python install.py --overwrite-de   # fallback: French over Deutsch, no menu patch
    python install.py --restore        # undo the menu patch
    python install.py "D:/Games/.../GunmanContracts_Data"   # custom install (or the game folder)

Steps, in order: tools/apply_text.py, tools/add_out_of_table_lines.py --apply,
tools/apply_scene_hints.py --apply, then tools/apply_french_patch.py.
Close the game first. Details and manual commands: README.md.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "tools")
PATCH = os.path.join(TOOLS, "apply_french_patch.py")

DEFAULT_DATA = "C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data"


def run(script, args):
    print(f"\n=== {os.path.relpath(script, HERE).replace(os.sep, '/')} {' '.join(args)}".rstrip())
    return subprocess.run([sys.executable, script, *args]).returncode


def main():
    ap = argparse.ArgumentParser(description="Install the French translation (texts + menu entry).")
    ap.add_argument("data", nargs="?", default=DEFAULT_DATA,
                    help="GunmanContracts_Data folder, or the game folder")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    ap.add_argument("--no-menu", action="store_true", help="texts only, skip the menu patch")
    ap.add_argument("--overwrite-de", action="store_true",
                    help="fallback: write French over Deutsch too (no menu patch)")
    ap.add_argument("--restore", action="store_true", help="undo the menu patch and exit")
    args = ap.parse_args()

    data = args.data.replace("\\", "/").rstrip("/")
    if not data.endswith("GunmanContracts_Data"):
        data = data + "/GunmanContracts_Data"
    game = os.path.dirname(data)

    if args.restore:
        return run(PATCH, ["--restore", game])

    steps = []
    if args.dry_run:
        print("note: apply_text.py has no --dry-run, skipped; the other steps only report.", flush=True)
    else:
        steps.append((os.path.join(TOOLS, "apply_text.py"),
                      (["--overwrite-de"] if args.overwrite_de else []) + [data]))
    steps += [
        (os.path.join(TOOLS, "add_out_of_table_lines.py"),
         (["--dry-run"] if args.dry_run else ["--apply"]) + [data]),
        (os.path.join(TOOLS, "apply_scene_hints.py"),
         (["--dry-run"] if args.dry_run else ["--apply"]) + [data]),
    ]

    for script, sargs in steps:
        code = run(script, sargs)
        if code != 0:
            print(f"\nstep failed (exit {code}), stopping.")
            return code

    if args.no_menu or args.overwrite_de:
        why = "--overwrite-de (French via Deutsch)" if args.overwrite_de else "--no-menu"
        print(f"\nmenu patch skipped ({why}).")
        return 0

    code = run(PATCH, (["--check"] if args.dry_run else []) + [game])
    if code == 0 and not args.dry_run:
        print("\nDone. In the game: Options -> Language -> Francais.")
    return code


if __name__ == "__main__":
    sys.exit(main())
