# gemini Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on gemini, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`):** none recorded.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for gemini:

- `target/linux/gemini/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/gemini/patches-7.3`
  - 6 outdated backports removed (now upstream in 7.3 or versioned backports):
    `0002-ARM-dts-Add-a-Verbatim-Gigabit-NAS-DTS.patch`,
    `0003-ARM-dts-Add-a-Raidsonic-IB-4210-B-DTS.patch`,
    `0004-ARM-dts-gemini-Correct-the-RUT1xx.patch`,
    `0009-v7.4-usb-fotg210-use-the-common-EHCI-core.patch`,
    `302-ARM-dts-gemini-Tag-disk-led-for-disk-activity.patch`,
    `304-gemini-augment-SQ201-DTS-with-botched-partitions.patch`,
  - 4 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `0005-v7.4-usb-ehci-support-non-standard-port-status-registers.patch`,
    `0006-v7.4-usb-ehci-add-port-reset-hooks.patch`,
    `0007-v7.4-usb-ehci-add-port-speed-hook.patch`,
    `0010-v7.4-usb-fotg210-udc-fix-endpoint-and-resource-handling.patch`,

- `target/linux/gemini/config-7.3`
  - 40 new defaults appended for symbols introduced in 7.3 (universal set
    plus arm architecture-specific symbols). These are inferred from the
    reference 7.3 (4/4) commits; confirm with `make kernel_oldconfig` for this
    target before relying on them.

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on gemini:

- **`jool` / `kmod-jool-netfilter`**
  - Failure without patch: `jool_common.ko: symbol 'snmp_fold_field' undefined`
  - Patch: `101-fix-unexported-snmp-fold-field.patch`
  - Location: `feeds/packages/net/jool/patches/`
- **`libpfring` / `kmod-pf-ring`**
  - Failure without patch: `ring_bind` has old `struct sockaddr *` prototype instead of `struct sockaddr_unsized *`
  - Patch: `902-fix-bind-callback-linux-6.19.patch`
  - Location: `feeds/packages/libs/libpfring/patches/`
- **`netatop` / `kmod-netatop`**
  - Failure without patch: implicit declaration of `strncpy`; missing `<linux/string.h>`
  - Patch: `200-kernel-7.3-string-api.patch`
  - Location: `feeds/packages/admin/netatop/patches/`
- **`xtables-addons` / `kmod-nf-nathelper-rtsp`**
  - Failure without patch: removed `strncpy`; `nf_conntrack_helper.tuple` removed; new `nf_conntrack_helper_register()` signature
  - Patch: `700-kernel-7.3-string-api.patch`, `701-rtsp-kernel-helper-api.patch`
  - Location: `feeds/packages/net/xtables-addons/patches/`

### jool

`snmp_fold_field()` is no longer exported. The patch reimplements the
per-CPU fold in `jstat_query()` using the existing inline `snmp_get_cpu_field`.

### libpfring / PF_RING

Linux 7.3 uses `struct sockaddr_unsized *` for the socket `bind` callback.
The patch keeps the old prototype for older kernels and uses the new one on 7.3.

### netatop

Linux 7.3 removed the legacy string helpers used by the module. The patch
includes `<linux/string.h>` and replaces `strncpy` with `memcpy_and_pad()`.

### xtables-addons

Two separate API changes are handled:

- `700-kernel-7.3-string-api.patch` replaces removed `strncpy` usage.
- `701-rtsp-kernel-helper-api.patch` adapts to the new `nf_conntrack_helper`
  layout (`nfproto` / `l4proto` instead of `tuple`) and the new
  `nf_conntrack_helper_register(helper, &ptr)` signature.

## Materialising the feed patches

The `target/linux/generic/hack-7.3/*-kernel-7.3.patch` files are meta-patches.
They create the actual feed patch files listed above and must be applied once
to the OpenWrt tree:

```sh
for p in \
    target/linux/generic/hack-7.3/jool-kernel-7.3.patch \
    target/linux/generic/hack-7.3/libpfring-kernel-7.3.patch \
    target/linux/generic/hack-7.3/netatop-kernel-7.3.patch \
    target/linux/generic/hack-7.3/xtables-addons-kernel-7.3.patch; do
    patch -p1 -N < "$p" || true
done
```
