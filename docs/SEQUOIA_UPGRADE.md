# Sonoma 14.3 → Sequoia 15.8.2 (in place) + Xcode 26.3

Do **not** erase the disk. Do **not** replace the internal EFI until a USB copy of this tree boots Sonoma and then the Sequoia installer.

Current OS on this laptop: **macOS Sonoma 14.3**. Target: **Sequoia 15.8.2**, then **Xcode 26.3** from Apple Developer downloads (not the App Store).

## Why this OS and this Xcode

- App Store Connect **since 28 Apr 2026** requires uploads built with **Xcode 26+** and an **iOS 26 SDK** ([Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/?id=04282026a)).
- [Xcode 26.3](https://developer.apple.com/xcode/system-requirements/) supports **macOS Sequoia 15.6 – Tahoe 26.x** and includes **iOS 26.2**. Sequoia 15.8.2 satisfies the 15.6 floor.
- Mac App Store Xcode on 2026-11-08 is **Xcode 27.x**, which needs **Tahoe 26.6+**. Installing that on Sequoia will fail. Download **Xcode 26.3** from [developer.apple.com/download/all](https://developer.apple.com/download/all/) (sign in, search “Xcode 26.3”). Prefer the **Universal** `.xip` on this Intel laptop.

## 1. Backup the working EFI (required)

From the current Sonoma install, copy the **internal EFI partition** to a USB stick labeled `EFI-BACKUP`. That stick is the only rollback if the new OpenCore build misbehaves.

Keep a second empty USB (`EFI-TEST`) for this repo’s `EFI` folder.

## 2. Preserve local SMBIOS identity

Committed `EFI/OC/config.plist` uses placeholders (`REPLACE_WITH_GENSMBIOS_SERIAL`, `REPLACE_WITH_GENSMBIOS_MLB`, zero UUID, dummy ROM). Those must stay in git.

On the USB **test** copy only, paste your **existing** `PlatformInfo → Generic` values from the backup EFI:

- `SystemSerialNumber`
- `MLB`
- `SystemUUID`
- `ROM`
- keep `SystemProductName` = `MacBookPro15,1` (USBPorts is bound to that model)

Do not type serials into this repository, issues, or screenshots.

## 3. USB-test this EFI before touching the internal ESP

1. Copy this repo’s `EFI` onto `EFI-TEST` (after step 2).
2. Reboot, `F12`, boot that USB.
3. Reset NVRAM once from the OpenCore picker.
4. Confirm Sonoma 14.3 still reaches the desktop: internal 1920×1080, UHD 630 not 7 MB VRAM, Ethernet `en0`, no NVIDIA.

If it fails, boot `EFI-BACKUP` and stop.

## 4. In-place Sequoia 15.8.2

Use **Ethernet**. USB Wi-Fi `0bda:8179` is **not** promised on Sequoia (SIP-on EFI, no `RtWlanU`).

1. Leave the working disk intact (no format, no “Erase Macintosh HD”).
2. Install **macOS Sequoia 15.8.2** with System Settings → Software Update **or** a Sequoia 15.8.2 USB installer. Do not pick Tahoe or Golden Gate recovery.
3. After the first Sequoia reboot, if you used `EFI-TEST`, copy that same EFI (with your local SMBIOS) to the **internal** ESP only after a successful USB boot of Sequoia. Reset NVRAM once.
4. Keep `EFI-BACKUP` forever.

## 5. Install Xcode 26.3 (not 27)

1. On Sequoia, open [More Downloads](https://developer.apple.com/download/all/).
2. Download **Xcode 26.3** (and matching Command Line Tools 26.3 if you want them).
3. Open the `.xip`, drag Xcode into `/Applications`.
4. Confirm: Xcode → Settings → Platforms shows an **iOS 26.x** SDK. `xcodebuild -version` should report 26.3, not 27.

Do not let the App Store replace it with Xcode 27.

## 6. After-upgrade checklist (vs Sonoma 14.3 baseline)

1. Picker + Reset NVRAM.
2. Display: 1920×1080 online; UHD 630 Device ID `0x3e9b`; VRAM ≫ 7 MB; Metal listed; no NVIDIA.
3. HDMI expected dark (GTX 1050 Ti stays off).
4. Ethernet `en0` / `RealtekRTL8111` used for downloads.
5. Built-in Input/Output still enumerated (2 ch / 44100). Photos never proved playback.
6. Camera UVC `04ca:7070` still listed; capture untested.
7. Bluetooth may show THIRD_PARTY_DONGLE; do not enable Broadcom kexts because VendorID `0x004c` is spoofed; pairing unproven.
8. USB Wi-Fi: treat as **unknown** until you decide (yourself) whether to install chris1111 with the SIP/Gatekeeper tradeoffs. This EFI will not do that.
9. Ignore **Upgradeable Memory: No**. Physical RAM is 16 GB + 8 GB.
10. `csrutil status` enabled; About This Mac still the same spoofed 15-inch 2018 model.

## Rollback

Boot `EFI-BACKUP`. The Sequoia volume can stay; you are rolling back **bootloader**, not necessarily the OS. A full OS rollback needs a Time Machine / clone you made **before** step 4.
