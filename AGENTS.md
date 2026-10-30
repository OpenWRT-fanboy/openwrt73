# Agent working notes — OpenWrt kernel migration

This is a reusable playbook for moving OpenWrt targets from an old LTS kernel
(`<old>`) to a newer one (`<new>`). The current 7.3 migration is complete;
use it as the reference implementation, not as a fixed set of SHAs.

Local `generic` is the authoritative baseline. `x86` is the base target and must
carry x86-specific changes; generic must not carry base-target-only files.
Plan, status, and known-broken packages live in `KERNEL-<new>.md`; the current
example is `KERNEL-7.3.md`.

Local overrides: this file wins over the agent's generic defaults on conflict.

## Working method

- Cite `file:line`; never cite your own summary. Re-read the source before
  asserting what a patch or register does.
- Attribute before confessing: check pristine upstream / `git show` before
  blaming a patch — offsets and patch-size deltas lie.
- When build output contradicts the sources on disk, suspect stale
  `build_dir/` first: clean the affected package and rebuild before theorizing.
- Before writing a patch, enumerate 2-3 candidate mechanisms and pick the
  smallest diff that carries the design.
- `build_dir/` is not a stable reference. Copy files out before analysing and
  re-check mtime/diff before quoting a line number read minutes earlier.
- NEVER build scratch kernel trees with `cp -al` / hardlinks: a single in-place
  write silently corrupts the shared "pristine" source and invalidates every
  later patch/verify result. Use `cp -a`. Re-extract from `dl/linux-*.tar.xz`
  and `diff -rq` against a fresh extraction if a base tree is ever suspect.
- Never silently replace a user artifact: back it up, say where, say why.
- Enumerate small sets completely; sampling is for large sets only, then state
  the basis.
- Scratch work goes in `/tmp/opencode` (pre-approved). `/tmp` is a 7.9G tmpfs
  and a full kernel tree is ~1.8G: clean scratch trees after each target, and
  remove `build_dir/toolchain-*` (~4G each) after `staging_dir/toolchain-*`
  is installed, or parallel targets will exhaust disk/inodes. Keep at least
  5G free on `/`; stop and clean before the next build if below that.
- Before any history rewrite, save all old branch heads with names, e.g.
  `git rev-parse <branch> >> /tmp/opencode/heads.txt`. `git reflog` tail is
  not a reliable "before" baseline.
- Do not start compile builds unless explicitly asked. Non-compiling audits
  and `make kernel_oldconfig` are allowed when needed for verification.

## Reusable workflow: generic first, then targets

For a future kernel or newer upstream:

1. Update `generic` first: copy generic patches/config, classify and delete
   obsolete backports, refresh/regenerate remaining patches, then update
   kernel version, build system, and generic config.
2. Rebase/rebuild each target from the updated `generic`, using its existing
   branch as advisory content where the `<old>` patch is unchanged upstream.
3. Re-run audits (patch placement, readmes, seeds) after each history rewrite.
4. Compile only when requested.

Never hand-write or hand-edit patch hunks. Edit the code (or a scratch copy),
then generate hunks with canonical `diff -u` / `git diff`.

A patch's base is "the tree produced by all preceding patches". Reconstruct
that in `/tmp`; never generate against a tree you did not produce, never
against the live `build_dir/`. The base is pristine `<new>` + generic files +
generic backport/pending/hack-<new> patches + the target's `files/` and
`files-<new>/` (OpenWrt copies files before patches — see `include/quilt.mk`).
A scan that omits them reports false pass/fail.

Prefer zero offsets; an offset means the base is stale. Refresh to a fixed
point and replay the whole series until no patch shows offset/fuzz. If an
explicit override tolerates offsets in untouched patches, record it; fuzz and
FAILED remain unacceptable. A clean replay is necessary but NOT sufficient:
alignment-based rebases can apply cleanly yet insert code in the wrong
function or outside it. Only a compile catches that class of error.

After any patch edit, verify hunk counts from the bodies, run `patch --dry-run`,
compute the diffstat, and compare the patch with the `<old>` counterpart.
A diffstat/body mismatch is a strong signal that a hunk was dropped.
Run `scripts/checkpatch.pl --no-tree` on new/changed hunks; clear ERRORs
(OpenWrt SOB/header noise excepted), and compare ERROR counts against the
old-kernel counterpart to separate inherited noise from new errors.
Patch files end with a newline. Satisfy both `patch` and `git apply`.

Patch placement: extend the patch that owns adjacent logic; stand alone when
touching pristine upstream code. Never duplicate upstream content or graft
unrelated behaviour onto someone else's patch. One invariant, one
implementation. Prefer an existing carrier over new plumbing; list callers
before changing a signature.

### Obsolete-patch detection

Do not rely on version prefixes alone. A patch is obsolete only if its unique
change is present in pristine `<new>`. Useful signals:

- reverse-application (`patch -R --dry-run`) succeeds on pristine `<new>`;
- all added code lines are already present in the affected source file;
- version-prefixed backports `< v<new>` whose subject/sha landed upstream.

A failed hunk is not proof of obsolescence: the new kernel may have moved the
surrounding nodes/helpers. Rebase unless the unique change exists upstream.

## Rebuilding generic

Use the current `generic` branch and `KERNEL-<new>.md` as advisory, but
re-derive content from pristine `<new>` and the actual upstream diff.

The four commits should be:

1. `<generic> <new> (1/4): copy patches and config from <old>`
   - Copy generic `backport-<old>`, `pending-<old>`, `hack-<old>` to `<new>`.
   - Copy `target/linux/generic/config-<old>` to `config-<new>`.
   - Do not copy target-specific configs or base-target files here.
2. `<generic> <new> (2/4): delete outdated backports`
   - Delete only patches confirmed upstream in `<new>`.
3. `<generic> <new> (3/4): update patches`
   - Reuse the advisory branch's `<new>` patch content only when the `<old>`
     source is unchanged. If upstream changed the `<old>` patch, regenerate
     from the exact `<new>` base instead of copying the old forward-port.
   - Keep generic API signatures consistent with package call sites.
4. `<generic> <new> (4/4): fix configuration`
   - Add `target/linux/generic/kernel-<new>` (version and hash).
   - Apply generic build-system changes (`include/kernel.mk`,
     `include/image.mk`, `config-filter`, package kernel module `.mk` files).
   - Add `KERNEL_TESTING_PATCHVER` for the base target in the base target
     branch, not in generic.

Feed fixes belong in generic as `target/linux/generic/hack-<new>/*-kernel-<new>.patch`
meta-patches that materialise feed patches. `feeds/` is git-ignored and lost on
feeds update; feed breakage itself is fixed upstream in the feeds.

## Rebuilding a target

The kernel move is four commits per target, in this order. Use the existing
target branch as advisory content, but re-derive from current generic and
pristine `<new>`. `bcm53xx` is the primary reference for branch shape, not an
immutable commit; if unusual, inspect other migrated branches.

1. `<target> <new> (1/4): copy patches and config from <old>`
   - Baseline is local `generic`, never a remote-tracking ref.
   - Copy `target/linux/<target>/patches-<old>` to `patches-<new>`.
   - Copy each subtarget `config-<old>` to `config-<new>` (or root config for
     single-config targets). Check renamed symbols between versions.
   - If `files-<old>/` exists, copy to `files-<new>/`. Unversioned `files/` is
     copied for every kernel version; do not duplicate it.
2. `<target> <new> (2/4): delete outdated backports`
   - Deletions only. Move late-discovered deletions into this commit, not 3/4.
3. `<target> <new> (3/4): update patches`
   - Additions and modifications only. Regenerate changed/new patches from
     the correct base; reuse advisory `<new>` versions when `<old>` unchanged.
4. `<target> <new> (4/4): fix configuration`
   - Set `KERNEL_TESTING_PATCHVER:=<new>` alongside unchanged
     `KERNEL_PATCHVER:=<old>`.
   - Edit `config-<new>` files; do not add them wholesale here if 1/4 already
     copied them. Config edits belong in 4/4, not 1/4.
   - If the build reports `Missing kernel version/hash file for .`, check that
     `KERNEL_TESTING_PATCHVER` is set, not `kernel-<new>`.

Empty 2/4 or 3/4 commits are valid. Coverage check: compare
`git ls-tree --name-only generic:target/linux` with the distribution's target
index; every non-generic target except the base target needs a branch.

## Kconfig sweep

NEVER discover new symbols by compiling: non-interactive `syncconfig` stops at
the first `(NEW)` prompt. Use one non-compiling `make kernel_oldconfig` pass
per target/subtarget with a device-selected seed.

- Merge the same inputs OpenWrt uses with `scripts/kconfig.pl`, including the
  filtered `.config` from `make defconfig` when symbols are only visible under
  `CONFIG_TESTING_KERNEL` or the selected target.
- Get ARCH from target/subtarget Makefiles; map OpenWrt names to kernel ARCH
  names (e.g. aarch64→arm64, mipsel→mips, riscv64→riscv, x86_64→x86).
- In a scratch kernel tree made with `cp -a`, run:
  `yes '' | make -s -C <scratch> ARCH=<arch> KCONFIG_CONFIG=<merged> oldconfig`.
- Add only symbols that appeared as `(NEW)` and survived
  `target/linux/generic/config-filter`. Include digit-prefixed symbols and
  choice prompts (`[0-9A-Z]`). Do not add every symbol resolved in a full
  generated kernel config; that creates huge, unnecessary config deltas.
- If a choice resolves silently in oldconfig but syncconfig still prompts,
  take the resolved value from the build tree `.config`.
- Helpers sweeping multiple subtargets must read already-edited working-tree
  configs, not only `git show <branch>:path`.
- De-duplicate `config-<new>`: exactly one line per `CONFIG_<symbol>`.
- When adding a family of defaults, never overwrite a symbol already set.
- Finish the sweep before creating the readme; regenerate readme counts from
  final diffs if config changes later.

## History rewrites and rebases

- Save old heads with names before rewriting.
- Derive a branch's old base from its 1/4 commit parent; do not assume a SHA
  from earlier in the session. Wrong-base rebases can silently replay unrelated
  upstream commits and conflict in target files.
- Use `git rebase --onto <new-generic> <old-base> <branch>` and replay commits
  sequentially. Resolve conflicts by preserving newer upstream content unless
  the target change is intentional.
- If a wrong-base rewrite happened, restore from saved heads and redo.
- Verify after every rewrite: `git log`, `git status`, commit count, branch
  ancestry, readme/seed file list, and placement (2/4 deletions, 3/4
  additions/modifications).

## readme.<target>.md

Create/update per-target build notes once the four commits are done. Use
`readme.ramips.md` as the template.

- Modify only **Kernel and target prerequisites** to reflect actual changes:
  `KERNEL_TESTING_PATCHVER`, backports removed, patches refreshed/added,
  new config defaults, target-specific `Kernel/Prepare` tweaks.
- At the top list every compile-tested subtarget with the exact seed:
  `knowngood.config`, `knowngood2.config`, etc. Save that seed in the branch
  and link it from the readme.
- A seed must select an actual device: `CONFIG_TARGET_<board>=y`,
  `CONFIG_TARGET_<board>_<subtarget>=y`, and
  `CONFIG_TARGET_<board>_<subtarget>_DEVICE_<device>=y`. After
  `scripts/diffconfig.sh`, assert the DEVICE line is present. Targets with no
  devices (e.g. UML) are the exception.
- Regenerate prerequisite bullets from final commit diffs after any late
  patch/config commit.
- Keep **Feed packages that need patches** and **Materialising the feed
  patches** essentially unchanged.

## Kernel migration toolkit

Reusable helpers live in `scripts/kernel-migration/`. Run them from the repo
root; they derive the root from `git rev-parse --show-toplevel` and keep scratch
state under `/tmp/opencode/kernel-migration/` by default.

- `history.py save <file>`: save all branch heads with names before rewriting.
  `history.py verify --base <ref> [--exceptions name=count]`: check commit counts
  and readme tip subjects after rebases.
- `replay.py --version <ver> --generic-only`: replay the generic patch series on
  a fresh extracted kernel tree. Add `--targets <target> ...` to replay target
  series too. Reports fuzz/FAILED/offsets; no compile.
- `kconfig_sweep.py <target> <subtarget> --version <ver>`: after `make defconfig`
  and `make target/linux/prepare`, collect `(NEW)` prompts via oldconfig,
  apply `config-filter`, and write resolved values to the owning config.
  Use `--dry-run` to inspect without writing.
- `readme_prereqs.py <target> ... --version <ver> --write`: regenerate the
  prereq bullets from final commit diffs without changing other sections.
- `audit.py --base <ref> --exceptions name=count [--json]`: audit branch shape,
  placement, readme patch/config counts, and seed coverage.
- `regen_patch.py <patch-name> --version <ver> [--edit script]`: regenerate one
  generic patch from the exact preceding-patch base. Edit source in a scratch
  tree via `--edit`; never hand-edit hunks.
- `seed.py <branch> <seed> --write [--device ...]`: compact a seed with
  `scripts/diffconfig.sh` and assert a DEVICE line. Does not commit.

## Verification

- Ladder: dry-run < real apply < config sweep < compiles < runs once <
  re-entry/error paths. Never present a lower rung as a higher one.
- A zero-offset replay is NOT a compile. Compiles and runtime tests require
  explicit user instruction.
- Replay each patch series sequentially; compare final patch files after all
  refreshes, because refreshing predecessors can break later patches.
- Audit placement, readme counts/lists, seed coverage, and branch shape after
  history rewrites.
- Label handover confidence: proven (named test), inferred (named evidence),
  untested. An untested item never reads as done.
- Trust facts already established in `KERNEL-<new>.md` before re-deriving them.

## Environment facts

- Single git repo: OpenWrt tree at `~/openwrt73`.
- Full image builds are the user's job; do not start one unless asked.
- When compilation testing IS requested, `make -j8 target/linux/compile` with
  a minimal device-selected `defconfig` and `CONFIG_TESTING_KERNEL=y` is the
  rung that catches Kconfig, DTS, and kernel API breakage. Clean
  `build_dir/target-*/linux-<target>_*/linux-<new>.*` after each target.
- Single-TU compile is the cheapest rung for interface/Kconfig breakage: get
  the command line from `make -n <object>`, then swap in your file and a
  different `-o`. Hand-rolled `-fsyntax-only` is unreliable.
- Toolchains do not predefine `__GLIBC__`; guard aarch64-only code with
  `__aarch64__`.
- `bin/`, `build_dir/`, `staging_dir/` can be stale; clean before concluding
  anything about the code.
