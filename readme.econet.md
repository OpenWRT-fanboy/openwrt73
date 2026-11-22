# econet Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on econet, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`; seed config used):**
- `en751221` — `knowngood.config`.
- `en751627` — `knowngood2.config`.
- `en7528` — `knowngood3.config`.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for econet:

- `target/linux/econet/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/econet/patches-7.3`
  - 46 outdated backports removed (now upstream in 7.3 or versioned backports):
    `017-v6.19rc1-clk-en7523-Add-reset-controller-support-for-EN7523-S.patch`,
    `018-v6.19rc1-dt-bindings-clock-airoha-Add-reset-support-to-EN7523.patch`,
    `020-v6.19rc1-dt-bindings-clock-airoha-Add-reset-support-to-EN7523.patch`,
    `029-05-v6.19-spi-airoha-remove-unnecessary-restriction-length.patch`,
    `029-06-v6.19-spi-airoha-remove-unnecessary-switch-to-non-dma-mode.patch`,
    `029-07-v6.19-spi-airoha-unify-dirmap-read-write-code.patch`,
    `029-08-v6.19-spi-airoha-support-of-dualio-quadio-flash-reading-co.patch`,
    `029-09-v6.19-spi-airoha-avoid-setting-of-page-oob-sizes-in-REG_SP.patch`,
    `029-10-v6.19-spi-airoha-reduce-the-number-of-modification-of-REG_.patch`,
    `029-11-v6.19-spi-airoha-set-custom-sector-size-equal-to-flash-pag.patch`,
    `029-12-v6.19-spi-airoha-avoid-reading-flash-page-settings-from-SN.patch`,
    `029-13-v6.19-spi-airoha-buffer-must-be-0xff-ed-before-writing.patch`,
    `030-v7.1-mips-dts-Add-PCIe-to-EcoNet-EN751221.patch`,
    `031-01-v7.1-dt-bindings-clock-reset-add-econet-en751221-bindings.patch`,
    `031-02-v7.1-clk-airoha-add-econet-en751221-clock-reset-support-t.patch`,
    `032-v7.1-PCI-Prevent-assignment-to-unsupported-bridge-windows.patch`,
    `033-01-v7.2-dt-bindings-phy-Document-PCIe-PHY-in-EcoNet-EN751221.patch`,
    `033-02-v7.2-phy-econet-Add-PCIe-PHY-driver-for-EcoNet-EN751221-a.patch`,
    `034-v6.19-PCI-mediatek-Convert-bool-to-single-quirks-entry-and.patch`,
    `035-v6.19-PCI-mediatek-Use-generic-MACRO-for-TPVPERL-delay.patch`,
    `036-v6.19-PCI-mediatek-Add-support-for-Airoha-AN7583-SoC.patch`,
    `041-v7.3-PCI-mediatek-Add-support-for-EcoNet-EN7528-SoC.patch`,
    `042-05-v6.19-pinctrl-airoha-convert-comma-to-semicolon.patch`,
    `043-01-v7.2-pinctrl-airoha-Fix-type-in-.pin_config_group_get-cal.patch`,
    `043-02-v7.2-pinctrl-Move-Airoha-driver-to-dedicated-directory.patch`,
    `044-06-v7.3-pinctrl-airoha-fix-I2C1-pin-mux-config-for-AN758.patch`,
    `044-07-v7.3-pinctrl-airoha-fix-I2C-pin-mux-config-for-AN7583.patch`,
    `044-08-v7.3-pinctrl-airoha-fix-AN7583-MDIO-pin-mux-config.patch`,
    `044-11-v7.3-pinctrl-airoha-add-set_direction-helper-for-gpio.patch`,
    `044-12-v7.3-pinctrl-airoha-minor-improvements.patch`,
    `044-17-v7.3-pinctrl-airoha-remove-not-needed-irq_type-array.patch`,
    `044-18-v7.3-pinctrl-airoha-statically-allocate-gpio-regs-str.patch`,
    `044-19-v7.3-pinctrl-airoha-move-common-definitions-to-the-se.patch`,
    `044-20-v7.3-pinctrl-airoha-split-driver-on-shared-code-and-S.patch`,
    `044-21-v7.3-pinctrl-airoha-an7581-remove-en7581-prefix-from-.patch`,
    `044-22-v7.3-pinctrl-airoha-an7583-remove-an7583-prefix-from-.patch`,
    `044-23-v7.3-pinctrl-airoha-an7583-rename-registers-to-match-.patch`,
    `044-24-v7.3-pinctrl-airoha-an7583-add-support-for-npu_uart-p.patch`,
    `044-25-v7.3-pinctrl-airoha-an7583-add-support-for-pon_alt-pi.patch`,
    `044-26-v7.3-pinctrl-airoha-an7583-add-support-for-olt-pinmux.patch`,
    `044-27-v7.3-pinctrl-airoha-add-support-of-en7523-SoC.patch`,
    `044-28-v7.3-pinctrl-airoha-try-to-find-chip-scu-node-by-phan.patch`,
    `044-29-v7.3-pinctrl-airoha-add-support-of-an7563-SoC.patch`,
    `046-v7.3-net-phy-mediatek-add-EcoNet-EN7528-PHY-support.patch`,
    `100-econet-add-en7528-soc.patch`,
    `914-phy-add-en7528-usb-phy-driver.patch`.
  - 1 new patch added:
    `999-mips-decompress-stringop-overread.patch`.
  - 10 patches refreshed to apply cleanly on 7.3 against the generic backport/pending/hack set:
    `045-01-v7.4-pinctrl-airoha-limit-GPIO-interrupts-to-interrup.patch`,
    `101-econet-timer-add-en7528-support.patch`,
    `300-spi-Add-support-for-the-Airoha-EN7523-SoC-SPI-contro.patch`,
    `301-spi-Airoha-adapt-to-support-en75-mips.patch`,
    `310-usb-enable-econet-usb.patch`,
    `320-gpio-en7523-enable-for-econet-mips.patch`,
    `886-uart-add-en7523-support.patch`,
    `887-uart-airoha-add-econet-support.patch`,
    `902-snand-mtk-bmt-support.patch`,
    `915-usb-xhci-mtk-add-en7528-ltssm-quirk.patch`.

- `target/linux/econet/config-7.3`
  - 81 new defaults appended to config-7.3 (unique `CONFIG_*` symbols added in 4/4).

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on econet:

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
