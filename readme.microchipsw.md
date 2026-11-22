# microchipsw Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on microchipsw, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`; seed config used):**
- `lan969x` — `knowngood.config`.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for microchipsw:

- `target/linux/microchipsw/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/microchipsw/patches-7.3`
  - 16 outdated backports removed (now upstream in 7.3 or versioned backports):
    `0001-v7.2-net-phy-micrel-use-dev_err_probe.patch`,
    `0002-v7.0-phy-sparx5-serdes-make-it-selectable-for-ARCH_LAN969.patch`,
    `0003-v6.19-reset-sparx5-add-LAN969x-support.patch`,
    `0004-v7.0-dmaengine-at_xdmac-get-the-number-of-DMA-channels-fr.patch`,
    `0005-v6.19-net-sparx5-lan969x-populate-netdev-of_node.patch`,
    `0006-01-v7.1-arm64-dts-microchip-add-LAN969x-clock-header-file.patch`,
    `0007-02-v7.1-arm64-dts-microchip-add-LAN969x-support.patch`,
    `0008-03-v7.1-arm64-dts-microchip-add-EV23X71A-board.patch`,
    `0010-v7.1-hwmon-sparx5-Make-it-selectable-for-ARCH_LAN969X.patch`,
    `0011-v7.2-nvmem-lan9662-otp-add-support-for-LAN969x.patch`,
    `0012-v7.2-arm64-dts-microchip-lan969x-add-OTP-node.patch`,
    `0013-v7.3-net-sparx5-configure-TAS-port-link-speed.patch`,
    `0014-v7.3-spi-atmel-quadspi-add-controller-init-callback.patch`,
    `0015-v7.3-spi-atmel-quadspi-use-init-callback-for-gclk-variant.patch`,
    `0016-v7.3-spi-atmel-quadspi-add-LAN969x-QSPI-support.patch`,
    `0017-v7.3-arm64-dts-microchip-lan969x-add-QSPI-nodes.patch`.
  - 4 patches refreshed to apply cleanly on 7.3 against the generic backport/pending/hack set:
    `127-net-sparx5-add-MTU-change-framework.patch`,
    `128-net-sparx5-add-MTU-change.patch`,
    `129-net-lan969x-add-MTU-change.patch`,
    `130-net-sparx5-wire-in-MTU-change.patch`.

- `target/linux/microchipsw/config-7.3`
  - 83 new defaults appended to config-7.3 (unique `CONFIG_*` symbols added in 4/4).

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on microchipsw:

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
