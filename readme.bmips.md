# bmips Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on bmips, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`; seed config used):**
- `bcm6318` — `knowngood.config`.
- `bcm6328` — `knowngood2.config`.
- `bcm6358` — `knowngood3.config`.
- `bcm6362` — `knowngood4.config`.
- `bcm6368` — `knowngood5.config`.
- `bcm63268` — `knowngood6.config`.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for bmips:

- `target/linux/bmips/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/bmips/patches-7.3`
  - 1 outdated backport removed (now upstream in 7.3 or versioned backports):
    `202-mips-bmips-tweak-Kconfig-options.patch`.
  - 10 patches refreshed to apply cleanly on 7.3 against the generic backport/pending/hack set:
    `100-irqchip-add-support-for-bcm6345-style-external-inter.patch`,
    `110-net-dsa-b53-bcm531x5-fix-cpu-rgmii-mode-interpretation.patch`,
    `500-net-broadcom-add-BCM6368-enetsw-controller-driver.patch`,
    `501-net-broadcom-add-BCM6348-enet-controller-driver.patch`,
    `502-net-mdio-mux-bcm6368-allow-disabling.patch`,
    `600-mips-bmips-add-pci-support.patch`,
    `601-pci-controllers-add-bcm6328-pcie-support.patch`,
    `602-pci-controllers-add-bcm6318-pcie-support.patch`,
    `603-pci-controllers-add-bcm6348-pci-support.patch`,
    `700-leds-add-support-for-Sercomm-MSP430-LED-controller.patch`.

- `target/linux/bmips/config-7.3`
  - 36 new defaults appended to config-7.3 (unique `CONFIG_*` symbols added in 4/4).

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on bmips:

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
