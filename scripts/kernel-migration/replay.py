#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from common import branches, full_version, git_bytes, patch_files, root


def run(cmd, cwd=None, stdin=None):
    return subprocess.run(cmd, cwd=cwd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def apply_patch(tree, patch):
    with open(patch, "rb") as fh:
        result = run(["patch", "-f", "-p1", "-d", str(tree)], stdin=fh)
    return result.returncode, result.stdout.decode(errors="replace")


def scan_output(text):
    return {
        "offset": len(re.findall(r"\(offset -?\d+ lines?\)", text)),
        "fuzz": len(re.findall(r"with fuzz \d+", text)),
        "failed": "FAILED" in text or "****" in text,
        "skipped": "previously applied" in text or "Skipping patch" in text,
    }


def extract_base(repo, version, workdir):
    tarball = None
    for candidate in sorted(repo.glob("dl/linux-" + version + "*.tar.xz"), reverse=True):
        tarball = candidate
        break
    if not tarball:
        raise RuntimeError("no tarball for linux-" + version)
    shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True)
    run(["tar", "-xf", str(tarball), "-C", str(workdir)])
    dirs = list(workdir.glob("linux-" + version + "*"))
    if not dirs:
        raise RuntimeError("extracted tree not found")
    base = workdir / "kernel-base"
    dirs[0].rename(base)
    generic_files = repo / "target/linux/generic/files"
    if generic_files.is_dir():
        run(["cp", "-a", str(generic_files) + "/.", str(base) + "/"])
    return base


def materialise_target(repo, target, workdir):
    dest = workdir / "target/linux" / target
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    archive = subprocess.Popen(["git", "-C", str(repo), "archive", target, "target/linux/" + target], stdout=subprocess.PIPE)
    extract = subprocess.Popen(["tar", "-xf", "-", "-C", str(workdir)], stdin=archive.stdout)
    archive.stdout.close()
    extract.communicate()
    return dest


def replay_generic(base, files):
    result = {"patches": len(files), "offset": [], "fuzz": [], "failed": [], "skipped": []}
    for patch in files:
        rc, out = apply_patch(base, patch)
        info = scan_output(out)
        if info["offset"]:
            result["offset"].append(patch.name)
        if info["fuzz"]:
            result["fuzz"].append(patch.name)
        if info["skipped"]:
            result["skipped"].append(patch.name)
        if rc or info["failed"]:
            result["failed"].append(patch.name)
    return result


def replay_target(base, target_dir, version):
    patches = sorted((target_dir / ("patches-" + version)).glob("*.patch")) if (target_dir / ("patches-" + version)).is_dir() else []
    res = {"target": target_dir.name, "patches": len(patches), "offset": [], "fuzz": [], "failed": [], "skipped": []}
    for patch in patches:
        rc, out = apply_patch(base, patch)
        info = scan_output(out)
        if info["offset"]:
            res["offset"].append(patch.name)
        if info["fuzz"]:
            res["fuzz"].append(patch.name)
        if info["skipped"]:
            res["skipped"].append(patch.name)
        if rc or info["failed"]:
            res["failed"].append(patch.name)
            break
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="7.3")
    parser.add_argument("--base", default="generic")
    parser.add_argument("--targets", nargs="*")
    parser.add_argument("--workdir", default="/tmp/opencode/kernel-migration/replay")
    parser.add_argument("--generic-only", action="store_true")
    args = parser.parse_args()
    repo = root()
    version = full_version(args.version, repo)
    base_version = args.version
    workdir = Path(args.workdir)
    base = extract_base(repo, version, workdir)
    result = {"version": version, "generic": replay_generic(base, patch_files(base_version, repo))}
    if not args.generic_only:
        targets = args.targets or branches(repo, exclude=("generic", "openwrt618"))
        for target in targets:
            tree = workdir / ("kernel-" + target)
            if tree.exists():
                shutil.rmtree(tree)
            shutil.copytree(base, tree, copy_function=shutil.copy2, symlinks=True)
            target_dir = materialise_target(repo, target, workdir)
            for name in ("files", "files-" + base_version):
                src = target_dir / name
                if src.is_dir():
                    subprocess.run(["cp", "-a", str(src) + "/.", str(tree) + "/"], check=True)
            result.setdefault("targets", []).append(replay_target(tree, target_dir, base_version))
            shutil.rmtree(tree, ignore_errors=True)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
