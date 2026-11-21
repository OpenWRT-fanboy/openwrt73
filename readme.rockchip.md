# rockchip Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on rockchip, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`):** armv7.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for rockchip:

- `target/linux/rockchip/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/rockchip/patches-7.3`
  - 107 outdated backports removed (now upstream in 7.3 or versioned backports):
    `001-16-v6.19-arm64-dts-rockchip-add-eMMC-CQE-support-for-rk3588.patch`,
    `010-v6.19-arm64-dts-rockchip-add-LinkEase-EasePi-R1.patch`,
    `037-04-v6.19-mmc-sdhci-of-dwcmshc-Add-command-queue-support-for-rockch.patch`,
    `037-05-v6.19-mmc-sdhci-of-dwcmshc-Fix-command-queue-support-for-RK3576.patch`,
    `037-06-v6.19-mmc-sdhci-of-dwcmshc-Disable-internal-clock-auto-gate-for.patch`,
    `037-07-v6.19-mmc-sdhci-of-dwcmshc-reduce-CIT-for-better-performance.patch`,
    `038-1-v7.1-nvmem-rockchip-otp-Handle-internal-word_size-in-main.patch`,
    `038-2-v7.1-nvmem-rockchip-otp-Add-support-for-RK3568.patch`,
    `038-3-v7.1-nvmem-rockchip-otp-Add-support-for-RK3562.patch`,
    `038-4-v7.1-nvmem-rockchip-otp-Add-support-for-RK3528.patch`,
    `039-1-v7.2-phy-rockchip-inno-usb2-Simplify-rockchip-usbgrf-hand.patch`,
    `039-2-v7.2-phy-rockchip-inno-usb2-Add-clkout_ctl_phy-support.patch`,
    `039-3-v7.2-phy-rockchip-inno-usb2-Add-support-for-RK3528.patch`,
    `045-01-v6.19-media-v4l2-mem2mem-Document-that-v4l2_m2m_get_vq-never-retur.patch`,
    `045-02-v6.19-media-v4l2-mem2mem-Don-t-copy-frame-flags-in-v4l2_m2m_buf_co.patch`,
    `045-03-v6.19-media-v4l2-ctrls-add-full-AV1-profile-validation-in-validate.patch`,
    `045-04-v6.19-media-v4l2-ctrls-set-AV1-sequence-flags-for-testing.patch`,
    `045-05-v6.19-media-rkvdec-Add-HEVC-backend.patch`,
    `045-06-v6.19-media-rkvdec-Add-variants-support.patch`,
    `045-07-v6.19-media-rkvdec-Implement-capability-filtering.patch`,
    `045-08-v6.19-media-rkvdec-Add-RK3288-variant.patch`,
    `045-09-v6.19-media-rkvdec-Disable-QoS-for-HEVC-and-VP9-on-RK3328.patch`,
    `045-10-v6.19-media-dt-bindings-rockchip-vdec-Add-RK3288-compatible.patch`,
    `045-15-v7.0-media-v4l2-mem2mem-Add-a-kref-to-the-v4l2_m2m_dev-structure.patch`,
    `045-16-v7.0-media-verisilicon-Avoid-G2-bus-error-while-decoding-H.264-an.patch`,
    `045-20-v7.0-media-v4l2-core-simplify-v4l2_m2m_register_entity.patch`,
    `045-22-v7.0-media-v4l2-ctrls-Add-hevc_ext_sps_-ls-t_rps-controls.patch`,
    `045-23-v7.0-media-rkvdec-Switch-to-using-structs-instead-of-writel.patch`,
    `045-24-v7.0-media-rkvdec-Move-cabac-tables-to-their-own-source-file.patch`,
    `045-25-v7.0-media-rkvdec-Use-structs-to-represent-the-HW-RPS.patch`,
    `045-26-v7.0-media-rkvdec-Move-h264-functions-to-common-file.patch`,
    `045-27-v7.0-media-rkvdec-Move-hevc-functions-to-common-file.patch`,
    `045-28-v7.0-media-rkvdec-Add-variant-specific-coded-formats-list.patch`,
    `045-29-v7.0-media-rkvdec-Add-RCB-and-SRAM-support.patch`,
    `045-30-v7.0-media-rkvdec-Support-per-variant-interrupt-handler.patch`,
    `045-31-v7.0-media-rkvdec-Enable-all-clocks-without-naming-them.patch`,
    `045-32-v7.0-media-rkvdec-Disable-multicore-support.patch`,
    `045-33-v7.0-media-rkvdec-Add-H264-support-for-the-VDPU381-variant.patch`,
    `045-34-v7.0-media-rkvdec-Add-H264-support-for-the-VDPU383-variant.patch`,
    `045-35-v7.0-media-rkvdec-Add-HEVC-support-for-the-VDPU381-variant.patch`,
    `045-36-v7.0-media-rkvdec-Add-HEVC-support-for-the-VDPU383-variant.patch`,
    `045-37-v7.0-treewide-Replace-kmalloc-with-kmalloc_obj-for-non-scalar-typ.patch`,
    `045-38-v7.0-Convert-alloc_obj-family-to-use-the-new-default-GFP_KERNEL-a.patch`,
    `045-40-v7.0-media-rkvdec-Improve-handling-missing-short-long-term-RPS.patch`,
    `045-41-v7.0-media-rkvdec-reduce-excessive-stack-usage-in-assemble_hw_pps.patch`,
    `045-43-v7.0-media-verisilicon-Fix-kernel-panic-due-to-__initconst-misuse.patch`,
    `045-48-v7.2-media-rkvdec-Introduce-a-global-bitwriter-helper.patch`,
    `045-49-v7.2-media-rkvdec-Use-the-global-bitwriter-instead-of-local-one.patch`,
    `045-50-v7.2-media-rkvdec-common-Drop-bitfields-for-the-bitwriter.patch`,
    `045-51-v7.2-media-rkvdec-vdpu383-Drop-bitfields-for-the-bitwriter.patch`,
    `045-52-v7.2-media-verisilicon-remove-hantro_run-declaration.patch`,
    `045-53-v7.3-media-rkvdec-hevc-tighten-EXT-SPS-RPS-control-dimensions.patch`,
    `045-54-v7.3-media-v4l2-ctrls-validate-HEVC-EXT-SPS-RPS-counts.patch`,
    `045-55-v7.3-media-rkvdec-hevc-guard-INTER_REF_PIC_SET_PRED-index-underfl.patch`,
    `045-57-v7.3-media-rkvdec-use-DIV_ROUND_UP-for-CTB-counts.patch`,
    `045-58-v7.3-media-platform-hantro_drv-Add-missing-media_entity_cleanup.patch`,
    `045-59-v6.19-media-dt-bindings-add-rockchip-px30-vip.patch`,
    `045-60-v6.19-media-dt-bindings-add-rockchip-rk3568-vicap.patch`,
    `045-61-v6.19-media-rockchip-add-driver-for-the-rockchip-camera-interfac.patch`,
    `045-62-v6.19-media-rockchip-rkcif-add-abstraction-for-interface-and-cro.patch`,
    `045-63-v6.19-media-rockchip-rkcif-add-abstraction-for-dma-blocks.patch`,
    `045-64-v6.19-media-rockchip-rkcif-add-support-for-px30-vip-dvp-capture.patch`,
    `045-65-v6.19-media-rockchip-rkcif-add-support-for-rk3568-vicap-dvp-capt.patch`,
    `045-66-v6.19-media-rockchip-rkcif-add-support-for-rk3568-vicap-mipi-cap.patch`,
    `045-67-v7.0-media-dt-bindings-add-rockchip-mipi-csi-2-receiver.patch`,
    `045-68-v7.0-media-synopsys-add-driver-for-the-designware-mipi-csi-2-re.patch`,
    `045-69-v7.0-media-synopsys-csi2rx-fix-out-of-bounds-check-for-formats-.patch`,
    `045-70-v7.1-media-synopsys-csi2rx-use-devm_reset_control_get_optional_.patch`,
    `045-71-v7.1-media-synopsys-csi2rx-only-check-errors-from-devm_clk_bulk.patch`,
    `045-72-v7.1-media-synopsys-csi2rx-implement-.get_frame_desc-callback.patch`,
    `045-73-v7.1-media-synopsys-csi2rx-Use-enum-and-u32-array-for-register-.patch`,
    `045-74-v7.1-media-dt-bindings-add-NXP-i.MX93-compatible-string.patch`,
    `045-75-v7.1-media-synopsys-csi2rx-add-i.MX93-support.patch`,
    `045-76-v7.1-media-rockchip-rkcif-fix-off-by-one-bugs.patch`,
    `045-77-v7.1-media-rockchip-rkcif-comply-with-minimum-number-of-buffers.patch`,
    `045-78-v7.1-media-rockchip-rkcif-Add-missing-MUST_CONNECT-flag-to-pads.patch`,
    `045-79-v7.2-media-synopsys-Fix-IPI-using-hardcoded-datatype.patch`,
    `045-80-v7.2-media-synopsys-Add-support-for-RAW16-Bayer-formats.patch`,
    `045-81-v7.2-media-synopsys-Add-support-for-multiple-streams.patch`,
    `045-82-v7.2-media-synopsys-Add-PHY-stopstate-wait-for-i.MX93.patch`,
    `045-83-v7.2-media-synopsys-Add-support-for-i.MX95.patch`,
    `045-84-v7.2-media-dt-bindings-add-rockchip-rk3588-vicap.patch`,
    `045-85-v7.2-media-rockchip-rkcif-add-support-for-rk3588-vicap-mipi-cap.patch`,
    `045-86-v7.2-media-dt-bindings-rockchip-rk3568-mipi-csi2-add-rk3588-com.patch`,
    `052-v6.19-arm64-dts-rockchip-Add-devicetree-for-the-FriendlyElec-Na.patch`,
    `053-v6.19-arm64-dts-rockchip-Fix-SD-card-support-for-RK3576-Na.patch`,
    `070-26-v6.19-arm64-dts-rockchip-Add-PCIe-Gen2x1-controller-for-RK3528.patch`,
    `071-14-v6.19-arm64-dts-rockchip-Enable-PCIe-controller-on-Radxa-E20C.patch`,
    `072-1-v7.1-arm64-dts-rockchip-Enable-OTP-controller-for-RK3562.patch`,
    `072-2-v7.1-arm64-dts-rockchip-Enable-OTP-controller-for-RK356x.patch`,
    `072-3-v7.1-arm64-dts-rockchip-Enable-OTP-controller-for-RK3528.patch`,
    `073-1-v7.2-arm64-dts-rockchip-Add-USB-nodes-for-RK3528.patch`,
    `073-2-v7.2-arm64-dts-rockchip-Enable-USB-2.0-ports-on-Radxa-E20.patch`,
    `074-02-v7.0-arm64-dts-rockchip-Add-the-vdpu381-Video-Decoders-on-RK3588.patch`,
    `074-04-v7.1-arm64-dts-rockchip-add-node-name-for-RK3588_PD_RKVDEC0-1-and.patch`,
    `074-05-v7.2-arm64-dts-rockchip-Update-vdec-register-blocks-order-on-RK35.patch`,
    `074-06-v7.2-arm64-dts-rockchip-add-mipi-csi-2-receiver-nodes-to-rk3588.patch`,
    `074-07-v7.2-arm64-dts-rockchip-add-vicap-node-to-rk3588.patch`,
    `101-arm64-dts-rockchip-Add-HINLINK-H28K.patch`,
    `113-rock-pi-s-add-led-aliases-and-stop-heartbeat.patch`,
    `130-arm64-dts-rockchip-Update-LED-properties-for-Radxa-ROCK-5-ITX.patch`,
    `134-arm64-dts-rockchip-Update-LED-properties-for-Radxa-ROCK-4D.patch`,
    `139-arm64-dts-rockchip-Update-LED-properties-for-Radxa-ROCK-2.patch`,
    `170-03-dt-bindings-phy-rockchip-inno-usb2phy-add-rv1126.patch`,
    `173-02-arm-dts-rockchip-add-i2c-and-spi-controllers-to-rv1126.patch`,
    `180-02-media-rkisp2-add-parameters-output-video-node.patch`,
    `188-01-dt-bindings-nvmem-rockchip-otp-add-rv1126.patch`,
  - 53 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `104-phy-rockchip-naneng-combphy-Fix-TX-detect-RX.patch`,
    `105-nanopi-r4s-sd-signalling.patch`,
    `106-r4s-openwrt-leds.patch`,
    `112-radxa-e25-add-led-aliases-and-stop-heartbeat.patch`,
    `116-arm64-dts-rockchip-Update-LED-properties-for-Radxa-Ro.patch`,
    `120-arm64-dts-rockchip-add-led-aliases-and-stop-heartbeat-for-nanopc-t6.patch`,
    `135-drm-rockchip-select-SND_SOC_HDMI_CODEC-for-DW-HDMI-QP.patch`,
    `142-iommu-rockchip-translate-DMA-for-IOMMU-masters.patch`,
    `161-01-thermal-rockchip-Change-to-use-bulk-clks.patch`,
    `161-03-arm64-dts-rockchip-Add-TSADC-controller-for-RK3528.patch`,
    `170-01-phy-rockchip-inno-usb2-add-otg-bypass-controls.patch`,
    `170-02-phy-rockchip-inno-usb2-skip-host-sm-without-linestate.patch`,
    `170-04-phy-rockchip-inno-usb2-skip-chg-detect-without-regs.patch`,
    `170-05-phy-rockchip-inno-usb2-add-rv1126-support.patch`,
    `170-06-dt-bindings-usb-rockchip-dwc3-add-rv1126.patch`,
    `170-07-arm-dts-rockchip-add-usb-nodes-to-rv1126.patch`,
    `171-01-thermal-rockchip-pass-the-grf-to-set-tshut-mode.patch`,
    `171-04-arm-dts-rockchip-add-tsadc-and-thermal-zones-to-rv1126.patch`,
    `172-01-dt-bindings-phy-rockchip-inno-csi-dphy-add-rv1126.patch`,
    `172-02-phy-rockchip-inno-csidphy-add-rv1126-support.patch`,
    `172-05-media-dt-bindings-rockchip-rk3568-mipi-csi2-add-rv1126.patch`,
    `172-07-arm-dts-rockchip-add-camera-capture-nodes-to-rv1126.patch`,
    `173-01-arm-dts-rockchip-add-i2c-and-spi-pin-groups-to-rv1126.patch`,
    `174-01-cpufreq-dt-platdev-add-rv1126-to-the-allowlist.patch`,
    `174-02-arm-dts-rockchip-add-cpu-opps-and-cooling-to-rv1126.patch`,
    `175-01-arm-dts-rockchip-add-audio-pin-groups-to-rv1126.patch`,
    `175-02-arm-dts-rockchip-add-i2s1-i2s2-and-pdm-to-rv1126.patch`,
    `176-03-arm-dts-rockchip-add-vpu-to-rv1126.patch`,
    `177-01-media-dt-bindings-rockchip-rga-add-rv1126.patch`,
    `177-02-arm-dts-rockchip-add-rga-to-rv1126.patch`,
    `178-02-leds-flash-add-driver-for-pwm-driven-flash-leds.patch`,
    `179-02-crypto-rockchip-add-rk3588-driver.patch`,
    `179-04-crypto-rockchip-rework-the-crypto-v2-driver-and-add-.patch`,
    `179-06-pmdomain-rockchip-add-the-crypto-domain-of-the-rv112.patch`,
    `179-07-arm-dts-rockchip-add-the-crypto-block-to-rv1126.patch`,
    `179-10-arm-dts-rockchip-add-rng-to-rv1126.patch`,
    `180-01-media-rockchip-rkisp2-add-rkisp2-driver.patch`,
    `180-05-arm64-dts-rockchip-add-isp-nodes-to-rk3588.patch`,
    `181-05-media-rockchip-rkisp2-set-the-dma-segment-size.patch`,
    `181-06-media-rockchip-rkisp2-set-the-csc-defaults-by.patch`,
    `181-09-media-rockchip-rkisp2-keep-the-reset-bits-of-sws-cfg.patch`,
    `181-10-media-rockchip-rkisp2-set-the-csm-range-from-the-pad.patch`,
    `182-01-iommu-rockchip-map-the-mmu-registers-non-exclusively.patch`,
    `182-04-arm-dts-rockchip-rv1126-add-isp2-0-ispp-and-vicap.patch`,
    `183-04-arm-dts-rockchip-rv1126-add-the-rkvenc-video-encoder.patch`,
    `183-07-arm-dts-rockchip-rv1126-add-the-rkvenc-operating.patch`,
    `183-08-arm-dts-rockchip-rv1126-bind-the-rkvenc-to-the-npu.patch`,
    `188-02-nvmem-rockchip-otp-add-rv1126-read-support.patch`,
    `188-03-arm-dts-rockchip-add-rv1126-otp-cells.patch`,
    `189-02-pmdomain-rockchip-add-rv1126-npu-domain.patch`,
    `189-03-arm-dts-rockchip-add-rv1126-npu-power-domain.patch`,
    `400-2-arm64-dts-rockchip-Fix-regulators-gmac-and-naming-on.patch`,
    `400-3-arm64-dts-rockchip-Improve-LEDs-on-NanoPi-R6C-R6S.patch`,

- `target/linux/rockchip/config-7.3`
  - 80 new defaults appended for symbols introduced in 7.3 (universal set
    plus arm architecture-specific symbols). These are inferred from the
    reference 7.3 (4/4) commits; confirm with `make kernel_oldconfig` for this
    target before relying on them.

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on rockchip:

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
