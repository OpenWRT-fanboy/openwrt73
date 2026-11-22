# realtek Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on realtek, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`; seed config used):**
- `rtl838x` — `knowngood.config`.
- `rtl839x` — `knowngood2.config`.
- `rtl930x` — `knowngood3.config`.
- `rtl930x_nand` — `knowngood4.config`.
- `rtl931x` — `knowngood5.config`.
- `rtl931x_nand` — `knowngood6.config`.
- `rtl960x` — `knowngood7.config`.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for realtek:

- `target/linux/realtek/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/realtek/patches-7.3`
  - 67 outdated backports removed (now upstream in 7.3 or versioned backports):
    `021-v6.19-gpio-regmap-Bypass-cache-for-shadowed-outputs.patch`,
    `022-v7.0-mtd-nand-realtek-ecc-relax-OOB-size-check-to-minimum.patch`,
    `023-01-v7.0-dt-bindings-gpio-realtek-otto-add-rtl9607-compatible.patch`,
    `023-02-v7.0-gpio-realtek-otto-add-rtl9607-support.patch`,
    `024-01-v7.1-dt-bindings-net-ethernet-phy-add-property-enet-phy-p.patch`,
    `024-02-v7.1-net-phy-realtek-add-RTL8224-pair-order-support.patch`,
    `024-03-v7.1-dt-bindings-net-ethernet-phy-add-property-enet-phy-p.patch`,
    `024-04-v7.1-net-phy-realtek-add-RTL8224-polarity-support.patch`,
    `025-01-v7.0-i2c-rtl9300-remove-const-cast.patch`,
    `025-02-v7.0-i2c-rtl9300-use-of-instead-of-fwnode.patch`,
    `026-v7.1-i2c-rtl9300-add-support-for-more-bus-speeds.patch`,
    `027-01-v7.1-i2c-rtl9300-split-data_reg-into-read-and-write-reg.patch`,
    `027-02-v7.1-i2c-rtl9300-introduce-max-length-property-to-driver-.patch`,
    `027-03-v7.1-i2c-rtl9300-introduce-F_BUSY-to-the-reg_fields-struc.patch`,
    `027-04-v7.1-i2c-rtl9300-introduce-a-property-for-8-bit-width-reg.patch`,
    `027-05-v7.1-dt-bindings-i2c-realtek-rtl9301-i2c-extend-for-clock.patch`,
    `027-06-v7.1-i2c-rtl9300-introduce-clk-struct-for-upcoming-rtl960.patch`,
    `027-07-v7.1-i2c-rtl9300-introduce-new-function-properties-to-driv.patch`,
    `027-08-v7.1-i2c-rtl9300-add-RTL9607C-i2c-controller-support.patch`,
    `028-v7.1-hwmon-lm75-fix-configuration-register-writes.patch`,
    `029-v7.2-hwmon-lm75-support-active-high-alert-polarity.patch`,
    `030-v7.2-net-phy-realtek-support-MDI-swapping-for-RTL8226-CG.patch`,
    `031-01-v7.2-net-mdio-realtek-rtl9300-enhance-documentation-namin.patch`,
    `031-02-v7.2-net-mdio-realtek-rtl9300-Add-device-specific-info-st.patch`,
    `031-03-v7.2-net-mdio-realtek-rtl9300-Add-ports-to-info-structure.patch`,
    `031-04-v7.2-net-mdio-realtek-rtl9300-Add-pages-to-info-structure.patch`,
    `031-05-v7.2-net-mdio-realtek-rtl9300-Add-register-structure.patch`,
    `031-06-v7.2-net-mdio-realtek-rtl9300-Add-command-C22-register.patch`,
    `031-07-v7.2-net-mdio-realtek-rtl9300-Add-I-O-register.patch`,
    `031-08-v7.2-net-mdio-realtek-rtl9300-Add-port-mask-register.patch`,
    `031-09-v7.2-net-mdio-realtek-rtl9300-Link-I-O-functions-in-info-.patch`,
    `031-10-v7.2-net-mdio-realtek-rtl9300-provide-generic-command-run.patch`,
    `031-11-v7.2-net-mdio-realtek-rtl9300-use-command-runner-for-writ.patch`,
    `031-12-v7.2-net-mdio-realtek-rtl9300-use-command-runner-for-read.patch`,
    `031-13-v7.2-net-mdio-realtek-rtl9300-use-command-runner-for-read.patch`,
    `031-14-v7.2-net-mdio-realtek-rtl9300-Refactor-otto_emdio_map_por.patch`,
    `031-15-v7.2-net-mdio-realtek-rtl9300-harden-otto_emdio_map_ports.patch`,
    `031-16-v7.2-net-mdio-realtek-rtl9300-harden-otto_emdio_probe_one.patch`,
    `031-17-v7.2-net-mdio-realtek-rtl9300-relocate-topology-setup.patch`,
    `031-18-v7.2-net-mdio-realtek-rtl9300-relocate-c22-c45-device-tre.patch`,
    `031-19-v7.2-net-mdio-realtek-rtl9300-reorder-controller-setup.patch`,
    `031-20-v7.2-net-mdio-realtek-rtl9300-Correctly-handle-ethernet-p.patch`,
    `031-21-v7.2-net-mdio-realtek-rtl9300-Add-prefix-to-register-fiel.patch`,
    `031-22-v7.2-net-mdio-realtek-rtl9300-Make-otto_emdio_read_cmd-ge.patch`,
    `031-23-v7.2-net-mdio-realtek-rtl9300-Add-registers-for-high-port.patch`,
    `031-24-v7.2-net-mdio-realtek-rtl9300-Add-support-for-RTL931x.patch`,
    `031-29-v7.4-net-mdio-realtek-rtl9300-Add-page-tracking.patch`,
    `032-06-v7.3-irqchip-irq-realtek-rtl-Add-a-select-function.patch`,
    `032-07-v7.3-irqchip-irq-realtek-rtl-Allow-shuffled-interrupt-ord.patch`,
    `032-08-v7.3-irqchip-irq-realtek-rtl-Activate-multiple-parents.patch`,
    `033-01-v7.3-i2c-algo-bit-Allow-to-skip-bit-test.patch`,
    `033-02-v7.3-i2c-gpio-Enhance-driver-for-buses-with-shared-SCL.patch`,
    `034-01-v7.2-watchdog-realtek-otto-prevent-PHASE2-underflows.patch`,
    `034-02-v7.2-watchdog-realtek-otto-enable-clock-before-using-IO.patch`,
    `035-v7.3-watchdog-realtek-otto-change-to-use-regmap-API.patch`,
    `036-v7.3-clocksource-rtl-otto-change-driver-to-use-__raw-reads-and-writes.patch`,
    `037-v7.3-spi-realtek-rtl-change-to-__raw-reads-and-writes.patch`,
    `700-dsa-mdio-increase-max-ports-for-rtl839x-rtl931x.patch`,
    `705-v7.1-net-sfp-initialize-i2c_block_size-at-adapter-configu.patch`,
    `706-01-v7.2-net-sfp-apply-I2C-adapter-quirks-to-limit-block-size.patch`,
    `706-02-v7.2-net-sfp-extend-SMBus-support.patch`,
    `716-net-ethernet-add-support-for-rtl838x-ethernet.patch`,
    `816-01-v7.3-net-pse-pd-add-Realtek-PSE-MCU-core.patch`,
    `816-02-v7.3-net-pse-pd-realtek-pse-mcu-add-I2C-transport.patch`,
    `816-03-v7.3-net-pse-pd-realtek-pse-mcu-add-UART-transport.patch`,
    `822-add-realtek-pcie-controller-driver.patch`,
    `824-net-dsa-pass-bridge-VLAN-protocol-changes-to-drivers.patch`.
  - 6 new patches added:
    `921-fix-pinctrl-rtl8231-gpio-regmap-api.patch`,
    `922-fix-clk-rtl83xx-round-rate-api.patch`,
    `923-fix-net-phy-sfp-port-api.patch`,
    `924-fix-pcs-rtl-otto-phylink-media-api.patch`,
    `925-fix-l3-at_least-macro-collision.patch`,
    `999-mips-decompress-stringop-overread.patch`.
  - 32 patches refreshed to apply cleanly on 7.3 against the generic backport/pending/hack set:
    `031-26-v7.4-net-mdio-realtek-rtl9300-deny-C45-over-C22-access.patch`,
    `031-27-v7.4-net-mdio-realtek-rtl9300-suppress-sysfs-bind-unbind-attributes.patch`,
    `031-28-v7.4-net-mdio-realtek-rtl9300-Configure-hardware-polling-during-probing.patch`,
    `031-30-v7.4-net-mdio-realtek-rtl9300-Increase-MDIO-timeout.patch`,
    `031-31-v7.4-net-mdio-realtek-rtl9300-Open-up-C22-and-C45-space-in-parallel.patch`,
    `031-32-v7.4-net-mdio-realtek-rtl9300-Add-support-for-RTL838x.patch`,
    `031-33-v7.4-net-mdio-realtek-rtl9300-Add-support-for-RTL839x.patch`,
    `031-34-v7.4-net-mdio-realtek-rtl9300-reword-Kconfig-and-module-description.patch`,
    `039-01-v7.4-gpio-realtek-otto-use-__raw_readl-writel-in-realtek_.patch`,
    `040-v7.4-spi-realtek-rtl-add-support-for-second-CS.patch`,
    `300-01-enhance-realtek-platform-config.patch`,
    `318-add-rtl83xx-clk-support.patch`,
    `330-add-realtek-thernal-driver.patch`,
    `712-net-phy-add-an-MDIO-SMBus-library.patch`,
    `714-net-phy-sfp-add-support-for-SMBus.patch`,
    `717-net-ethernet-add-rtl960x-gmac-probe-driver.patch`,
    `718-net-dsa-add-support-for-rtl838x-switch.patch`,
    `719-net-dsa-add-rtl960x-switch.patch`,
    `720-add-rtl-phy.patch`,
    `721-net-dsa-add-support-for-tag-rtl-otto.patch`,
    `722-net-dsa-let-hw-port-metadata-mark-trapped-frames.patch`,
    `723-net-mdio-Add-Realtek-Otto-auxiliary-controller.patch`,
    `743-net-realtek-serdes-configuration.patch`,
    `802-mfd-Add-RTL8231-core-device.patch`,
    `803-pinctrl-Add-RTL8231-pin-control-and-GPIO-support.patch`,
    `804-leds-Add-support-for-RTL8231-LED-scan-matrix.patch`,
    `806-add-mdio-driver.patch`,
    `808-add-serdes-mdio-driver.patch`,
    `809-add-hasivo-stc8-mfd.patch`,
    `810-add-hasivo-mcu-wdt.patch`,
    `813-add-hasivo-mcu-sensor.patch`,
    `820-add-rtl960x-mdio-driver.patch`.

- `target/linux/realtek/config-7.3`
  - 85 new defaults appended to config-7.3 (unique `CONFIG_*` symbols added in 4/4).

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on realtek:

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
