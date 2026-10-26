# ipq806x Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on ipq806x, and the patches used to make them work.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for ipq806x:

- `target/linux/ipq806x/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/ipq806x/patches-7.3`
  - 4 outdated backports removed as they are now upstream in 7.3:
    `001-01-v6.19-err.h-add-INIT_ERR_PTR-macro.patch`,
    `001-02-v6.19-soc-qcom-smem-better-track-SMEM-uninitialized-state.patch`,
    `002-v6.19-cpufreq-qcom-nvmem-add-compatible-fallback-for-ipq80.patch`,
    `903-net-stmmac-force-name-from-dt-alias.patch`.
  - 10 patches refreshed to apply cleanly on 7.3 against the generic
    backport/pending/hack set:
    `102-mtd-rootfs-conflicts-with-OpenWrt-auto-mounting.patch`,
    `107-10-ARM-dts-qcom-add-saw-for-l2-cache-and-kraitcc-for.patch`,
    `107-13-ARM-dts-qcom-add-opp-table-for-cpu-and-l2-for-ipq.patch`,
    `107-15-ARM-dts-qcom-add-multiple-missing-binding-for-cpu.patch`,
    `114-01-devfreq-qcom-Add-L2-Krait-Cache-devfreq-scaling-driv.patch`,
    `115-01-devfreq-add-ipq806x-fabric-scaling-driver.patch`,
    `850-soc-add-qualcomm-syscon.patch`,
    `900-arm-add-cmdline-override.patch`,
    `901-02-ARM-decompressor-add-option-to-ignore-MEM-ATAGs.patch`,
    `902-ARM-decompressor-support-for-ATAGs-rootblock-parsing.patch`.
  - `107-13` and `107-15` rebuilt around the files that upstream dropped
    from the tree together with the removal of the remaining ipq806x
    boards. The 6.18 versions modified pre-existing dtsi files; on 7.3 the
    files no longer exist, so the sections became `/dev/null` creation
    hunks with the same content as the 6.18 patched result:
    - `107-13` creates `arch/arm/boot/dts/qcom/qcom-ipq8065.dtsi` and
      `arch/arm/boot/dts/qcom/qcom-ipq8062.dtsi` (with the cpu/l2 opp
      table overrides for IPQ8065 and IPQ8062).
    - `107-15` creates `arch/arm/boot/dts/qcom/qcom-ipq8064-smb208.dtsi`,
      `arch/arm/boot/dts/qcom/qcom-ipq8064-v2.0-smb208.dtsi`,
      `arch/arm/boot/dts/qcom/qcom-ipq8062-smb208.dtsi` and
      `arch/arm/boot/dts/qcom/qcom-ipq8065-smb208.dtsi`, including the
      smb208 regulators plus the cpu0/cpu1/l2 supply references. Without
      these the device trees of 27 boards fail to preprocess with
      `qcom-ipq8064-v2.0-smb208.dtsi: No such file or directory`.
  - The devfreq patches `114-01`/`115-01` drop the removed internal
    `devfreq` `governor.h` include.
- `target/linux/ipq806x/config-7.3`
  - 53 new defaults appended: `CONFIG_SCHED_CACHE=y`, `CONFIG_QCOM_SOC=y`
    and 51 `# CONFIG_... is not set` entries for symbols that are new in
    7.3, including explicit off for the qcom mass-strength symbols
    `CONFIG_HW_RANDOM_QCOM`, `CONFIG_POWER_SEQUENCING_QCOM_WCN`,
    `CONFIG_GUNYAH_WATCHDOG`, `CONFIG_QCOM_SPMI_ADC5_GEN3`.
- `package/kernel/linux/modules/crypto.mk`
  - `kmod-crypto-ghash` `FILES`/`AUTOLOAD` updated for the Linux 7.3
    module removal:
    `crypto/ghash-generic.ko@lt7.3`, so nothing is packaged on 7.3
    (the module fold into the crypto core).

## Feed packages that need patches

The following packages require patches to build against Linux 7.3 on ipq806x:

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
