#!/usr/bin/env python3
import argparse
from pathlib import Path
from common import branches, commits_since, commit_subject, git, root


def save(outfile, repo):
    lines = []
    for branch in branches(repo):
        lines.append(branch + " " + git("rev-parse", branch, repo=repo))
    Path(outfile).write_text("\n".join(lines) + "\n")
    print("saved", len(lines), "branches to", outfile)


def verify(base, exceptions, repo):
    expected = {}
    for item in exceptions or []:
        if "=" in item:
            name, count = item.split("=", 1)
            expected[name] = int(count)
    issues = []
    for branch in branches(repo, exclude=(base, "openwrt618")):
        count = len(commits_since(base, branch, repo))
        want = expected.get(branch, 5)
        if count != want:
            issues.append([branch, "commit-count", count, want])
    print("issues", len(issues))
    for issue in issues:
        print(issue)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    save_parser = sub.add_parser("save")
    save_parser.add_argument("outfile")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--base", default="generic")
    verify_parser.add_argument("--exceptions", action="append", default=[])
    args = parser.parse_args()
    repo = root()
    if args.cmd == "save":
        save(args.outfile, repo)
    else:
        verify(args.base, args.exceptions, repo)


if __name__ == "__main__":
    main()
