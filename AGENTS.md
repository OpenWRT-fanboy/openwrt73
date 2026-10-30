# Agent working notes — OpenWrt kernel 6.18 → 7.3 migration

Focus: move targets from `KERNEL_PATCHVER:=6.18` to 7.3, mostly by porting
and refreshing target patches. `generic/` 7.3 and x86/64 are done and are the
reference; every other target is still on 6.18. Plan, 6.18 reference commits,
status log and known-broken packages live in `KERNEL-7.3.md`.

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
- Never silently replace a user artifact: back it up, say where, say why.
- Enumerate small sets completely; sampling is for large sets only, then state
  the basis.
- Scratch work goes in `/tmp/opencode` (pre-approved).

## Porting patches (the main work)
- NEVER hand-write or hand-edit patch hunks. Edit the code (or a scratch copy),
  then generate hunks with canonical `diff -u` / `git diff`.
- A patch's base is "the tree produced by all preceding patches". Reconstruct
  that in `/tmp`; never generate against a tree you did not produce, never
  against the live `build_dir/`.
- Prefer zero offsets. An offset means the base is stale: find the preceding
  patch that moved the target, regenerate, re-measure the series.
- After any edit, verify hunk counts from the bodies, run `patch --dry-run`
  (fuzz/FAILED is never acceptable), and compute the diffstat (`--stat`).
- A patch file carries the diff only; rationale belongs in the commit. Keep
  in-code comments that carry a non-obvious invariant.
- Run `scripts/checkpatch.pl --no-tree` on new/changed hunks; clear ERRORs
  (OpenWrt SOB/header noise excepted). `Documentation/process/coding-style.rst`
  is the style authority.
- Patch files end with a newline. `diff`/`git diff` exit 1 on differences and
  kill `&&` chains — use `;`. Satisfy both `patch` and `git apply`.
- Patch placement: extend the patch that owns adjacent logic; stand alone when
  touching pristine upstream code. Never duplicate upstream content or graft
  unrelated behaviour onto someone else's patch.
- Dropping a patch requires proof it is in 7.3 upstream (sha/subject). When a
  patch exists upstream, rebuild from the upstream original, not from the 6.18
  forward-port.
- A failed hunk is not proof a patch is obsolete: 7.3 may have moved the
  surrounding nodes/helpers into another file. Rebase unless the unique change
  exists in pristine 7.3.
- Refresh in series order with quilt: set up a scratch pristine 7.3 tree with
  `patches/series`, `quilt push` each patch, and run
  `QUILT_DIFF_OPTS="-p" quilt refresh -p ab --no-index --no-timestamps`
  (same invocation as `include/quilt.mk`) on patches showing offset/fuzz.
  Refreshing an earlier patch moves later hunk positions.
- Verify sequentially: a batch of `patch --dry-run` calls without applying
  each predecessor reports false offsets/fuzz. Use `quilt push`, or
  `patch --dry-run && patch` per patch, before claiming zero offsets.
- After restoring a patch with `git show` or resolving a merge, check for
  conflict markers, a missing diffstat/separator blank, and stale `@@`
  headers before trusting it.
- Back up `patches-<ver>/` before bulk edits; `git show <copy-commit>:path`
  recovers a deleted patch.
- One invariant, one implementation: fold drifting copies into one helper.
- Prefer an existing carrier (skb field, metadata, existing parameter, caller
  lock) over new plumbing; list every caller before changing a signature.

## Per-target migration
The 6.18 → 7.3 move is performed as four commits per target, in the exact
order used on the existing branches. Always use the existing branches as
the authoritative reference for what the commits contain and how they are
named. Do not invent steps; mirror the pattern found there.

1/4 copy patches and config from 6.18
- Create `target/linux/<target>/patches-7.3` from `patches-6.18`:
  `cp -a target/linux/<target>/patches-6.18/* target/linux/<target>/patches-7.3/`
- For each subtarget, copy the kernel config:
  `cp target/linux/<target>/<subtarget>/config-6.18 target/linux/<target>/<subtarget>/config-7.3`
  For targets with a single config, copy `target/linux/<target>/config-6.18`
  → `config-7.3`.
- Commit as `<target> 7.3 (1/4): copy patches and config from 6.18`
- Reference commits: ath79 7.3 (1/4), ipq806x 7.3 (1/4), ramips 7.3 (1/4),
  bcm53xx 7.3 (1/4), airoha 7.3 (1/4).

2/4 delete outdated backports
- In `target/linux/<target>/patches-7.3/`, remove patches that are now
  upstream in 7.3. These are typically version-prefixed backports
  `v6.19`, `v7.0`, `v7.1` etc. that were required for 6.18 but are merged.
- Identify candidates by comparing `patches-6.18` vs `patches-7.3` after the
  copy and by inspecting the existing branches for the exact files they
  removed. For mediatek the removed set includes
  `010-v7.0-mtd-spinand-...`, `046-v6.19-arm64-dts-mediatek...`, etc.
- Reliable obsolete-patch detection:
  * Clean the build tree: `rm -rf build_dir/target-*/linux-<target>_*/linux-7.3`
  * Build with `CONFIG_TESTING_KERNEL=y` until the first
    `Patch failed! Please fix` is hit.
  * Verify upstream presence: inspect the extracted 7.3 source in
    `build_dir/.../linux-7.3/` for the change the patch introduces. Use
    `grep -rn` for unique symbols / nodes / macros from the patch.
  * If the change is already present in the pristine 7.3 tree, the patch
    is redundant/obsolete – delete it from `patches-7.3/` and clean
    `build_dir/` before retrying. Do not regenerate hunks for a change that
    is already upstream.
  * Repeat until the series applies cleanly with quilt. This catches
    non-version-prefixed backports that have landed in 7.3.
- Commit as `<target> 7.3 (2/4): delete outdated backports`
- Reference commits: ath79 7.3 (2/4), ipq806x 7.3 (2/4), ramips 7.3 (2/4),
  bcm53xx 7.3 (2/4), airoha 7.3 (2/4).

3/4 update patches
- Ensure every patch in `patches-7.3` applies cleanly to the 7.3 kernel tree.
- Run `make target/linux/refresh` on a tree with 7.3 enabled, or regenerate
  failing patches manually from a scratch copy in `/tmp` with the correct
  base: “the tree produced by all preceding patches”. Never generate against
  `build_dir/`.
- Update hunks to reflect 7.3 context changes, keep patch count and
  `patch --dry-run` fuzz/FAILED = 0. Run `scripts/checkpatch.pl --no-tree`
  on changed hunks.
- Add a new patch only when the existing branches added one for the same
  reason.
- Verify header / implementation signature consistency for patches that change
  kernel APIs: generic backports that modify headers must be matched by a
  corresponding implementation update. Check macro argument counts against
  call sites in packages; add a minimal implementation patch if upstream 7.3
  has not yet updated the file.
- Verify includes for helpers moved to new headers in 7.3. When a backported
  driver uses such helpers, add the correct include to the patch rather than
  leaving an implicit declaration.
- Commit as `<target> 7.3 (3/4): update patches`
- Reference commits: ath79 7.3 (3/4), ipq806x 7.3 (3/4), ramips 7.3 (3/4),
  bcm53xx 7.3 (3/4), airoha 7.3 (3/4).

4/4 fix configuration
- Set `KERNEL_TESTING_PATCHVER:=7.3` in `target/linux/<target>/Makefile`
  alongside the existing `KERNEL_PATCHVER:=6.18`. Do not change the default
  `KERNEL_PATCHVER`.
- If the build reports `Missing kernel version/hash file for .`, the empty
  version means `KERNEL_TESTING_PATCHVER` is unset/empty in the target
  Makefile, not that `kernel-7.3` is missing (`include/kernel-version.mk`).
- Run `make kernel_oldconfig` with `CONFIG_TESTING_KERNEL=y` to import new
  symbols and drop removed ones. The config files are then updated to add
  `# CONFIG_... is not set` lines for symbols removed in 7.3.
- Update `target/linux/<target>/config-7.3` and/or each
  `target/linux/<target>/<subtarget>/config-7.3` accordingly. The exact set
  of symbols to disable is target-specific; use the existing 7.3 (4/4)
  commits for the same class of target as guidance.
- Commit as `<target> 7.3 (4/4): fix configuration`
- Reference commits: ath79 7.3 (4/4), ipq806x 7.3 (4/4), ramips 7.3 (4/4),
  bcm53xx 7.3 (4/4), airoha 7.3 (4/4).

After the four commits, verify:
- `make kernel_oldconfig` completes without manual prompts for the target.
- Patches apply clean with `patch --dry-run`.
- The target builds with `CONFIG_TESTING_KERNEL=y`.

Keep patches that move to v7.4 only when still legitimate; re-key version
gates to real 7.3 boundaries.

### readme.<target>.md
Create a per-target build notes file `readme.<target>.md` once the four
commits are done. Use `readme.ramips.md` at branch ramips as the template.

- Copy the file and rename to `readme.<target>.md`.
- Modify only the **Kernel and target prerequisites** section to reflect
  the target’s specific changes:
  * `target/linux/<target>/Makefile` `KERNEL_TESTING_PATCHVER:=7.3`
  * Number and list of outdated backports removed from `patches-7.3`
  * Number and list of patches refreshed for 7.3
  * Number of new defaults appended to `config-7.3`
  * Any target-specific `Kernel/Prepare` tweaks
- Keep **Feed packages that need patches** and **Materialising the feed
  patches** sections essentially unchanged; they document generic 7.3 API
  breakage that affects all targets.

## Verification
- Ladder, each level proves only itself: dry-run < real apply < compiles <
  runs once < survives re-entry/error paths. Never present a lower rung as a
  higher one.
- Compile the touched file per affected config, not just the default `.config`
  (driver Kconfigs can make a legal alternative break).
- Any change touching open/stop/setup/teardown needs a runtime down/up test.
- Label handover confidence: proven (named test), inferred (named evidence),
  untested. An untested item never reads as done.
- Trust facts already established for 7.3 in `KERNEL-7.3.md` before
  re-deriving them: strncpy removed, `proto_ops.bind` takes
  `struct sockaddr_unsized *`, `nf_conntrack_helper->tuple` gone,
  `snmp_fold_field()` unexported, MTD_VIRT_CONCAT symbol collision, symvers
  dropped the `.o` path field.

## Environment facts
- Single git repo: OpenWrt tree at `~/openwrt73`.
- Full image builds are the user's job; do not start one unless asked, keep
  compiles short, and never write into `build_dir/`.
- Single-TU compile is the cheapest rung that catches interface/Kconfig
  breakage: get the command line from `make -n <object>`, then swap in your
  file and a different `-o`. Hand-rolled `-fsyntax-only` is unreliable.
- Toolchains do not predefine `__GLIBC__`; guard aarch64-only code with
  `__aarch64__`.
- `feeds/` is git-ignored; patches there are lost on feeds update. Feed
  breakage is fixed in the feed, not this tree.
- `bin/`, `build_dir/`, `staging_dir/` can be stale; first `make clean` the
  affected package/target before concluding anything about the code.
