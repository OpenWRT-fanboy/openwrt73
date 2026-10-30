# Kernel 7.3 status

The active baseline is `generic`, based on recent upstream OpenWrt. The kernel is
Linux 7.3.6 final; `target/linux/generic/kernel-7.3` carries the version and hash.
The migration is complete for the generic build system and all targets.

## Generic branch

The migration commits are:

1. `generic 7.3 (1/4): copy patches and config from 6.18`
2. `generic 7.3 (2/4): delete outdated backports`
3. `generic 7.3 (3/4): update patches`
4. `generic 7.3 (4/4): fix configuration`

There is also a feed-fixes commit adding the four `*-kernel-7.3.patch` meta-patches
for jool, libpfring, netatop, and xtables-addons; it is pending squash into 4/4.

Generic 2/4 deletes backports confirmed upstream in 7.3.6. Generic 3/4 regenerates
patches where upstream has changed. The full generic patch series replays with zero
failures and zero fuzz.

Generic 4/4 adds the 7.3 kernel version file and the generic build-system changes
(`include/kernel.mk`, `include/image.mk`, `config-filter`, and
`package/kernel/linux/modules/*.mk`).

## Target branches

All 45 target branches have the standard four migration commits plus their readme
commit (`qualcommbe` has one extra non-migration commit). Each target readme links
device-selected `knowngood*.config` seeds.

## Feed packages

The meta-patches in `target/linux/generic/hack-7.3/` materialise these feed patches:

- `jool`: `101-fix-unexported-snmp-fold-field.patch`
- `libpfring`: `902-fix-bind-callback-linux-6.19.patch`
- `netatop`: `200-kernel-7.3-string-api.patch`
- `xtables-addons`: `700-kernel-7.3-string-api.patch`, `701-rtsp-kernel-helper-api.patch`

The `feeds/` tree is git-ignored; these patches must be re-materialised after a
feeds update. Feed breakage itself is fixed upstream in the feeds, not in this tree.
