#!/usr/bin/env python3
import argparse
import re
import subprocess
from pathlib import Path
from common import git_bytes, root


def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and result.returncode:
        raise RuntimeError(" ".join(map(str, cmd)) + "\n" + result.stdout.decode(errors="replace"))
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("branch")
    parser.add_argument("seed")
    parser.add_argument("--device")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-no-device", action="store_true")
    args = parser.parse_args()
    repo = root()
    saved = (repo / ".config").read_bytes() if (repo / ".config").exists() else None
    full = git_bytes("show", args.branch + ":" + args.seed, repo=repo)
    (repo / ".config").write_bytes(full)
    run(["make", "defconfig"], cwd=repo)
    compact = subprocess.run(["bash", "scripts/diffconfig.sh"], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    text = compact.decode(errors="replace")
    devices = re.findall(r"^CONFIG_TARGET_.*_DEVICE_.*=y$", text, re.M)
    if not devices and args.device:
        text += args.device + "\n"
        devices = [args.device]
    if not devices and not args.allow_no_device:
        raise SystemExit("no DEVICE line in seed " + args.seed)
    if saved is None:
        (repo / ".config").unlink(missing_ok=True)
    else:
        (repo / ".config").write_bytes(saved)
    if args.write:
        path = repo / args.seed
        path.write_text(text)
        print("wrote", path.relative_to(repo), "device", devices[0] if devices else "none")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
