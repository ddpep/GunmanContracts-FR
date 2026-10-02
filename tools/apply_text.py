#!/usr/bin/env python3
"""Apply the French translations to the installed game."""
import argparse
import datetime
import json
import os
import shutil
import sys

DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data"
HERE = os.path.dirname(os.path.abspath(__file__))
STRINGS = os.path.join(HERE, "..", "data", "fr_strings.json")

DE_SLOT = 2
FR_SLOT = 3


def find_languages(env):
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        if getattr(data, "m_Name", "") == "languages":
            return data
    return None


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", default=DATA, help="path to GunmanContracts_Data")
    parser.add_argument("--overwrite-de", action="store_true",
                        help="also write French into Deutsch for games without a French language option")
    return parser.parse_args(argv)


def translate_line(line, french, overwrite_german):
    fields = line.split("|")
    if fields[0] not in french or len(fields) <= FR_SLOT:
        return line, False

    translation = french[fields[0]]
    changed = False
    if fields[FR_SLOT] != translation:
        fields[FR_SLOT] = translation
        changed = True
    if overwrite_german and fields[DE_SLOT] != translation:
        fields[DE_SLOT] = translation
        changed = True
    return "|".join(fields), changed


def translate_lines(lines, french, overwrite_german=False):
    out, changed = [], 0
    for i, line in enumerate(lines):
        if i > 0:
            line, was_changed = translate_line(line, french, overwrite_german)
            changed += was_changed
        out.append(line)
    return out, changed, overwrite_german


def game_running():
    """Return whether the game is running, or None if it cannot be checked."""
    import subprocess
    try:
        # tasklist writes OEM bytes on a non-English Windows: decode nothing.
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq GunmanContracts.exe"],
                             capture_output=True, timeout=20).stdout or b""
    except Exception:
        return None
    return b"GunmanContracts" in out


def main():
    args = parse_args()
    import UnityPy

    target = os.path.join(args.data, "resources.assets")
    if not os.path.exists(target):
        sys.exit("game not found at " + target)
    state = game_running()
    if state is None:
        print("WARNING: could not check whether the game is running - verify by hand.")
    elif state:
        sys.exit("REFUSING to install: the game is running. Close it first.")
    french = json.load(open(STRINGS, encoding="utf-8"))

    backup = target + ".orig-backup-" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(target, backup)
    print("backup:", backup)
    if os.path.getsize(target) < 500_000_000:
        sys.exit("unexpected resources.assets size - wrong file?")

    env = UnityPy.load(target)
    asset = find_languages(env)
    if asset is None:
        sys.exit("TextAsset 'languages' not found - unexpected game build")

    lines = asset.m_Script.split("\r\n")
    out, changed, overwrite_german = translate_lines(lines, french, args.overwrite_de)

    for a, b in zip(lines, out):
        if a != b:
            assert len(a.split("|")) == len(b.split("|")), "field count changed - aborting"

    asset.m_Script = "\r\n".join(out)
    asset.save()
    blob = env.file.save()
    if len(blob) < 500_000_000:
        sys.exit("REFUSING to write: suspicious output size %d" % len(blob))
    with open(target, "wb") as fh:
        fh.write(blob)

    print("entries updated:", changed)
    print("Deutsch overwrite:", "enabled" if overwrite_german else "disabled")
    if overwrite_german:
        print("done. In game: Options > Language > Deutsch.")
    else:
        print("done. Select French in game if available; Deutsch was left unchanged.")


if __name__ == "__main__":
    main()
