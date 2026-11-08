# Two OpenCore profiles

OpenCore only loads `EFI/OC/config.plist`. This repo ships two validated plists.

| File | macOS target | Role |
| --- | --- | --- |
| `EFI/OC/config.plist` | Sequoia 15.8.2 | Conservative fallback. SIP on, Apple Secure Boot `Default`, AppleALC analog audio. |
| `EFI/OC/config-tahoe-26.plist` | Tahoe 26.7.2 | Newest Intel macOS this laptop can actually boot. Copy over `config.plist` on a **USB EFI** to use. |

Golden Gate 27 has **no Intel kernel**. There is no third profile for it.

## How to switch (USB only)

1. Keep a USB copy of the working Sequoia `EFI` as rollback.
2. On a second USB, copy this repo `EFI`, then:

```bash
cp EFI/OC/config.plist EFI/OC/config-sequoia.plist.bak
cp EFI/OC/config-tahoe-26.plist EFI/OC/config.plist
```

3. Boot that USB with `F12`. Reset NVRAM once. Do not format disks.

To go back, boot the Sequoia USB and restore its `EFI`.

## What Tahoe changes vs Sequoia (and what it does not)

| Item | Sequoia fallback | Tahoe 26 profile |
| --- | --- | --- |
| SIP `csr-active-config` | `00000000` (on) | `00000000` (on) |
| AppleALC | enabled | **disabled** (AppleHDA removed in 26) |
| WhateverGreen / UHD 630 | enabled | enabled |
| GTX 1050 Ti | off (`SSDT-NoHybGfx` + `-wegnoegpu`) | same |
| Broadcom / Intel Wi-Fi kexts | disabled | disabled |
| `SecureBootModel` | `Default` | **`Disabled`** (needed for installer/OTA on a dropped SMBIOS; documented, not silent) |
| Extra boot-args | none | `-no_compat_check` `revpatch=sbvmm` |
| Root patches / OCLP | none | none |

`revpatch=sbvmm` is RestrictEvents **model spoofing** (pretend VMM so the installer accepts `MacBookPro15,1`). It is not a root volume patch and does not turn SIP off. [Dortania Tahoe OTA](https://dortania.github.io/OpenCore-Install-Guide/extras/tahoe.html) also requires `SecureBootModel=Disabled` for that path.

## Why people say “latest works on OpenCore”

They are almost always running **Tahoe 26**, the last x86_64 macOS, with SMBIOS spoofing. That is solvable. **Golden Gate 27** is ARM-only on Apple’s list ([support.apple.com/en-us/127255](https://support.apple.com/en-us/127255), 5 Nov 2026). Spoofing `MacBookPro16,1` cannot add an Apple silicon kernel.
