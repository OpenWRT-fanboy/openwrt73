#!/usr/bin/env python3
import argparse
import glob
import re
import shutil
import subprocess
from pathlib import Path
from common import config_filter_patterns, full_version, git, is_filtered, root


def merge_configs(repo, target, subtarget, version, workdir):
    inputs = []
    generic = repo / "target/linux/generic" / ("config-" + version)
    if generic.is_file():
        inputs.append(generic)
    paths = [
        "target/linux/" + target + "/config-" + version,
        "target/linux/" + target + "/" + subtarget + "/config-default",
        "target/linux/" + target + "/" + subtarget + "/config-" + version,
    ]
    for idx, path in enumerate(paths):
        text = git("show", "HEAD:" + path, repo=repo, check=False)
        if text:
            out = workdir / ("input-" + str(idx) + ".cfg")
            out.write_text(text)
            inputs.append(out)
    merged = workdir / "target.cfg"
    cmd = [str(repo / "scripts/kconfig.pl")] + ["+"] * (len(inputs) - 1) + [str(p) for p in inputs]
    subprocess.run(cmd, stdout=open(merged, "wb"), check=True)
    override = workdir / "override.cfg"
    cmd = [str(repo / "scripts/package-metadata.pl"), "kconfig", str(repo / "tmp/.packageinfo"), str(repo / ".config"), version]
    subprocess.run(cmd, stdout=open(override, "wb"), check=True)
    final = workdir / "merged.cfg"
    subprocess.run([str(repo / "scripts/kconfig.pl"), "m+", "+", str(merged), "/dev/null", str(override)], stdout=open(final, "wb"), check=True)
    return final


def find_build_tree(repo, target, subtarget, version):
    pattern = str(repo / ("build_dir/target-*/linux-" + target + "_" + subtarget + "/linux-" + version + "*"))
    found = sorted(glob.glob(pattern))
    if not found:
        raise RuntimeError("no build tree for " + target + "/" + subtarget)
    return Path(found[0])


def kernel_arch(repo, target, subtarget):
    archmap = {
        "aarch64": "arm64", "arm": "arm", "armeb": "arm", "mips": "mips", "mipsel": "mips",
        "mips64": "mips", "mips64el": "mips", "loongarch64": "loongarch",
        "powerpc": "powerpc", "powerpc64": "powerpc", "riscv64": "riscv", "x86_64": "x86",
    }
    arch = None
    for path in ("target/linux/" + target + "/Makefile", "target/linux/" + target + "/" + subtarget + "/target.mk"):
        text = git("show", "HEAD:" + path, repo=repo)
        match = re.search(r"^ARCH\s*:?=\s*(\S+)", text, re.M)
        if match:
            arch = match.group(1)
    return archmap.get(arch, arch or "arm")


def collect_prompts(log, merged, patterns):
    text = log.read_text(errors="replace")
    syms = set(re.findall(r"\(([0-9A-Z][A-Z0-9_]*)\)[^)]*\(NEW\)", text))
    syms |= set(re.findall(r"\(([0-9A-Z][A-Z0-9_]*)\) \(NEW\)", text))
    resolved = {}
    for line in merged.read_text(errors="replace").splitlines():
        match = re.match(r"#?\s*CONFIG_([A-Za-z0-9_]+)", line)
        if match and match.group(1) in syms and not is_filtered(line, patterns):
            resolved[match.group(1)] = line.strip()
    return resolved


def write_symbols(path, resolved):
    lines = path.read_text(errors="replace").splitlines()
    for sym, value in resolved.items():
        lines = [line for line in lines if not re.match(r"#?\s*CONFIG_" + re.escape(sym) + r"\b", line)]
        lines.append(value)
    path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("subtarget")
    parser.add_argument("--version", default="7.3")
    parser.add_argument("--workdir", default="/tmp/opencode/kernel-migration/kconfig")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    repo = root()
    full = full_version(args.version, repo)
    workdir = Path(args.workdir)
    shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True)
    merged = merge_configs(repo, args.target, args.subtarget, args.version, workdir)
    build_tree = find_build_tree(repo, args.target, args.subtarget, full)
    scratch = workdir / "kernel"
    shutil.copytree(build_tree, scratch, copy_function=shutil.copy2, symlinks=True)
    log = workdir / "oldconfig.log"
    cmd = "yes '' | make -s -C " + str(scratch) + " ARCH=" + kernel_arch(repo, args.target, args.subtarget) + " KCONFIG_CONFIG=" + str(merged) + " oldconfig"
    with open(log, "wb") as lf:
        subprocess.run(["bash", "-c", cmd], stdout=lf, stderr=subprocess.STDOUT)
    resolved = collect_prompts(log, merged, config_filter_patterns(repo))
    own = repo / "target/linux" / args.target / ("config-" + args.version)
    if not own.is_file():
        own = repo / "target/linux" / args.target / args.subtarget / ("config-" + args.version)
    print(args.target, args.subtarget, "prompts", len(resolved))
    if not args.dry_run and resolved:
        write_symbols(own, resolved)
        print("added", len(resolved), "to", own.relative_to(repo))


if __name__ == "__main__":
    main()
