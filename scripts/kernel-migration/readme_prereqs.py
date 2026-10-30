#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from common import commits_since, commit_subject, git, root


def patch_changes(commits, repo):
    changes = {"D": [], "A": [], "M": []}
    for c in commits[1:]:
        if "readme" in commit_subject(c, repo).lower():
            continue
        for line in git("diff-tree", "--no-commit-id", "--name-status", "-r", c, repo=repo).splitlines():
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            status, path = parts
            if status in changes and "/patches-" in path and path.endswith(".patch"):
                name = path.split("/")[-1]
                if name not in changes[status]:
                    changes[status].append(name)
    return changes


def config_count(commits, version, repo):
    matches = [c for c in commits if "(4/4)" in commit_subject(c, repo)]
    if not matches:
        return 0
    c4 = matches[0]
    syms = set()
    for line in git("diff-tree", "--no-commit-id", "--name-status", "-r", c4, repo=repo).splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        status, path = parts
        if status not in ("A", "M") or "config-" + version not in path:
            continue
        diff = git("diff", c4 + "^", c4, "--", path, repo=repo)
        syms.update(re.findall(r"^\+(?:# )?(CONFIG_[A-Za-z0-9_]+)", diff, re.M))
    return len(syms)


def name_list(names):
    return [f"    `{name}`" + ("," if i < len(names) - 1 else ".") for i, name in enumerate(names)]


def rewrite_section(section, target, version, changes, count):
    lines = section.split("\n")
    idx = [i for i, line in enumerate(lines) if line.startswith("- ")]
    intro = lines[:idx[0]] if idx else lines[:]
    blocks = []
    for j, i in enumerate(idx):
        end = idx[j + 1] if j + 1 < len(idx) else len(lines)
        blocks.append(lines[i:end])
    out = []
    patch_head = "- `target/linux/" + target + "/patches-" + version + "`"
    config_head = "- `target/linux/" + target + "/config-" + version
    for block in blocks:
        head = block[0]
        if head.startswith(patch_head):
            new = [head]
            if changes["D"]:
                label = "backport" if len(changes["D"]) == 1 else "backports"
                new += ["  - " + str(len(changes["D"])) + " outdated " + label + " removed (now upstream in " + version + " or versioned backports):"] + name_list(changes["D"])
            if changes["A"]:
                label = "patch" if len(changes["A"]) == 1 else "patches"
                new += ["  - " + str(len(changes["A"])) + " new " + label + " added:"] + name_list(changes["A"])
            if changes["M"]:
                label = "patch" if len(changes["M"]) == 1 else "patches"
                new += ["  - " + str(len(changes["M"])) + " " + label + " refreshed to apply cleanly on " + version + " against the generic backport/pending/hack set:"] + name_list(changes["M"])
            while new and new[-1] == "":
                new.pop()
            new.append("")
            out += new
        elif head.startswith("- `target/linux/" + target + "/") and ("config-" + version) in head:
            out += [head, "  - " + str(count) + " new defaults appended to config-" + version + " (unique `CONFIG_*` symbols added in 4/4).", ""]
        else:
            out += block
    return "\n".join(intro + out).rstrip() + "\n"


def rewrite(target, base, version, repo):
    commits = commits_since(base, target, repo)
    text = git("show", target + ":readme." + target + ".md", repo=repo)
    parts = text.split("## Kernel and target prerequisites", 1)
    if len(parts) != 2:
        raise RuntimeError("missing prerequisites section for " + target)
    rest = parts[1].split("\n## ", 1)
    if len(rest) != 2:
        raise RuntimeError("missing next section for " + target)
    section = rewrite_section(rest[0], target, version, patch_changes(commits, repo), config_count(commits, version, repo))
    return parts[0] + "## Kernel and target prerequisites" + section + "\n## " + rest[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="+")
    parser.add_argument("--base", default="generic")
    parser.add_argument("--version", default="7.3")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    repo = root()
    for target in args.targets:
        text = rewrite(target, args.base, args.version, repo)
        if args.write:
            path = repo / ("readme." + target + ".md")
            path.write_text(text)
            print("updated", path.relative_to(repo))
        else:
            print(text)


if __name__ == "__main__":
    main()
