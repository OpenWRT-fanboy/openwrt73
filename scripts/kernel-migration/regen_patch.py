#!/usr/bin/env python3
import argparse
import glob
import os
import re
import shutil
import subprocess
from pathlib import Path
from common import full_version, patch_dirs, root


def run(cmd, cwd=None, stdin=None, check=False):
    kwargs = {"cwd": str(cwd) if cwd else None, "stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
    if stdin is not None:
        kwargs["stdin"] = stdin
    result = subprocess.run(cmd, **kwargs)
    if check and result.returncode:
        raise RuntimeError(" ".join(map(str, cmd)) + "\n" + result.stdout.decode(errors="replace"))
    return result


def tarball(repo, version):
    found = sorted(repo.glob("dl/linux-" + version + "*.tar.xz"), reverse=True)
    if not found:
        raise RuntimeError("no tarball for linux-" + version)
    return found[0]


def current_branch(repo):
    out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE, check=True)
    return out.stdout.decode().strip()


def materialize(repo, branch, rel, dest):
    proc = subprocess.run(["git", "-C", str(repo), "archive", branch, rel], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode:
        return
    if not proc.stdout:
        return
    p = subprocess.run(["tar", "-x", "-C", str(dest)], input=proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError("materialize failed: " + rel + "\n" + p.stderr.decode(errors="replace"))


def build_base(repo, version, workdir, target=None, branch=None, short_version=None):
    shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True)
    run(["tar", "-xf", str(tarball(repo, version)), "-C", str(workdir)], check=True)
    dirs = list(workdir.glob("linux-" + version + "*"))
    if not dirs:
        raise RuntimeError("extracted tree not found")
    base = workdir / "kernel"
    dirs[0].rename(base)
    generic_files = repo / "target/linux/generic/files"
    if generic_files.is_dir():
        run(["cp", "-a", str(generic_files) + "/.", str(base) + "/"], check=True)
    if target:
        for suffix in ("files", "files-" + (short_version or version)):
            stage = workdir / ("stage-" + suffix)
            materialize(repo, branch, "target/linux/" + target + "/" + suffix, workdir)
            staged = workdir / ("target/linux/" + target + "/" + suffix)
            if staged.is_dir():
                run(["cp", "-a", str(staged) + "/.", str(base) + "/"], check=True)
                shutil.rmtree(workdir / "target", ignore_errors=True)
    return base


def apply_one(tree, patch, fuzz=None):
    cmd = ["patch", "-f", "-p1", "-d", str(tree)]
    if fuzz is not None:
        cmd.insert(1, "-F" + str(fuzz))
    with open(patch, "rb") as fh:
        result = run(cmd, stdin=fh)
    return result.returncode, result.stdout.decode(errors="replace")


def touched_paths(raw):
    paths = []
    for line in raw.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:].split("\t")[0]
            if path not in paths:
                paths.append(path)
    return paths


def diff_one(old, new, path, created):
    label_old = "/dev/null" if created else "a/" + path
    old_path = "/dev/null" if created else str(old)
    cmd = ["diff", "-u", "--label", label_old, "--label", "b/" + path, old_path, str(new)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout.decode(errors="replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("patch")
    parser.add_argument("--edit")
    parser.add_argument("--version", default="7.3")
    parser.add_argument("--fuzz", type=int, default=3)
    parser.add_argument("--target")
    parser.add_argument("--workdir", default="/tmp/opencode/kernel-migration/regen")
    args = parser.parse_args()
    repo = root()
    version = full_version(args.version, repo)
    branch = current_branch(repo)
    patch = None
    if args.target:
        directory = repo / "target/linux" / args.target / ("patches-" + args.version)
        candidate = directory / args.patch
        if candidate.is_file():
            patch = candidate
    else:
        for directory in patch_dirs(args.version, repo):
            candidate = directory / args.patch
            if candidate.is_file():
                patch = candidate
                break
    if not patch:
        raise SystemExit("patch not found: " + args.patch)
    raw = patch.read_text(errors="replace")
    workdir = Path(args.workdir)
    base = build_base(repo, version, workdir, args.target, branch, args.version)
    generic = [p for d in patch_dirs(args.version, repo) if d.is_dir() for p in sorted(d.glob("*.patch"))]
    if args.target:
        staged = workdir / "target-patches"
        staged.mkdir(exist_ok=True)
        materialize(repo, branch, "target/linux/" + args.target + "/patches-" + args.version, staged)
        target_dir = staged / ("target/linux/" + args.target + "/patches-" + args.version)
        files = generic + (sorted(target_dir.glob("*.patch")) if target_dir.is_dir() else [])
    else:
        files = generic
    idx = [i for i, p in enumerate(files) if p.name == args.patch]
    if len(idx) != 1:
        raise SystemExit("patch not unique in series: " + args.patch)
    for preceding in files[:idx[0]]:
        rc, out = apply_one(base, preceding)
        if rc:
            raise SystemExit("predecessor failed " + preceding.name + "\n" + out[:500])
    snapdir = workdir / "snap"
    shutil.rmtree(snapdir, ignore_errors=True)
    paths = touched_paths(raw)
    created = []
    for path in paths:
        src = base / path
        dst = snapdir / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dst)
        else:
            created.append(path)
    rc, out = apply_one(base, patch, args.fuzz)
    print("apply rc", rc)
    print(out[-300:])
    if (rc or "FAILED" in out or "****" in out) and not args.edit:
        raise SystemExit("patch has failed hunks; use --edit to apply source fixes")
    if args.edit:
        namespace = {"post": base, "base": base, "pre": snapdir}
        exec(Path(args.edit).read_text(errors="replace"), namespace)
    idx = raw.find("\n--- a/")
    if idx < 0:
        idx = raw.find("\n--- /dev/null")
    if idx < 0:
        raise SystemExit("no diff header")
    header = raw[:idx + 1]
    body = "".join(diff_one(snapdir / path, base / path, path, path in created) for path in paths)
    text = header + body
    if not text.endswith("\n"):
        text += "\n"
    for path in paths:
        dst = base / path
        src = snapdir / path
        if path in created:
            if dst.is_file():
                dst.unlink()
        elif src.is_file():
            shutil.copy2(src, dst)
    patch.write_text(text)
    rc, out = apply_one(base, patch)
    bad = "fuzz" in out or "FAILED" in out or "****" in out or rc != 0
    print("verify rc", rc, "fuzz", len(re.findall(r"with fuzz", out)), "failed", "FAILED" in out or "****" in out)
    if bad:
        raise SystemExit(out[:800])


if __name__ == "__main__":
    main()
