# mvebu Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on mvebu, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`):** cortexa53, cortexa72, cortexa9.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for mvebu:

- `target/linux/mvebu/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/mvebu/patches-7.3`
  - 4 outdated backports removed (now upstream in 7.3 or versioned backports):
    `300-mvebu-Mangle-bootloader-s-kernel-arguments.patch`,
    `340-v7.2-arm64-dts-marvell-armada-37xx-mark-EIP97-as-dma-cohe.patch`,
    `830-03-i2c-pxa-handle-Early-Bus-Busy-condition-on-Armada-3700.patch`,
    `901-dt-bindings-Add-IEI-vendor-prefix-and-IEI-WT61P803-P.patch`,
  - 13 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `100-aardvark-workaround-PCIe.patch`,
    `323-arm64-dts-marvell-update-LED-and-partition-labels-fo.patch`,
    `400-find_active_root.patch`,
    `700-mvneta-tx-queue-workaround.patch`,
    `801-pci-mvebu-time-out-reset-on-link-up.patch`,
    `830-02-i2c-pxa-prevent-calling-of-the-generic-recovery-init-code.patch`,
    `902-drivers-mfd-Add-a-driver-for-IEI-WT61P803-PUZZLE-MCU.patch`,
    `903-drivers-hwmon-Add-the-IEI-WT61P803-PUZZLE-HWMON-driv.patch`,
    `904-drivers-leds-Add-the-IEI-WT61P803-PUZZLE-LED-driver.patch`,
    `906-Documentation-hwmon-Add-iei-wt61p803-puzzle-hwmon-dr.patch`,
    `907-MAINTAINERS-Add-an-entry-for-the-IEI-WT61P803-PUZZLE.patch`,
    `913-drivers_spi_add_mtpoe_device_compatible.patch`,
    `951-pci-mvebu-wait-for-link-down-in-reset.patch`,

- `target/linux/mvebu/config-7.3`
  - config symbols finalised by `make kernel_oldconfig` with
    CONFIG_TESTING_KERNEL=y (see commit 4/4 for the exact diff).
## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on mvebu:

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
