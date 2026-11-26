# siflower Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on siflower, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`; seed config used):**
- `sf19a2890` — `knowngood.config`.
- `sf21` — `knowngood2.config`.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for siflower:

- `target/linux/siflower/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/siflower/patches-7.3`
  - 2 new patches added:
    `921-fix-clk-sf21-round-rate-api.patch`,
    `999-pinctrl-siflower-add-missing-bitfield-include.patch`.
  - 14 patches refreshed to apply cleanly on 7.3 against the generic backport/pending/hack set:
    `005-clk-add-drivers-for-siflower-socs.patch`,
    `006-reset-add-support-for-sf19a2890.patch`,
    `007-gpio-add-support-for-siflower-socs.patch`,
    `008-pinctrl-add-driver-for-siflower-sf19a2890.patch`,
    `009-stmmac-add-support-for-sf19a2890.patch`,
    `010-phy-add-support-for-Siflower-USB-PHYs.patch`,
    `012-usb-dwc2-handle-OTG-interrupt-regardless-of-GINTSTS.patch`,
    `013-riscv-add-Siflower-RISC-V-SoC-family-Kconfig-support.patch`,
    `015-reset-add-support-for-sf21a6826-sf21h8898.patch`,
    `016-spi-spi-mem-allow-gpio-cs-in-spi_mem_exec_op.patch`,
    `017-spi-add-support-for-sf21-qspi.patch`,
    `018-pci-dw-pcie-add-support-for-sf21-pcie.patch`,
    `019-net-phy-add-support-for-Siflower-SF23P1211-SF23P1240.patch`,
    `020-net-ethernet-add-support-for-Siflower-DPNS.patch`.

- `target/linux/siflower/config-7.3`
  - 107 new defaults appended to config-7.3 (unique `CONFIG_*` symbols added in 4/4).

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on siflower:

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

