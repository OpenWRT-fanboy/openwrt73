# mediatek Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on mediatek, and the patches used to make them work.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for mediatek:

- `target/linux/mediatek/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.

- `target/linux/mediatek/patches-7.3`
  - 32 outdated backports removed as they are now upstream in 7.3:
    `001-clk-mediatek-add-MUX_CLR_SET-macro.patch`,
    `002-clk-mediatek-mt8192-use-MUX_CLR_SET.patch`,
    `003-clk-mediatek-mt7988-use-MUX_CLR_SET-for-gate-less-mu.patch`,
    `010-v7.0-mtd-spinand-add-support-for-Dosilicon-DS35Q1GA-DS35M.patch`,
    `046-v6.19-arm64-dts-mediatek-mt7988a-bpi-r4-pro-add-dts.patch`,
    `047-v6.19-arm64-dts-mediatek-mt7988a-bpi-r4-pro-Add-PCIe-overlays.patch`,
    `048-v6.19-arm64-dts-mediatek-mt7988a-bpi-r4-pro-add-emmc-sd-overlay.patch`,
    `049-v6.19-arm64-dts-mediatek-mt7988-add-dtbs-with-applied-overlays-for-bpi-r4pro.patch`,
    `061-v6.19-arm64-dts-mediatek-mt7986-bpi-r3-Change-fan-PWM-valu.patch`,
    `063-v7.0-fix-incorrect-model-string-in-devicetree-for-bpi-r4-pro.patch`,
    `070-v7.0-pinctrl-mediatek-enable-ies_present-flag-for-MT798x.patch`,
    `080-v6.19-drm-mediatek-mtk_hdmi_common-Defer-probe-when-ddc-i2.patch`,
    `090-v7.1-drm-prime-Limit-scatter-list-size-with-dedicated-DMA.patch`,
    `091-v7.1-drm-gem-dma-Support-dedicated-DMA-device-for-allocat.patch`,
    `092-v7.1-drm-mediatek-mtk_gem-Partial-refactor-and-use-drm_ge.patch`,
    `093-v7.1-drm-mediatek-Set-dedicated-DMA-device-and-drop-custo.patch`,
    `094-v7.1-arm64-dts-mediatek-mt7988a-bpi-r4pro-rename-mgmt-port-to-lan5.patch`,
    `095-v7.1-arm64-dts-mediatek-mt7988a-bpi-r4pro-drop-duplicate-fan-properties.patch`,
    `096-v7.1-arm64-dts-mediatek-mt7988a-bpi-r4pro-update-gpio-leds.patch`,
    `097-v7.1-arm64-dts-mediatek-mt7988a-bpi-r4pro-rework-pcie-gpio-hog-handling.patch`,
    `117-complete-mt7981b-dtsi.patch`,
    `186-arm64-dts-mt7988a-complete-dtsi.patch`,
    `198-dts-mt7988a-enable-wed.patch`,
    `320-hwrng-mtk-add-support-for-hw-access-via-SMCC.patch`,
    `734-net-phy-add-Airoha-EN8801SC-PHY.patch`,
    `737-net-dsa-add-Airoha-AN8855.patch`,
    `830-thermal-drivers-mediatek-lvts_thermal-Add-irq_enable-support.patch`,
    `831-thermal-drivers-mediatek-lvts_thermal-Add-MT7987-support.patch`,
    `842-mediatek-enable-using-efuse-cali-data-for-mt7988-cpu-volt.patch`,
    `863-arm64-dts-mt7986-add-sound-wm8960.patch`,
    `864-arm64-dts-mt7986-add-sound-overlay-for-bpi-r3.patch`,
    `920-block-partitions-msdos-add-OF-node-by-partition-numb.patch`.
  - 48 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `100-dts-update-mt7622-rfb1.patch`,
    `103-mt7623-enable-arch-timer.patch`,
    `104-mt7622-add-snor-irq.patch`,
    `106-dts-mt7622-disable_btif.patch`,
    `115-Revert-arm64-dts-mediatek-fix-t-phy-unit-name.patch`,
    `116-arm64-dts-mediatek-mt7622-readd-syscon-to-pciesys-no.patch`,
    `121-hack-spi-nand-1b-bbm.patch`,
    `131-dts-mt7622-add-snand-support.patch`,
    `140-dts-fix-wmac-support-for-mt7622-rfb1.patch`,
    `150-dts-mt7623-eip97-inside-secure-support.patch`,
    `188-arm64-dts-mediatek-add-MT7988A-reference-board-devic.patch`,
    `189-arm64-dts-mediatek-mt7988a-complete-bpi-r4.patch`,
    `190-arm64-dts-mediatek-mt7622-fix-GICv2-range.patch`,
    `195-dts-mt7986a-bpi-r3-leds-port-names-and-wifi-eeprom.patch`,
    `197-arm64-dts-mediatek-mt7986-correct-timer-frequency.patch`,
    `330-snand-mtk-bmt-support.patch`,
    `331-mt7622-rfb1-enable-bmt.patch`,
    `360-pinctrl-add-pinctrl-driver-for-mt7987-from-sdk.patch`,
    `410-bt-mtk-serial-fix.patch`,
    `411-mtd-spinand-fix-support-for-FORESEE.patch`,
    `431-drivers-spi-mt65xx-Move-chip_config-to-driver-s-priv.patch`,
    `432-drivers-spi-Add-support-for-dynamic-calibration.patch`,
    `433-drivers-spi-mem-Add-spi-calibration-hook.patch`,
    `434-drivers-spi-mt65xx-Add-controller-s-calibration-para.patch`,
    `435-drivers-mtd-spinand-Add-calibration-support-for-spin.patch`,
    `436-drivers-mtd-spi-nor-Add-calibration-support-for-spi-.patch`,
    `450-nvmem-add-layout-for-Adtran-devices.patch`,
    `602-arm64-dts-mediatek-add-mt7622-pcie-slot-node.patch`,
    `610-pcie-mediatek-fix-clearing-interrupt-status.patch`,
    `710-pci-pcie-mediatek-add-support-for-coherent-DMA.patch`,
    `740-net-pcs-mtk_lynxi-add-mt7987-support.patch`,
    `741-net-pcs-mtk-lynxi-add-phya-tx-rx-clock-path.patch`,
    `750-net-ethernet-mtk_eth_soc-add-mt7987-support.patch`,
    `821-add-pwm-feature-for-mt7987.patch`,
    `870-iommu-mediatek-v1-add-.of_xlate-and-defer-arm_iommu_.patch`,
    `901-arm-add-cmdline-override.patch`,
    `930-spi-mt65xx-enable-sel-clk.patch`,
    `941-arm64-dts-mt7986-move-cpuboot-in-a-dedicated-node.patch`,
    `944-net-ethernet-mtk_wed-move-dlm-a-dedicated-dts-node.patch`,
    `945-arm64-dts-mt7986-move-ilm-in-a-dedicated-node.patch`,
    `946-arm64-dts-mt7986-move-dlm-in-a-dedicated-node.patch`,
    `950-smartrg-i2c-led-driver.patch`,
    `955-dts-mt7968a-bpi-r3-add-label-to-gmac-for-sfp1-port.patch`,
    `960-asus-hack-u-boot-ignore-mtdparts.patch`,
    `965-dts-mt7988a-add-trng-support.patch`,
    `966-pcie-mediatek-gen3-Add-WIFI-HW-reset-flow.patch`,
    `968-arm64-dts-mediatek-mt7988a-bpi-r4-pro-add-lan-wan-overlays.patch`,
    `971-arm64-dts-mediatek-mt7988a-add-support-for-bpi-r4-pro-4e.patch`.
  - `999-mediatek-mtk_wed-ppe_check-wcid.patch` added: updates `mtk_wed_ppe_check()`
    to the new `u16 wcid` signature required by the generic WED flow API
    backport.

- `target/linux/mediatek/*/config-7.3`
  - 63 new defaults appended per subtarget: `CONFIG_SCHED_CACHE=y` and 62
    `# CONFIG_... is not set` / `CONFIG_...=y` entries for symbols that are
    new in 7.3, including explicit off for `CONFIG_ARCH_BST`,
    `CONFIG_ARCH_MICROCHIP`, `CONFIG_ARM_MHU_V2`, `CONFIG_ARM_MHU_V3`,
    `CONFIG_MTK_ADSP_MBOX`, `CONFIG_MTK_CMDQ_MBOX` and `CONFIG_MTK_VCP_MBOX`,
    and explicit on for `CONFIG_SCHED_CACHE`, `CONFIG_ARM64_ERRATUM_4311569`,
    `CONFIG_PINCTRL_MT6858`, `CONFIG_PINCTRL_MT6878`,
    `CONFIG_MTK_GPUEB_MBOX`, `CONFIG_MTK_MFG_PM_DOMAIN`,
    `CONFIG_SWIOTLB_DEFAULT_SIZE_MB=64`.

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on mediatek:

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
