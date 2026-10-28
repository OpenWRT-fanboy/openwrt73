# ath79 Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on ath79, and the patches used to make them work.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for ath79:

- `target/linux/ath79/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.

- `target/linux/ath79/patches-7.3`
  - 1 outdated backport removed:
    `340-register_gpio_driver_earlier.patch`.
  - 15 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `100-reset-ath79-read-back-reset-register.patch`,
    `101-reset-ath79-reset-ETH-switch-for-AR9344.patch`,
    `311-MIPS-pci-ar71xx-convert-to-OF.patch`,
    `313-MIPS-pci-ar724x-convert-to-OF.patch`,
    `314-MIPS-ath79-remove-irq-code-from-pci.patch`,
    `341-wifi-ath9k-always-register-system-gpios.patch`,
    `370-MIPS-ath79-sanitize-symbols.patch`,
    `400-mtd-nor-support-mtd-name-from-device-tree.patch`,
    `430-mtd-ar934x-nand-driver.patch`,
    `700-phy-add-ath79-usb-phys.patch`,
    `701-usb-add-more-OF-quirk-properties.patch`,
    `800-leds-add-reset-controller-based-driver.patch`,
    `900-unaligned_access_hacks.patch`,
    `910-mikrotik-rb4xx.patch`,
    `911-mikrotik-rb91x.patch`.
  - Add `999-mips-decompress-stringop-overread.patch` to silence GCC 14
    `-Werror=stringop-overread` in `arch/mips/boot/compressed/decompress.c`.

- `target/linux/ath79/config-7.3`
  - 37 new defaults appended: 37 `# CONFIG_... is not set` entries for
    symbols that are new in 7.3, including explicit off for
    `CONFIG_NET_DSA_HIRSCHMANN_HELLCREEK`, `CONFIG_VIDEO_OV2732`, the new
    `DRM_PANEL_*` drivers, `CONFIG_DRM_LONTIUM_LT8713SX`, `CONFIG_AD4691`
    and `CONFIG_TI_ADS131M02`.

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on ath79:

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
per-CPU fold in `jstat_query()` using the existing inline
`snmp_get_cpu_field`.

### libpfring / PF_RING

Linux 7.3 uses `struct sockaddr_unsized *` for the socket `bind`
callback. The patch keeps the old prototype for older kernels and uses
the new one on 7.3.

### netatop

Linux 7.3 removed the legacy string helpers used by the module. The patch
includes `<linux/string.h>` and replaces `strncpy` with
`memcpy_and_pad()`.

### xtables-addons

Two separate API changes are handled:

- `700-kernel-7.3-string-api.patch` replaces removed `strncpy` usage.
- `701-rtsp-kernel-helper-api.patch` adapts to the new
  `nf_conntrack_helper` layout (`nfproto` / `l4proto` instead of `tuple`,
  `expect_policy[]` instead of `expect_policy`) and the new
  `nf_conntrack_helper_register(helper, &ptr)` signature.

## Materialising the feed patches

The `target/linux/generic/hack-7.3/*-kernel-7.3.patch` files are
meta-patches. They create the actual feed patch files listed above and
must be applied once to the OpenWrt tree:

```sh
for p in \
    target/linux/generic/hack-7.3/jool-kernel-7.3.patch \
    target/linux/generic/hack-7.3/libpfring-kernel-7.3.patch \
    target/linux/generic/hack-7.3/netatop-kernel-7.3.patch \
    target/linux/generic/hack-7.3/xtables-addons-kernel-7.3.patch; do
    patch -p1 -N < "$p" || true
done
```
