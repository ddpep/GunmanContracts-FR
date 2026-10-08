"""Shared helpers: game location, running guard, the `languages` table, safe writes."""
import datetime
import os
import shutil
import subprocess
import sys

DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data"
EXE = "GunmanContracts.exe"
DE_SLOT = 2
FR_SLOT = 3
EOL = "\r\n"
MIN_RATIO = 0.9


def game_running():
    """True/False, or None when the check cannot run.

    Raw bytes, never text=True: tasklist writes OEM on a non-English Windows.
    """
    try:
        out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {EXE}"],
                             capture_output=True, timeout=20).stdout or b""
    except Exception:                                                   # noqa: BLE001
        return None
    return EXE.encode()[:14] in out


def refuse_if_running():
    state = game_running()
    if state:
        sys.exit("REFUSING: the game is running. Close it first.")
    if state is None:
        print("WARNING: could not check whether the game is running - verify by hand.")


def backup(path):
    """Keep the first copy ever seen as `<file>.orig`, and a timestamped copy of this run."""
    orig = path + ".orig"
    if not os.path.exists(orig):
        shutil.copy2(path, orig)
        print("  original kept:", orig)
    stamp = path + ".orig-backup-" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, stamp)
    print("  backup:", stamp)


def write_replacing(path, blob, verify=None):
    """Write next to the target, check, then swap in one rename.

    `verify(tmp_path)` returns an error message or None.
    """
    size = os.path.getsize(path)
    if len(blob) < MIN_RATIO * size:
        sys.exit(f"REFUSING to write: output {len(blob)} bytes against {size} on disk")
    tmp = path + ".tmp-write"
    with open(tmp, "wb") as fh:
        fh.write(blob)
    error = verify(tmp) if verify else None
    if error:
        os.remove(tmp)
        sys.exit("REFUSING to install: " + error)
    os.replace(tmp, path)


def find_languages(env):
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        if getattr(data, "m_Name", "") == "languages":
            return data
    return None


def load_table(data_dir):
    """(path, env, asset) for resources.assets and its `languages` TextAsset."""
    import UnityPy

    path = os.path.join(data_dir, "resources.assets")
    if not os.path.exists(path):
        sys.exit("game not found at " + path)
    env = UnityPy.load(path)
    asset = find_languages(env)
    if asset is None:
        sys.exit("TextAsset 'languages' not found - unexpected game build")
    return path, env, asset


def release(env):
    """Close the containers UnityPy keeps open.

    Windows refuses `os.replace` over a file this process still has open, and an
    Environment holds its container open for its whole life. A save that keeps the
    Environment alive therefore fails with WinError 32 on the swap - after having
    written the whole file, so the install looks half done.
    """
    import gc

    containers = list(getattr(env, "files", {}).values())
    single = getattr(env, "file", None)
    if single is not None:
        containers.append(single)
    for container in containers:
        reader = getattr(container, "reader", None)
        if reader is not None:
            reader.dispose()
    gc.collect()


def save_table(path, env, asset, lines):
    """Back up, write the table, read it back before replacing the game file."""
    import UnityPy

    text = EOL.join(lines)
    asset.m_Script = text
    asset.save()
    blob = env.file.save()

    def same_table(tmp):
        check = UnityPy.load(tmp)
        written = find_languages(check)
        ok = written is not None and written.m_Script == text
        release(check)          # the verification opened the tmp: close it before the swap
        return None if ok else \
            "the written table does not read back identical"

    backup(path)
    release(env)                # the swap cannot replace a file this process still has open
    write_replacing(path, blob, same_table)
