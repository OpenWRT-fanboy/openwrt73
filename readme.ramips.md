# ramips Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on ramips, and the patches used to make them work.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for ramips:

- `target/linux/ramips/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.

- `target/linux/ramips/patches-7.3`
  - 10 outdated backports removed as they are now upstream in 7.3:
    `102-02-pwm-mediatek-correct-mt7628-clock-source-setting.patch`,
    `110-MIPS-ralink-reduce-ARCH_DMA_MINALIGN.patch`,
    `120-1-mips-pci-mt7620-fix-bridge-register-access.patch`,
    `120-2-mips-pci-mt7620-add-more-register-init-values.patch`,
    `120-3-mips-pci-mt7620-rework-initialization-procedure.patch`,
    `315-owrt-hack-fix-mt7688-cache-issue.patch`,
    `400-mtd-cfi-cmdset-0002-force-word-write.patch`,
    `761-net-dsa-add-ralink-metadata-tagger.patch`,
    `802-GPIO-MIPS-ralink-add-gpio-driver-for-ralink-SoC.patch`,
    `850-awake-rt305x-dwc2-controller.patch`.
  - 18 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `200-add-ralink-eth.patch`,
    `311-MIPS-use-set_mode-to-enable-disable-the-cevt-r4k-irq.patch`,
    `314-MIPS-add-bootargs-override-property.patch`,
    `331-mt7620-avoid-direct-jal-in-resume_user_mode_work.patch`,
    `332-mt7620-conditional-stack-align.patch`,
    `405-mtd-spi-nor-Add-support-for-BoHong-bh25q128as.patch`,
    `410-mtd-rawnand-add-driver-support-for-MT7621-nand-flash.patch`,
    `720-NET-no-auto-carrier-off-support.patch`,
    `804-dma-ralink-add-back-gdma-driver.patch`,
    `810-uvc-add-iPassion-iP2970-support.patch`,
    `821-SPI-ralink-add-Ralink-SoC-spi-driver.patch`,
    `825-i2c-MIPS-adds-ralink-I2C-driver.patch`,
    `830-mmc-MIPS-ralink-add-sdhci-for-mt7620a-SoC.patch`,
    `831-01-mmc-mtk-sd-add-tuning-parameters-for-legacy-MIPS-MT7.patch`,
    `831-02-mmc-mtk-sd-disable-auto-CMD23-support-for-mt7620.patch`,
    `831-03-mmc-mtk-sd-use-default-PATCH_BIT1-2-values-for-mt762.patch`,
    `835-asoc-add-mt7620-support.patch`,
    `870-Input-sx951x-add-Semtech-SX9512-SX9513-driver.patch`.
  - Add `999-mips-decompress-stringop-overread.patch` to silence GCC 14
    `-Werror=stringop-overread` in `arch/mips/boot/compressed/decompress.c`.

- `target/linux/ramips/*/config-7.3`
  - 38 new defaults appended: `CONFIG_SCHED_CACHE=y` and 37
    `# CONFIG_... is not set` entries for symbols that are new in 7.3,
    including explicit off for `CONFIG_NET_DSA_HIRSCHMANN_HELLCREEK`,
    `CONFIG_VIDEO_OV2732`, the new `DRM_PANEL_*` drivers,
    `CONFIG_AD4691` and `CONFIG_TI_ADS131M02`.

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on ramips:

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
