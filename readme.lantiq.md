# lantiq Linux 7.3 build notes

This file documents the out-of-tree packages that do not build against
Linux 7.3 on lantiq, and the patches used to make them work.
**Compile-tested subtargets (`CONFIG_TESTING_KERNEL=y`; seed config used):**
- `ase` — `knowngood.config`.
- `xrx200` — `knowngood2.config`.
- `xrx200_legacy` — `knowngood3.config`.
- `xway` — `knowngood4.config`.
- `xway_legacy` — `knowngood5.config`.
- `falcon` — `knowngood6.config`.

## Kernel and target prerequisites

The following target changes were made to enable a Linux 7.3 build for lantiq:

- `package/kernel/lantiq/ltq-adsl` and `package/kernel/lantiq/ltq-atm`
  - Ported to 7.3: `strncpy` replaced with `strscpy` (`414-kernel-7.3-string-api.patch`)
    and the removed SVC-era ATM callbacks/fields dropped (`ltq_atm.c`). A full
    `make world` image build for the `ase` subtarget succeeds.

- `target/linux/lantiq/Makefile`
  - `KERNEL_TESTING_PATCHVER:=7.3` added to enable 7.3 kernel builds.
- `target/linux/lantiq/patches-7.3`
  - 8 patches refreshed to apply cleanly on 7.3 against the generic backport/pending/hack set:
    `001-MIPS-lantiq-add-pcie-driver.patch`,
    `004-MIPS-lantiq-add-atm-hack.patch`,
    `031-I2C-MIPS-lantiq-add-FALC-ON-i2c-bus-master.patch`,
    `035-owrt-lantiq-wifi-and-ethernet-eeprom-handling.patch`,
    `101-find_active_root.patch`,
    `152-lantiq-VPE.patch`,
    `200-MIPS-lantiq-xway-vmmc-use-platform_get_irq-to-get-ir.patch`,
    `302-mtd-cfi_cmdset_0001-Disable-write-buffer-functions-i.patch`.

- `target/linux/lantiq/config-7.3`
  - 36 new defaults appended to config-7.3 (unique `CONFIG_*` symbols added in 4/4).

## Feed packages that need patches

The following feed packages require patches to build against Linux 7.3 on lantiq:

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
