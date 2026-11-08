# OpenCore Sequoia for Lenovo Legion Y530-15ICH (Xcode 26.3)

This tree is **Sequoia 15.8.2 only**. Goal: keep the laptop on the newest macOS that still runs **Xcode 26.3** so App Store Connect uploads remain possible, without Tahoe dropped-model bypasses or lowered SIP.

| Target | Why |
| --- | --- |
| macOS Sequoia **15.8.2** | 2018 15-inch MacBook Pro is still listed ([120282](https://support.apple.com/en-us/120282)). SIP on, AppleALC, `SecureBootModel Default`. |
| **Xcode 26.3** | [Apple Xcode support table](https://developer.apple.com/xcode/system-requirements/): 26.3 runs on **macOS Sequoia 15.6 through Tahoe 26.x** and ships the **iOS 26.2 SDK**. Sequoia 15.8.2 is in that range. |
| App Store uploads | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/?id=04282026a) **since 28 Apr 2026**: apps uploaded to App Store Connect must be built with **Xcode 26 or later** using an **iOS 26** (or matching 26) SDK. |

**Do not install Xcode 27 from the Mac App Store.** Xcode 27 / 27.1 / 27.2 require **macOS Tahoe 26.6 or later**. Get **Xcode 26.3** from [developer.apple.com/download/all](https://developer.apple.com/download/all/) (Apple Developer downloads), not the App Store latest.

This PR does **not** ship a Tahoe profile, `-no_compat_check`, `revpatch=sbvmm`, or `SecureBootModel Disabled`. Golden Gate 27 is Apple silicon only and is not a goal here.

Static checks: `ocvalidate` 1.0.8 + `scripts/verify_efi.py`. This environment cannot boot the laptop. Always USB-test EFI first. Guide: `docs/SEQUOIA_UPGRADE.md`.

## Hardware (owner System Information on Sonoma 14.3)

Transcribed; **no serials or MAC addresses**.

| Item | What Sonoma 14.3 reports | Not proven |
| --- | --- | --- |
| CPU | 2.2 GHz 6-core Intel Core i7 | Exact SKU (not asserted as i7-8750H) |
| RAM | **16 GB + 8 GB** DDR4, both 2400 MHz, Status OK | Dual 16 GB. **Upgradeable Memory: No** is spoofed SMBIOS |
| iGPU | UHD 630 Device ID **`0x3e9b`**, 1536 MB, **Metal 3**, internal **1920×1080** online, 24-bit ARGB8888 | Benchmarks |
| Audio | Built-in Input/Output enumerated, 2 ch 44100 Hz | Playback/mic; codec string |
| Ethernet | PCI **`10ec:8168`** `17aa:38b4` rev `0015` (RTL8168H/8111H); `com.insanelymac.RealtekRTL8111`; **en0**; max 1 Gb/s | Current link is 1 Gbps |
| USB Wi-Fi | `0bda:8179` Realtek 802.11n (in use on 14.3) | Sequoia wireless; see below |
| Bluetooth | State On, **THIRD_PARTY_DONGLE**, USB, reported VendorID **`0x004c`**; headphones **Not Connected**. USB tree **`0bda:b023`** | Apple/Broadcom silicon; pairing; PCI Wi-Fi |
| Camera | UVC **`04ca:7070`** | Capture |
| OS | Sonoma 14.3; spoofed MacBook Pro 15-inch 2018 | Real Mac |

**Preserved OpenCore maps:** `AAPL,ig-platform-id` `00009B3E`, GTX 1050 Ti off (`SSDT-NoHybGfx` + `-wegnoegpu`), `USBPorts.kext` CNL `0xa36d8086`, AppleALC layout-id 18, `RealtekRTL8111.kext`.

**Repo-original only (photos do not identify):** ALC236, ELAN061B, BIOS 8JCN56WW. Internal WLAN unknown/unused. BCM94352Z is not assumed. Broadcom and Intel Wi-Fi kexts stay **disabled**.

## USB Wi-Fi `0bda:8179` (RTL8188EUS) — not guaranteed

Identity is documented in `extras/usb-wifi/README.md`. There is **no** Apple or Acidanthera kext. chris1111 `RtWlanU` is a closed Realtek blob; **not vendored**, **not injected**. Sequoia compatibility is **unknown**. chris1111’s default installer wants SIP fully off and Gatekeeper off. This EFI **does not** lower SIP or AMFI and **does not** claim Wi-Fi after the upgrade.

Use **Ethernet** for the Sequoia installer and Xcode download.

## Security (this profile)

| Setting | Value |
| --- | --- |
| SIP `csr-active-config` | `00000000` (on) |
| `SecureBootModel` | `Default` |
| AppleALC | enabled |
| Tahoe bypass boot-args | **absent** |
| OCLP / AMFIPass / `amfi=0x80` | **absent** |
| `ToggleSipEntry.efi` | on disk, **disabled** |

## SMBIOS

Committed `config.plist` uses `REPLACE_WITH_GENSMBIOS_*` placeholders. Keep your **existing local identity** when installing this EFI (`docs/SEQUOIA_UPGRADE.md`). Do not commit real serials.

## Validation

```bash
./tools/ocvalidate.linux EFI/OC/config.plist
python3 scripts/verify_efi.py
```

## Credits

Hamza (original Y530 tree), Acidanthera, VoodooI2C, Mieze, RehabMan, xiaoM, Dortania.
