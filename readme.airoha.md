# airoha Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on airoha, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`):** an7581, an7583.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for airoha:

- `target/linux/airoha/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.

- `target/linux/airoha/patches-7.3`
  - 109 outdated backports removed as they are now upstream in 7.3:
    `029-05-v6.19-spi-airoha-remove-unnecessary-restriction-length.patch`,
    `029-06-v6.19-spi-airoha-remove-unnecessary-switch-to-non-dma-mode.patch`,
    `029-07-v6.19-spi-airoha-unify-dirmap-read-write-code.patch`,
    `029-08-v6.19-spi-airoha-support-of-dualio-quadio-flash-reading-co.patch`,
    `029-09-v6.19-spi-airoha-avoid-setting-of-page-oob-sizes-in-REG_SP.patch`,
    `029-10-v6.19-spi-airoha-reduce-the-number-of-modification-of-REG_.patch`,
    `029-11-v6.19-spi-airoha-set-custom-sector-size-equal-to-flash-pag.patch`,
    `029-12-v6.19-spi-airoha-avoid-reading-flash-page-settings-from-SN.patch`,
    `029-13-v6.19-spi-airoha-buffer-must-be-0xff-ed-before-writing.patch`,
    `096-v6.19-net-airoha-Add-missing-stats-to-ethtool_eth_mac_stat.patch`,
    `097-v6.19-net-airoha-Add-get_link-ethtool-callback.patch`,
    `099-06-v6.19-net-airoha-ppe-Remove-airoha_ppe_is_enabled-where-no.patch`,
    `099-07-v6.19-net-airoha-ppe-Configure-SRAM-PPE-entries-via-the-cp.patch`,
    `099-08-v6.19-net-airoha-ppe-Flush-PPE-SRAM-table-during-PPE-setup.patch`,
    `099-09-v6.19-net-airoha-Select-default-ppe-cpu-port-in-airoha_dev.patch`,
    `099-11-v6.19-net-airoha-ppe-Do-not-use-magic-numbers-in-airoha_pp.patch`,
    `102-02-v6.19-net-airoha-npu-Add-airoha_npu_soc_data-struct.patch`,
    `102-03-v6.19-net-airoha-npu-Add-7583-SoC-support.patch`,
    `107-v6.19-pwm-airoha-Add-support-for-EN7581-SoC.patch`,
    `114-v6.19-pinctrl-airoha-convert-comma-to-semicolon.patch`,
    `118-v7.0-net-airoha-npu-Dump-fw-version-during-probe.patch`,
    `120-v7.0-net-airoha-implement-get_link_ksettings.patch`,
    `121-v7.0-net-airoha-npu-Init-BA-memory-region-if-provided-via.patch`,
    `122-v7.0-net-airoha_eth-increase-max-MTU-to-9220-for-DSA-jumb.patch`,
    `123-v7.0-net-airoha-npu-Add-the-capability-to-read-firmware-n.patch`,
    `125-v7.1-net-airoha-Rely-__field_prep-for-non-constant-masks.patch`,
    `126-v7.1-net-airoha-Make-flow-control-source-port-mapping-dep.patch`,
    `127-v7.1-net-airoha-Move-GDM-forward-port-configuration-in-nd.patch`,
    `129-v7.1-net-airoha-select-QDMA-block-according-LAN-WAN-confi.patch`,
    `131-v7.0-net-phy-mediatek-enable-interrupts-on-AN7581.patch`,
    `132-v7.1-net-airoha-Reset-PPE-default-cput-port-in-airoha_ppe.patch`,
    `134-v7.1-net-airoha-Delay-offloading-until-all-net_devices-ar.patch`,
    `142-01-v7.1-net-airoha-Rely-on-net_device-pointer-in-airoha_dev_.patch`,
    `142-02-v7.1-net-airoha-Rely-on-net_device-pointer-in-HTB-callbac.patch`,
    `142-03-v7.1-net-airoha-Rely-on-net_device-pointer-in-ETS-callbac.patch`,
    `142-04-v7.1-net-airoha-Remove-PCE_MC_EN_MASK-bit-in-REG_FE_PCE_C.patch`,
    `143-v7.1-net-airoha-Fix-typo-in-airoha_set_gdm2_loopback-rout.patch`,
    `144-v7.1-net-airoha-Set-REG_RX_CPU_IDX-once-in-airoha_qdma_fi.patch`,
    `147-v7.1-net-airoha-Fix-PPE-cpu-port-configuration-for-GDM2-l.patch`,
    `155-v7.2-net-airoha-Rename-get_src_port_id-callback-in-get_sp.patch`,
    `158-v7.2-net-airoha-configure-QoS-channel-for-HW-accelerated-.patch`,
    `159-v7.2-net-airoha-Introduce-airoha_fe_get-airoha_qdma_get-r.patch`,
    `161-01-v7.2-net-airoha-Introduce-airoha_gdm_dev-struct.patch`,
    `161-02-v7.2-net-airoha-Move-airoha_qdma-pointer-in-airoha_gdm_de.patch`,
    `161-03-v7.2-net-airoha-Rely-on-airoha_gdm_dev-pointer-in-airoha_.patch`,
    `161-04-v7.2-net-airoha-Move-qos_sq_bmap-in-airoha_gdm_dev-struct.patch`,
    `161-05-v7.2-net-airoha-Move-cpu-fwd-_tx_packets-in-airoha_gdm_de.patch`,
    `161-06-v7.2-net-airoha-Rename-airoha_set_gdm2_loopback-in-airoha.patch`,
    `163-v7.2-net-airoha-Report-extack-error-to-the-user-if-airoha.patch`,
    `165-01-v7.2-net-airoha-Remove-private-net_device-pointer-in-airo.patch`,
    `165-02-v7.2-net-airoha-Support-multiple-net_devices-for-a-single.patch`,
    `165-03-v7.2-net-airoha-Do-not-stop-GDM-port-if-it-is-shared.patch`,
    `165-04-v7.2-net-airoha-Introduce-WAN-device-flag.patch`,
    `165-05-v7.2-net-airoha-Support-multiple-LAN-WAN-interfaces-for-h.patch`,
    `166-v7.2-net-airoha-better-handle-MIBs-for-GDM-ports-with-mul.patch`,
    `167-v7.2-net-airoha-use-int-instead-of-atomic_t-for-qdma-user.patch`,
    `168-v7.2-net-airoha-move-get_sport-callback-at-the-beginning-.patch`,
    `169-v7.2-net-airoha-simplify-WAN-device-check-in-airoha_dev_i.patch`,
    `173-v7.2-net-airoha-Fix-non-standard-return-value-in-airoha_p.patch`,
    `175-v7.2-net-airoha-Fix-TX-scheduler-queue-mask-loop-upper-bo.patch`,
    `176-v7.2-net-airoha-Fix-typos-in-comments-and-Kconfig.patch`,
    `177-v7.2-net-airoha-Fix-off-by-one-in-airoha_tc_remove_htb_qu.patch`,
    `178-v7.2-net-airoha-fix-netif_set_real_num_tx_queues-for-spar.patch`,
    `179-v7.2-pinctrl-airoha-Fix-type-in-.pin_config_group_get-cal.patch`,
    `180-01-v7.2-pinctrl-Move-Airoha-driver-to-dedicated-directory.patch`,
    `181-v7.3-net-airoha-npu-load-the-firmware-without-the-sysfs-fall.patch`,
    `185-v7.2-net-airoha-Fix-error-handling-in-airoha_ppe_flush_sr.patch`,
    `186-v7.2-net-airoha-Fix-MODULE_LICENSE-to-match-SPDX-GPL-2.0-.patch`,
    `187-v7.3-net-airoha-Add-retry-mechanism-to-airoha_qdma_set_tr.patch`,
    `188-v7.2-net-airoha-fix-BQL-underflow-in-shared-QDMA-TX-ring.patch`,
    `189-v7.2-net-airoha-dma-map-xmit-frags-with-skb_frag_dma_map.patch`,
    `190-v7.2-net-airoha-fix-max-receive-size-configuration.patch`,
    `191-v7.2-net-airoha-add-preliminary-support-to-configure-tx-h.patch`,
    `192-v7.2-net-airoha-fix-MIB-stats-collection-to-be-lossless.patch`,
    `193-01-v7.2-net-airoha-rename-airoha_priv_flags-to-airoha_dev_fl.patch`,
    `193-02-v7.2-net-airoha-fix-ETS-QoS-stats-counter-underflow-and-c.patch`,
    `193-03-v7.2-net-airoha-defer-GDM3-GDM4-WAN-mode-and-GDM2-loopbac.patch`,
    `202-06-v7.3-pinctrl-airoha-fix-I2C1-pin-mux-config-for-AN758.patch`,
    `202-07-v7.3-pinctrl-airoha-fix-I2C-pin-mux-config-for-AN7583.patch`,
    `202-08-v7.3-pinctrl-airoha-fix-AN7583-MDIO-pin-mux-config.patch`,
    `202-11-v7.3-pinctrl-airoha-add-set_direction-helper-for-gpio.patch`,
    `202-12-v7.3-pinctrl-airoha-minor-improvements.patch`,
    `202-17-v7.3-pinctrl-airoha-remove-not-needed-irq_type-array.patch`,
    `202-18-v7.3-pinctrl-airoha-statically-allocate-gpio-regs-str.patch`,
    `202-19-v7.3-pinctrl-airoha-move-common-definitions-to-the-se.patch`,
    `202-20-v7.3-pinctrl-airoha-split-driver-on-shared-code-and-S.patch`,
    `202-21-v7.3-pinctrl-airoha-an7581-remove-en7581-prefix-from-.patch`,
    `202-22-v7.3-pinctrl-airoha-an7583-remove-an7583-prefix-from-.patch`,
    `202-23-v7.3-pinctrl-airoha-an7583-rename-registers-to-match-.patch`,
    `202-24-v7.3-pinctrl-airoha-an7583-add-support-for-npu_uart-p.patch`,
    `202-25-v7.3-pinctrl-airoha-an7583-add-support-for-pon_alt-pi.patch`,
    `202-26-v7.3-pinctrl-airoha-an7583-add-support-for-olt-pinmux.patch`,
    `202-27-v7.3-pinctrl-airoha-add-support-of-en7523-SoC.patch`,
    `202-28-v7.3-pinctrl-airoha-try-to-find-chip-scu-node-by-phan.patch`,
    `203-06-pinctrl-airoha-fix-AN7583-SPI-pin-mux-config.patch`,
    `402-01-thermal-airoha-convert-to-regmap-API.patch`,
    `402-02-thermal-drivers-airoha-Generalize-probe-function.patch`,
    `402-03-thermal-drivers-airoha-generalize-get_thermal_ADC-an.patch`,
    `402-05-thermal-drivers-airoha-Add-support-for-AN7583.patch`,
    `402-06-thermal-drivers-airoha-serialise-access-to-the-shared-ADC.patch`,
    `402-07-thermal-drivers-airoha-read-all-three-AN7583-sensors.patch`,
    `600-11-dt-bindings-clock-airoha-Add-reset-support-to-EN7523.patch`,
    `600-12-v6.19-clk-en7523-Add-reset-controller-support-for-EN7523-S.patch`,
    `604-01-net-pcs-airoha-add-support-for-AN7583.patch`,
    `607-02-phy-airoha-Add-support-for-Airoha-AN7583-USB-PHY.patch`,
    `607-cpufreq-airoha-fix-probe-failure-with-correct-error-check.patch`,
    `609-01-dt-bindings-clock-airoha-Add-additional-reset-for-PC.patch`,
    `609-02-clk-en7523-add-support-for-dedicated-PCIe-PERSTOUT-r.patch`,
    `913-clk-en7523-reset-PCIE-HB-on-init.patch`.

  - 27 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `182-v7.4-net-airoha-grow-the-small-RX-rings.patch`,
    `200-02-ASoC-airoha-Add-AFE-and-I2S-driver-for-Airoha-AN7581.patch`,
    `203-02-pinctrl-airoha-reset-SCU-IOMUX-registers-at-probe.patch`,
    `203-08-pinctrl-airoha-fix-AN7583-eMMC-pin-mux-config.patch`,
    `220-05-dt-bindings-phy-Add-documentation-for-Airoha-AN7581-.patch`,
    `220-06-phy-move-Airoha-PCIe-PHY-driver-to-dedicated-directo.patch`,
    `220-07-phy-airoha-Add-support-for-Airoha-AN7581-USB-PHY.patch`,
    `220-10-PCI-mediatek-gen3-set-PHY-mode-for-Airoha-EN7581.patch`,
    `221-02-pmdomain-airoha-Add-AN7583-cpufreq-compatible.patch`,
    `310-06-net-airoha-add-initial-fixup-for-GDM3-4-port-support.patch`,
    `600-01-clk-en7523-convert-driver-to-regmap-API.patch`,
    `600-02-clk-en7523-generalize-register-clocks-function.patch`,
    `600-03-clk-en7523-convert-to-full-clk_hw-implementation.patch`,
    `600-04-clk-en7523-add-support-for-.set_rate.patch`,
    `600-05-clk-en7523-permit-to-reference-Chip-SCU-from-phandle.patch`,
    `600-07-clk-en7523-reword-and-clean-clk_probe-variables.patch`,
    `600-08-clk-en7523-add-support-for-probing-SCU-child.patch`,
    `600-10-clk-en7523-add-support-for-Airoha-AN7583-clock.patch`,
    `605-net-pcs-airoha-add-support-for-optional-xfi-reset-li.patch`,
    `606-net-pcs-airoha-fix-an7583-port-count.patch`,
    `607-01-dt-bindings-phy-Add-documentation-for-Airoha-AN7583-USB-PHY.patch`,
    `609-04-PCI-mediatek-gen3-Add-2-lanes-mode-support-for-Airoh.patch`,
    `886-uart-add-en7523-support.patch`,
    `901-snand-mtk-bmt-support.patch`,
    `915-01-net-netfilter-flowtable-Add-the-capability-to-offloa.patch`,
    `915-02-net-airoha-Set-hw-QoS-parameter-according-to-the-pac.patch`,
    `920-13-net-airoha-Rework-MTU-configuration.patch`.

  - Add `600-11-clk-en7523-restore-AN7583-soc-data.patch` and `600-12-clk-en7523-pass-soc-data-to-en751221-hw-init.patch` to restore the AN7583 clock/reset
    soc-data handling that changed in 7.3.

- `target/linux/airoha/*/config-7.3`
  - New 7.3 config defaults appended to the three subtarget configs
    (`en7523`: 43, `an7581`: 82, `an7583`: 83 added lines each, with a
      handful of removed symbols where 7.3 dropped them), including explicit
      off for `CONFIG_ARCH_ZTE`, `CONFIG_AMD_SBTSI` and `CONFIG_LEDS_LP5860_SPI`.

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on ramips:

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
