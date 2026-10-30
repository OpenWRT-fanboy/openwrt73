#!/usr/bin/env python3
import argparse
import json
import re
from common import branches, commits_since, commit_subject, git, readme_section, root


def parse_exceptions(values):
    out = {}
    for v in values or []:
        if "=" in v:
            name, count = v.split("=", 1)
            out[name] = int(count)
    return out


def patch_changes(commits, repo):
    changes = {}
    for c in commits[1:]:
        if "readme" in commit_subject(c, repo).lower():
            continue
        for line in git("diff-tree", "--no-commit-id", "--name-status", "-r", c, repo=repo).splitlines():
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            status, path = parts
            if status in ("A", "M", "D") and "/patches-" in path and path.endswith(".patch"):
                changes[path.split("/")[-1]] = status
    return changes


def config_count(commits, version, repo):
    if not commits:
        return 0
    c4 = [c for c in commits if "(4/4)" in commit_subject(c, repo)]
    if not c4:
        return None
    c4 = c4[0]
    syms = set()
    for line in git("diff-tree", "--no-commit-id", "--name-status", "-r", c4, repo=repo).splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        status, path = parts
        if status not in ("A", "M") or "config-" not in path:
            continue
        diff = git("diff", c4 + "^", c4, "--", path, repo=repo)
        syms.update(re.findall(r"^\+(?:# )?(CONFIG_[A-Za-z0-9_]+)", diff, re.M))
    return len(syms)


def readme_claims(section, target, version):
    lines = section.split("\n")
    idx = [i for i, line in enumerate(lines) if line.startswith("- ")]
    blocks = []
    for j, i in enumerate(idx):
        end = idx[j + 1] if j + 1 < len(idx) else len(lines)
        blocks.append(lines[i:end])
    patch_block = next((b for b in blocks if b[0].startswith("- `target/linux/" + target + "/patches-" + version + "`")), [])
    claimed = set(re.findall(r"`([^`]+\.patch)`", "\n".join(patch_block)))
    match = re.search(r"(\d+) new defaults appended", section)
    count = int(match.group(1)) if match else None
    return claimed, count


def tested_seeds(target, repo):
    text = git("show", target + ":readme." + target + ".md", repo=repo)
    tested = set(re.findall(r"^- `([^`]+)` —", text, re.M))
    seeds = {s for s in git("ls-tree", "--name-only", target, repo=repo).split() if re.fullmatch(r"knowngood\d*\.config", s)}
    return tested, seeds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="generic")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--version", default="7.3")
    parser.add_argument("--exceptions", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo = root()
    exceptions = parse_exceptions(args.exceptions)
    excludes = set(args.exclude) | {"openwrt618"}
    issues = []
    targets = branches(repo, exclude=excludes | {args.base})
    for target in targets:
        commits = commits_since(args.base, target, repo)
        expected = exceptions.get(target, 5)
        if len(commits) != expected:
            issues.append([target, "commit-count", len(commits), expected])
        for tag, flag in (("(2/4)", "A"), ("(3/4)", "D")):
            matches = [c for c in commits if tag in commit_subject(c, repo)]
            if not matches:
                issues.append([target, tag, "missing"])
                continue
            for line in git("diff-tree", "--no-commit-id", "--name-status", "-r", matches[0], repo=repo).splitlines():
                parts = line.split("\t", 1)
                if len(parts) == 2 and parts[0] == flag and "/patches-" in parts[1]:
                    issues.append([target, tag, "placement", parts[1]])
                    break
        section = readme_section(target, repo)
        if not section:
            issues.append([target, "readme-section", "missing"])
            continue
        claimed, claim_count = readme_claims(section, target, args.version)
        actual = patch_changes(commits, repo)
        if claimed != set(actual):
            issues.append([target, "patch-list", sorted(claimed - set(actual))[:5], sorted(set(actual) - claimed)[:5]])
        cfg_count = config_count(commits, args.version, repo)
        if claim_count != cfg_count:
            issues.append([target, "config-count", claim_count, cfg_count])
        tested, seeds = tested_seeds(target, repo)
        if len(tested) != len(seeds):
            issues.append([target, "seed-coverage", len(tested), len(seeds)])
    result = {"branches": len(targets), "issues": issues}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("branches", result["branches"], "issues", len(issues))
        for issue in issues:
            print(issue)


if __name__ == "__main__":
    main()
