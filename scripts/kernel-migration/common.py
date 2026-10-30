#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path


def root():
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return Path(out.stdout.decode().strip())


def git(*args, repo=None, check=True):
    cmd = ["git", "-C", str(repo or root())] + [str(a) for a in args]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)
    if not check and out.returncode:
        return ""
    return out.stdout.decode(errors="replace")


def git_bytes(*args, repo=None, check=True):
    cmd = ["git", "-C", str(repo or root())] + [str(a) for a in args]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)
    return out.stdout


def branches(repo=None, exclude=()):
    names = git("for-each-ref", "--format=%(refname:short)", "refs/heads/", repo=repo).split()
    return sorted(n for n in names if n not in exclude)


def full_version(version, repo=None):
    path = (repo or root()) / "target/linux/generic" / ("kernel-" + version)
    text = path.read_text(errors="replace")
    match = re.search(r"^LINUX_VERSION-" + re.escape(version) + r"\s*=\s*(\S*)", text, re.M)
    suffix = match.group(1).strip() if match else ""
    if suffix.startswith("-"):
        return version + suffix
    if suffix:
        return version + suffix if suffix.startswith(".") else version + "-" + suffix
    return version


def patch_dirs(version, repo=None):
    repo = repo or root()
    return [repo / "target/linux/generic" / (d + "-" + version) for d in ("backport", "pending", "hack")]


def patch_files(version, repo=None):
    files = []
    for d in patch_dirs(version, repo):
        if d.is_dir():
            files.extend(sorted(d.glob("*.patch")))
    return files


def config_filter_patterns(repo=None):
    repo = repo or root()
    patterns = []
    path = repo / "target/linux/generic/config-filter"
    if not path.is_file():
        return patterns
    for line in path.read_text(errors="replace").splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("# CONFIG_") and line.endswith(" is not set"):
            pat = line[len("# "):-len(" is not set")]
            patterns.append(re.compile("^" + pat + " is not set$"))
        elif line.startswith("CONFIG_") and "=" in line:
            patterns.append(re.compile("^" + line.split("=", 1)[0] + "="))
    return patterns


def is_filtered(line, patterns):
    line = line.rstrip("\n")
    return any(p.match(line) for p in patterns)


def commit_subject(commit, repo=None):
    return git("log", "-1", "--format=%s", commit, repo=repo).strip()


def commits_since(base, branch, repo=None):
    return git("rev-list", "--reverse", base + ".." + branch, repo=repo).split()


def readme_section(branch, repo=None):
    text = git("show", branch + ":readme." + branch + ".md", repo=repo)
    rest = text.split("## Kernel and target prerequisites", 1)
    if len(rest) != 2:
        return None
    return rest[1].split("\n## ", 1)[0]
