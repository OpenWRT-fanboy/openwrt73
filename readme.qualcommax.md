# qualcommax Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on qualcommax, and the patches used to make them work.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for qualcommax:

- `target/linux/qualcommax/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.

- `target/linux/qualcommax/patches-7.3`
  - 17 outdated backports removed as they are now upstream in 7.3:
    `0073-v7.0-arm64-dts-qcom-ipq5018-Remove-tsens-v1-fallback-compatible.patch`,
    `0075-v7.0-arm64-dts-qcom-ipq5018-Correct-USB-DWC3-wrapper-interrupts.patch`,
    `0076-v7.2-dt-bindings-pwm-add-IPQ6018-binding.patch`,
    `0077-v7.2-pwm-Driver-for-qualcomm-ipq6018-pwm-block.patch`,
    `0078-v7.3-arm64-dts-qcom-ipq6018-add-pwm-node.patch`,
    `0079-v7.3-arm64-dts-qcom-ipq5018-add-pwm-node.patch`,
    `0080-v7.1-dt-bindings-clock-qcom-Add-CMN-PLL-support-for-IPQ6018.patch`,
    `0081-v7.1-dt-bindings-clock-qcom-Add-CMN-PLL-support-for-IPQ8074.patch`,
    `0082-v7.1-clk-qcom-ipq-cmn-pll-Add-IPQ6018-SoC-support.patch`,
    `0083-v7.1-clk-qcom-ipq-cmn-pll-Add-IPQ8074-SoC-support.patch`,
    `0087-v7.2-dt-bindings-net-ethernet-phy-increase-max-clock-count-to-two.patch`,
    `0088-v7.2-dt-bindings-net-qca-ar803x-Add-clocks-for-IPQ5018-PHY.patch`,
    `0089-v7.2-net-phy-at803x-add-RX-and-TX-clock-management-for-IPQ5018-PHY.patch`,
    `0091-v6.19-dt-bindings-usb-qcom-snps-dwc3-Correct-IPQ5018-interrupts.patch`,
    `0092-v7.3-pinctrl-qcom-ipq5018-add-missing-pwm3-function-on-gpio13.patch`,
    `0305-pinctrl-qcom-IPQ5018-update-pwm-groups.patch`,
    `0917-clk-qcom-gcc-ipq6018-mark-gcc_xo_clk_src-as-critical.patch`.
  - 5 new patches added for the hexagon-based WCSS secure PIL remoteproc
    and its TME-L QMP mailbox prerequisites:
    `00730-01-mailbox-qcom-share-TME-L-QMP-client-header.patch`,
    `00730-02-dt-bindings-remoteproc-qcom-document-hexagon-based-wcss-secure-pil.patch`,
    `00730-03-remoteproc-qcom-add-hexagon-based-wcss-secure-pil-driver.patch`,
    `00730-04-remoteproc-qcom-wcss-sec-add-split-firmware-support.patch`,
    `00730-05-dt-bindings-remoteproc-wcss-sec-describe-split-firmware.patch`.
  - 33 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `0084-01-Correct-IPQ8074-NSS-NoC-rate.patch`,
    `0090-v7.4-clk-qcom-gcc-ipq5018-mark-gpll0_main-clock-as-critical.patch`,
    `0120-arm64-dts-qcom-ipq8074-add-secure-WCSS-remoteproc.patch`,
    `0121-arm64-dts-ipq8074-Add-WLAN-node.patch`,
    `0140-usb-dwc3-core-Allow-glue-layer-to-pass-reference-clo.patch`,
    `0142-arm64-dts-qcom-ipq5018-Flatten-usb-controller-node.patch`,
    `0145-arm64-dts-qcom-ipq8074-move-DR-mode-to-board-DTS.patch`,
    `0146-arm64-dts-qcom-ipq8074-Flatten-usb-controller-nodes.patch`,
    `0151-phy-qualcomm-qcom-uniphy-pcie-28lp-Convert-to-PCIe-U.patch`,
    `0157-dt-bindings-usb-qcom-snps-dwc3-Add-clocks-for-USB3-o.patch`,
    `0184-mailbox-tmelite-qmp-Introduce-TMEL-QMP-mailbox-driver.patch`,
    `0185-firmware-qcom_scm-ipq5332-add-support-to-pass-metadata-size.patch`,
    `0189-arm64-dts-qcom-ipq5018-add-nodes-to-bringup-q6.patch`,
    `0314-spi-spi-gpio-Implement-spidelay-when-requested-bit-r.patch`,
    `0400-mtd-rawnand-add-support-for-TH58NYG3S0HBAI4.patch`,
    `0401-spi-spi-qpic-snand-default-to-4-bit-ECC.patch`,
    `0411-mtd-rawnand-qpic-only-support-max-4-bytes-ID.patch`,
    `0412-mtd-spinand-qpic-only-support-max-4-bytes-ID.patch`,
    `0721-clk-gcc-ipq5018-remove-the-unsupported-clk-combinati.patch`,
    `0723-clk-qcom-gcc-ipq5018-fix-uniphy-soft-reset-issue.patch`,
    `0803-firmware-qcom_scm-ipq5332-add-msa-lock-unlock-suppor.patch`,
    `0804-remoteproc-qcom-q6v5-Add-multipd-interrupts-support.patch`,
    `0805-remoteproc-qcom-Add-Hexagon-based-multipd-rproc-driv.patch`,
    `0811-firmware-qcom_scm-support-MPD.patch`,
    `0812-soc-qcom-mdt_loader-support-MPD.patch`,
    `0820-dt-bindings-net-wireless-ath11k-add-bindings-for-QCN6122.patch`,
    `0901-regulator-add-Qualcomm-CPR-regulators.patch`,
    `0907-soc-qcom-fix-smp2p-ack-on-ipq6018.patch`,
    `0911-arm64-cmdline-replacement.patch`,
    `0920-clk-add-clk_hw_recalc_rate-to-trigger-HW-clk-rate-re.patch`,
    `0954-net-stmmac-Introduce-Qualcomm-IPQ5018-DWMAC-driver.patch`,
    `0955-net-dsa-tag_qca-add-a-variant-behind-an-ethertype.patch`,
    `0956-net-dsa-qca8k-support-the-qca-etype-tagging-protocol.patch`.

- `target/linux/qualcommax/files/drivers/net/ethernet/qualcomm/qca_ppe_scheduler.c`
  - Updated to the 7.3 devlink parameter API: `ppe_shaper_get()` takes a
    trailing `struct netlink_ext_ack *extack`, and `ppe_shaper_validate()`
    receives `union devlink_param_value *val` by pointer.

- `target/linux/qualcommax/config-7.3`
  - 136 new defaults: 83 `CONFIG_...=y` / `=m` entries and 53
    `# CONFIG_... is not set` entries for symbols that are new in 7.3,
    including explicit off for `CONFIG_NET_DSA_HIRSCHMANN_HELLCREEK`,
    `CONFIG_VIDEO_OV2732`, the new `DRM_PANEL_*` drivers,
    `CONFIG_DRM_LONTIUM_LT8713SX`, `CONFIG_REGULATOR_MT6316`,
    `CONFIG_REGULATOR_MT6363` and `CONFIG_QCOM_SPMI_ADC5_GEN3`.

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on qualcommax:

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
