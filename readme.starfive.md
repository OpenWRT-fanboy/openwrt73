# starfive Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on starfive, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`; seed config used):**
- `generic` — `knowngood.config`.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for starfive:

- `target/linux/starfive/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/starfive/patches-7.3`
  - 2 outdated backports removed (now upstream in 7.3 or versioned backports):
    `0007-driver-mailbox-Add-mailbox-driver.patch`,
    `0022-spi-pl022-starfive-fix-the-problem-of-spi-overlay-re.patch`.
  - 33 patches refreshed to apply cleanly on 7.3 against the generic backport/pending/hack set:
    `0001-riscv-dts-starfive-Add-full-support-except-VIN-and-V.patch`,
    `0002-clocksource-Add-JH7110-timer-driver.patch`,
    `0003-pwm-opencores-Add-PWM-driver-support.patch`,
    `0004-spi-spl022-Get-and-deassert-reset-in-probe.patch`,
    `0005-i2c-designware-Delete-SMBus-functionalities.patch`,
    `0008-driver-rtc-Add-StarFive-JH7110-rtc-driver.patch`,
    `0009-uart-8250-Add-dw-auto-flow-ctrl-support.patch`,
    `0010-uart-8250-add-reset-operation-in-runtime-PM.patch`,
    `0011-CAN-starfive-Add-CAN-engine-support.patch`,
    `0013-drivers-nvme-Add-precheck-and-delay-for-CQE-pending-.patch`,
    `0014-riscv-Optimize-memcpy-with-aligned-version.patch`,
    `0015-riscv-purgatory-Change-memcpy-to-the-aligned-version.patch`,
    `0017-plic-irq-Set-IRQCHIP_EOI_THREADED-in-PREEMPT_RT-case.patch`,
    `0018-driver-e24-add-e24-driver.patch`,
    `0020-spi-pl022-starfive-Add-platform-bus-register-to-adap.patch`,
    `0021-spi-pl022-starfive-Avoid-power-device-error-when-CON.patch`,
    `0023-spi-pl022-starfive-Enable-spi-to-be-compiled-into-mo.patch`,
    `0024-spi-pl022-Prompt-warning-when-frequency-does-not-sup.patch`,
    `0025-spi-pl022-Fix-spi-overlay-falut.patch`,
    `0027-RISC-V-Create-unique-identification-for-SoC-PMU.patch`,
    `0031-spi-pl022-starfive-fix-controller-deregistration.patch`,
    `1002-serial-8250_dw-Add-starfive-jh7100-hsuart-compatible.patch`,
    `1004-power-reset-tps65086-Allow-building-as-a-module.patch`,
    `1007-reset-starfive-Add-JH7100-audio-reset-driver.patch`,
    `1009-clk-starfive-jh7100-Keep-more-clocks-alive.patch`,
    `1010-pinctrl-starfive-Reset-pinmux-settings.patch`,
    `1011-net-stmmac-use-GFP_DMA32.patch`,
    `1012-dt-bindings-dma-dw-axi-dmac-Increase-DMA-channel-lim.patch`,
    `1013-dmaengine-dw-axi-dmac-Handle-xfer-start-while-non-id.patch`,
    `1014-dmaengine-dw-axi-dmac-Add-StarFive-JH7100-support.patch`,
    `1015-hwrng-Add-StarFive-JH7100-Random-Number-Generator-dr.patch`,
    `1021-riscv-dts-Add-full-JH7100-Starlight-and-VisionFive-s.patch`,
    `1024-riscv-dts-starfive-visionfive2-add-LED-aliases-and-s.patch`.

- `target/linux/starfive/config-7.3`
  - 69 new defaults appended to config-7.3 (unique `CONFIG_*` symbols added in 4/4).

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on starfive:

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
