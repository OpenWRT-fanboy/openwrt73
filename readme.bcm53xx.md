# bcm53xx Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on bcm53xx, and the patches used to make them work.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for bcm53xx:

- `target/linux/bcm53xx/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/bcm53xx/patches-7.3`
  - 12 outdated backports removed as they are now upstream in 7.3:
    `311-v7.1-ARM-dts-BCM5301X-EA9200-set-WAN-MAC-from-nvram.patch`,
    `312-v7.1-ARM-dts-BCM5301X-panamera-set-WAN-MAC-from-nvram.patch`,
    `320-v7.1-ARM-dts-BCM5301X-EA9200-add-WiFi-button.patch`,
    `321-v7.1-ARM-dts-BCM5301X-EA9200-add-USB-GPIOs.patch`,
    `322-v7.1-ARM-dts-BCM5301X-EA9200-add-LEDs.patch`,
    `323-v7.1-ARM-dts-BCM5301X-EA9200-specify-partitions.patch`,
    `331-v7.2-ARM-dts-NSP-Move-MX6X-pinctrl-config-to-PWM-node.patch`,
    `349-v7.1-ARM-dts-BCM5301X-Describe-PCIe-controllers-fully.patch`,
    `350-v7.1-ARM-dts-BCM5301X-add-root-pcie-bridges.patch`,
    `352-v7.2-ARM-dts-BCM5301X-EA9200-fix-nvram-size.patch`,
    `360-v7.2-ARM-dts-BCM5301X-R6300v2-fix-USB3.patch`,
    `361-v7.2-ARM-dts-BCM5301X-EA6500v2-fix-USB3.patch`.
  - 6 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `140-mtd-parsers-trx-parse-firmware-MTD-partitions-only.patch`,
    `180-usb-xhci-add-support-for-performing-fake-doorbell.patch`,
    `304-ARM-dts-BCM5301X-Specify-switch-ports-for-remaining-.patch`,
    `371-ARM-dts-broadcom-model-USB-VBUS-power-with-regulator.patch`,
    `500-UBI-Detect-EOF-mark-and-erase-all-remaining-blocks.patch`,
    `905-BCM53573-minor-hacks.patch`.
- `target/linux/bcm53xx/config-7.3`
  - 41 new defaults appended, matching the ramips branch 7.3 config fix:
    `CONFIG_SCHED_CACHE=y` and 40 `# CONFIG_... is not set`
    for new symbols, including explicit off for `CONFIG_ARCH_ZTE`,
    `CONFIG_AMD_SBTSI` and `CONFIG_LTC2378`.

## Feed packages that need patches

The following packages require patches to build against Linux 7.3 on bcm53xx:

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
