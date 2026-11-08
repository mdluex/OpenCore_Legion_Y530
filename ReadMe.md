# OpenCore for Lenovo Legion Y530-15ICH

Two OpenCore 1.0.8 profiles for this laptop’s **Intel UHD 630** (GTX 1050 Ti stays off):

| Profile | File | macOS |
| --- | --- | --- |
| Conservative fallback (default `config.plist`) | `EFI/OC/config.plist` | **Sequoia 15.8.2** — SIP on, AppleALC, Apple Secure Boot Default |
| Newest Intel macOS | `EFI/OC/config-tahoe-26.plist` | **Tahoe 26.7.2** — last x86_64 macOS. Copy over `config.plist` on a USB to use. See `docs/PROFILES.md`. |

**Golden Gate 27.2 is not possible.** Apple’s list is Apple silicon only ([support 127255](https://support.apple.com/en-us/127255), 5 Nov 2026). OpenCore cannot boot an OS that has no Intel kernel.

This repo cannot boot the physical laptop. Checks here are static (`ocvalidate` 1.0.8 + `scripts/verify_efi.py`). Always test from a USB EFI.

## Why “people run the newest with OpenCore” is not Golden Gate

Hard architectural limits (spoofing a different Mac model does **not** fix these):

- **Golden Gate 27** — no x86_64 build. Last Intel release is Tahoe 26.
- **GTX 1050 Ti (Pascal)** — no Metal drivers after High Sierra. It stays powered down (`SSDT-NoHybGfx` + `-wegnoegpu`). HDMI on this chassis is typically wired to that GPU, so HDMI-out is expected dead.
- **USB Wi-Fi `0bda:8179` (RTL8188EUS)** — no Apple/Acidanthera kext. chris1111 `RtWlanU` is the matching closed Realtek blob; **not vendored**. Tahoe 26.7.2 runtime is **unverified**.

Solvable with OpenCore / kexts (what those “Tahoe on OpenCore” builds actually do):

- Apple dropped `MacBookPro15,1` from the Tahoe **support list**. The Intel UHD 630 kexts are still in macOS 26 (2019 16-inch MBP still has UHD 630). Community Coffee Lake + UHD 630 Tahoe boots exist. This tree keeps `MacBookPro15,1` so `USBPorts.kext` still matches, and the Tahoe profile adds `-no_compat_check` plus RestrictEvents `revpatch=sbvmm` (VMM spoof for the installer, [Dortania](https://dortania.github.io/OpenCore-Install-Guide/extras/tahoe.html)). That is **not** a root patch.
- Analog audio: AppleHDA was removed in 26, so AppleALC cannot work. Sequoia keeps AppleALC. Tahoe leaves SIP on and ALC **off**; use USB audio or a later opt-in you apply yourself (`extras/tahoe-audio/`).

## Newest verified versions (2026-11-08)

| Release | Apple current | This laptop |
| --- | --- | --- |
| macOS 27 Golden Gate **27.2** | [109033](https://support.apple.com/en-us/109033), [127255](https://support.apple.com/en-us/127255) | Impossible (Apple silicon only) |
| macOS Tahoe **26.7.2** | [109033](https://support.apple.com/en-us/109033), [122867](https://support.apple.com/en-us/122867) | **Newest Intel OS.** Profile: `config-tahoe-26.plist`. Costs below. |
| macOS Sequoia **15.8.2** | [109033](https://support.apple.com/en-us/109033), [120282](https://support.apple.com/en-us/120282) | **Fallback.** Native AppleALC, `SecureBootModel Default`, 2018 15-inch MBP still listed. |

WhateverGreen 1.7.1 includes macOS 26 constants. Coffee Lake UHD 630 acceleration on Tahoe is reported in the wild without OCLP (iGPU path; AMD WEG panics on Tahoe are a different problem).

## Hardware (verified vs leftover)

**Confirmed for this owner (About This Mac / System Information, 2026-11-08):**

- Legion Y530-15ICH, NVIDIA GTX 1050 Ti kept off, **Intel UHD Graphics 630 1536 MB** for the panel
- **24 GB 2400 MHz DDR4**
- **2.2 GHz 6-core Intel Core i7** — About This Mac does **not** show a SKU; this PR does **not** assert i7-8750H
- Current OS: **macOS Sonoma 14.3** (spoofed as MacBook Pro 15-inch 2018 / `MacBookPro15,1`)
- Daily Wi-Fi: USB **Vendor `0x0bda` Product `0x8179`** Realtek 802.11n, USB 480 Mb/s → USB ID Repository **RTL8188EUS**; chris1111 V17 personality `RTL8188EU_8179`
- Separate **Bluetooth Radio** VID `0x0bda` PID `0xb023` Realtek Built-in Yes (USB ID Repository: RTL8822BE BT adapter). Does **not** prove PCI Wi-Fi or that BT works
- Internal Wi-Fi **unknown and unused**. Serial numbers are private and not stored in this repo.

**From the original tree only (Hamza; not re-verified from this About screen):** ALC236 / RTL8168H / ELAN061B / BIOS 8JCN56WW. That tree also wrote i7-8750H; Y530-15ICH also shipped as i5-8300H. BCM94352Z was the *previous* README card — **not assumed here**. Broadcom and Intel Wi-Fi kexts are **disabled** in both profiles.

## Tahoe functional costs (if you switch the profile)

| Area | Sequoia fallback | Tahoe 26 profile |
| --- | --- | --- |
| Display | UHD 630 + WEG (1536 MB already on Sonoma 14.3) | Same goal; Tahoe QE/CI still untested on this chassis |
| Speakers / 3.5 mm | AppleALC layout 18 | Silent unless USB audio or a SIP-lowering VoodooHDA you add later |
| Ethernet | RTL8111 3.0.0 | Same |
| USB Wi-Fi | `0bda:8179` — **no kext in this EFI**; chris1111 `RtWlanU` is owner-installed if needed | Same kext policy; **Tahoe 26.7.2 unverified** (OCLP-Mod/AMFI not applied) |
| Internal Wi-Fi | Disabled / unused | Same |
| SIP | On | On (`csr-active-config` zeros) |
| Apple Secure Boot | `Default` | **`Disabled`** (required for this dropped SMBIOS installer/OTA path; documented) |
| Extra boot-args | — | `-no_compat_check` `revpatch=sbvmm` |
| OCLP / AMFI / root patches | None | None |
| Point updates | Sequoia OTAs | `BlacklistAppleUpdate` stays true so Golden Gate is not offered via sbvmm; install Tahoe 26.x updates from USB |

Maintenance: every Tahoe point release may need a USB installer. WhateverGreen must stay enabled for the iGPU; if a Tahoe *installer* blacks out, boot a USB with `-igfxvesa` only for that session — do not leave VESA as the daily config.

## USB Wi-Fi (`0bda:8179`)

Mapped and documented; **not injected**.

- USB ID Repository: **RTL8188EUS**. chris1111 V17 `RtWlanU.kext` personality **`RTL8188EU_8179`** (`idVendor` `0x0bda`, `idProduct` `0x8179`). Same PID, family vs USB-variant names.
- Maintained *installer* (closed Realtek blob, no source): [Wireless-USB-OC-Big-Sur-Adapter V17](https://github.com/chris1111/Wireless-USB-OC-Big-Sur-Adapter/releases/tag/V17). **Not vendored** here.
- Sequoia: chris1111 wants Gatekeeper off; default path wants SIP fully off. This EFI keeps SIP on.
- Tahoe 26.7.2: chris1111’s Tahoe doc needs OCLP-Mod + `AMFIPass`/`amfi=0x80`. **Unverified on this stick; not applied.**

Details and SIP caveats: `extras/usb-wifi/README.md`. OS installs/updates: **Ethernet**.

## Graphics

Internal LCD = Intel UHD 630. Preserved framebuffer (not generic Dortania `0900A53E`):

- `AAPL,ig-platform-id` = `00009B3E`
- `con1` / `con2` disabled, `framebuffer-portcount` = 1

Pascal dGPU remains off. Do not enable it to chase HDMI.

## Backup / rollback / BIOS

No format, no firmware flash.

1. Copy your **current working EFI** to a USB first.
2. Test this repo on another USB (`F12`). For Tahoe, copy `config-tahoe-26.plist` → `config.plist` on that USB only.
3. Reset NVRAM from the picker after a swap.
4. If it fails, boot the backup USB and restore.

Original Advanced menu (confirm): `Fn+D+O`, reboot, `F2`. UEFI boot, AHCI, firmware Secure Boot off, CFG Lock off, DVMT 64 MB, GPIO pads unlocked. If CFG Lock cannot be disabled, set `AppleXcpmCfgLock` true. `ControlMsrE2.efi` is for **reading** MSR 0xE2 only.

## SMBIOS

Both profiles: `MacBookPro15,1` with `REPLACE_WITH_GENSMBIOS_*` placeholders. Generate identity locally. `USBPorts.kext` is bound to that model (now also has Tahoe `usb-port-number` keys). Do not change SMBIOS without remapping USB.

## Audio / input / USB

| Device | Sequoia | Tahoe |
| --- | --- | --- |
| ALC236 | layout-id 18; `AudioFix.sh` from this clone | Not via AppleALC; USB audio or later opt-in |
| Trackpad | VoodooI2C 2.9.1; uncheck Force Click | Same |
| USB map | `USBPorts.kext` CNL `0xa36d8086` | Same file; extra `usb-port-number` |

## Upgrade path

- Stay on Sequoia: replace EFI from USB, Reset NVRAM, install 15.8.2, take Sequoia security updates only.
- Move to Tahoe: USB-test `config-tahoe-26.plist`, backup, install 26.7.2 from a USB installer (not Golden Gate recovery). Keep the Sequoia EFI USB forever.

## Hardware checklist (USB boot)

1. Picker appears; Reset NVRAM.
2. Internal panel + brightness; About This Mac shows UHD 630 ≫ 7 MB VRAM; no NVIDIA.
3. HDMI expected dark.
4. Ethernet download.
5. USB Wi-Fi: already in use on Sonoma 14.3; Sequoia/Tahoe still need Ethernet until the owner re-applies chris1111 themselves. Tahoe wireless is unverified.
6. Trackpad, keyboard, battery, sleep/wake, USB-A/C, webcam.
7. Speakers: Sequoia yes / Tahoe expected silent without USB audio.

## Validation (static)

```bash
./tools/ocvalidate.linux EFI/OC/config.plist
./tools/ocvalidate.linux EFI/OC/config-tahoe-26.plist
python3 scripts/verify_efi.py
```

## Credits

Hamza (original Y530 tree), Acidanthera, VoodooI2C, Mieze, RehabMan, xiaoM, Dortania.
