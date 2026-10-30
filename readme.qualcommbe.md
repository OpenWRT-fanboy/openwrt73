# qualcommbe Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on qualcommbe, and the patches used to make them work.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for qualcommbe:

### Boot-critical fixes (read this first)

Two independent problems crash the boot on IPQ9574 boards (Askey SBE1V1K,
Kiwi DVK). Either one alone produces the crash; both must be in place for a
reliable boot. The crash signature is timing-dependent and moves around:
silent multi-CPU RCU stalls with NMI-unresponsive cores, or panics with
`Oops - Undefined instruction` (ESR `0x02000000`, an *uncategorized*
exception) in scheduler/timer softirq paths (`sched_balance_...`,
`ktime_get_update_offsets_now`), with onset anywhere between 0.2s and 12s.
Because of this variability, a single fix can appear to work once and fail
the next boot - always judge a fix by repeated boots, not one.

**Fix 1: remove the CPU OPP table**
(`patches-7.3/0450-arm64-dts-qcom-ipq9574-remove-cpu-opp-table.patch`)

With the OPP table present, `ARM_QCOM_CPUFREQ_NVMEM` probes and cpufreq
switches the A73 cluster from the bootloader rate (gpll0, 800MHz) to the
lowest OPP (a53pll, 936MHz, 725mV). That switch kills the system. The
patch removes `cpu_opp_table` and the CPUs' `operating-points-v2`
references, so `qcom-cpufreq-nvmem` bails out early with -ENOENT before
any clock is touched (`qcom-cpufreq-nvmem.c:495-500`); the cores stay at
800MHz, the same state the known-good 6.18 runtime effectively used (on
6.18 cpufreq-dt stayed deferred forever and never switched). The boot log
shows `qcom-cpufreq-nvmem qcom-cpufreq-nvmem: probe ... failed with
error -2` - that is the patch working as intended. `cpufreq.off=1` on the
kernel command line is an equivalent runtime knob for testing, but the
patch makes it structural. `config-7.3` deliberately keeps the cpufreq
drivers enabled; disabling them in Kconfig is *not* required.

**Fix 2: port the board DTS to the 7.3 PCIe downstream-port binding**
(`ipq9570-sbe1v1k.dts`, `ipq9570-kiwi-dvk.dts`)

Upstream 7.3 reworked the IPQ9574 PCIe stack for multi-port support:
`pcie-qcom.c` gained `struct qcom_pcie_port` and parses per-port
`reset-gpios` (pcie-qcom.c:1974, :1984), and `ipq9574.dtsi` defines
labelled port nodes (`pcie0_port0` ... `pcie3_port0: pcie@0`). The old
board DTS predates that: `perst-gpios` on the root complex and
hand-written `pcie@0` bridge subnodes under each controller. On 7.3 this
mismatches the driver (ports without their `reset-gpios`, bridge
boilerplate layered onto the port nodes) and wedges the boot during PCIe
enumeration. The board DTS is restructured accordingly: `status` only on
the controller, `reset-gpios`/`wake-gpios` moved to the `&pcieN_port0`
nodes, the `wifi@0` endpoints (pci17cb,1109, QCN9274) as their children,
manual bridge boilerplate dropped.

**Known non-fatal**: after ~45s ath12k logs `No reg rules available`,
`failed to extract regulatory info` and a `WARNING ... wmi.c:6997 at
ath12k_wmi_op_rx` on the first regulatory event. Runtime ath12k noise;
the boot and the other radios are unaffected.

- `target/linux/qualcommbe/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.

- `target/linux/qualcommbe/patches-7.3`
  - 3 outdated backports removed as they are now upstream in 7.3:
    `0400-dt-bindings-pwm-add-IPQ6018-binding.patch`,
    `0401-pwm-driver-for-qualcomm-ipq6018-pwm-block.patch`,
    `0402-arm64-dts-qcom-ipq9574-add-pwm-node.patch`.
  - 1 new patch added: `0450-arm64-dts-qcom-ipq9574-remove-cpu-opp-table.patch`
    (see "Fix 1" above).
  - 23 patches refreshed to apply cleanly on 7.3:
    `0100-arm64-dts-qcom-ipq9574-add-reset-to-SDHC.patch`,
    `0309-net-phy-Add-phy_package_remove_once-helper.patch`,
    `0324-arm64-dts-qcom-ipq9574-add-PCS-uniphy-nodes.patch`,
    `0325-MAINTAINERS-Add-maintainer-for-Qualcomm-PPE-driver.patch`,
    `0327-net-ethernet-qualcomm-Add-phylink-support-for-PPE-MA.patch`,
    `0331-net-ethernet-qualcomm-Add-EDMA-support-for-QCOM-IPQ9.patch`,
    `0342-net-qualcomm-Update-IPQ9574-PPE-driver.patch`,
    `0343-arm64-dts-qcom-Add-IPQ9574-PPE-base-device-node.patch`,
    `0344-arm64-dts-qcom-Add-EDMA-node-for-IPQ9574.patch`,
    `0345-arm64-dts-qcom-Add-IPQ9574-MDIO-device-node.patch`,
    `0346-arm64-dts-qcom-ipq9574-Use-usb-phy-for-node-names.patch`,
    `0347-arm64-dts-qcom-ipq9574-add-QPIC-SPI-NAND-default-par.patch`,
    `0348-arm64-dts-qcom-add-partition-table-for-ipq9574-rdp-c.patch`,
    `0349-arm64-dts-qcom-Add-IPQ9574-RDP433-port-node.patch`,
    `0350-arm64-dts-qcom-add-AQR-NVMEM-node-for-IPQ9574-RDP433.patch`,
    `0351-arm64-dts-qcom-Add-label-to-EDMA-port-for-IPQ9574-RD.patch`,
    `0353-arm64-dts-qcom-ipq9574-add-NSSNOC-clock-to-nss-node.patch`,
    `0355-arm64-dts-qcom-ipq9574-add-NSSNOC-interconnects-to-n.patch`,
    `0356-arm64-dts-qcom-ipq9574-describe-remaining-uniphy-resets.patch`,
    `0403-pwm-fix-period-calculation.patch`,
    `0407-arm64-dts-qcom-ipq9574-add-secure-WCSS-nodes.patch`,
    `0408-dt-bindings-net-ath11k-describe-IPQ9574.patch`,
    `0409-arm64-dts-qcom-ipq9574-add-ath11k-node.patch`.
  - `0349`–`0351` were rebased rather than dropped: 7.3 moved the shared
    IPQ9574 RDP433 nodes into `ipq9574-rdp433-common.dtsi`, which is also
    used by the eMMC variant.
  - `0403-pwm-fix-period-calculation.patch` was rebased onto the 7.3
    upstream `drivers/pwm/pwm-ipq.c`.
  - The remaining out-of-tree patches (PPE/EDMA, PCS/uniphy including
    `0314`/`0357`–`0362`, nsscc `0352`/`0354`, WCSS, ath11k/ath12k
    bindings `0440`, ...) carried over from the 6.18 set and apply
    unchanged.

- `target/linux/qualcommbe/config-7.3`
  - 105 new defaults appended: 35 `CONFIG_...=y` entries, 1
    `CONFIG_...=m` entry, 68 `# CONFIG_... is not set` entries and one
    explicit value; 11 stale symbols were removed or replaced.
  - The cpufreq drivers are intentionally left enabled - the OPP-table
    removal patch above is what prevents the lethal 936MHz switch.

## Feed packages that need patches

The following packages require patches to build against Linux 7.3 on qualcommbe:

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
