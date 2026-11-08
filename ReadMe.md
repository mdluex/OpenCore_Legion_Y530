# OpenCore for Lenovo Legion Y530-15ICH

OpenCore EFI for installing and running **macOS Sequoia 15.8.2** on a Lenovo Legion Y530-15ICH with a **GTX 1050 Ti**. This is the newest macOS that can realistically run with **Intel UHD 630 acceleration, AppleALC analog audio, and SIP left on**. Newer Apple releases are documented below instead of being pretended to work.

This repository cannot boot or test the physical laptop. Validation here is **static** (`ocvalidate` 1.0.8, file-reference checks, schema/mapping review). Confirm everything on hardware with a USB backup EFI before touching the internal ESP.

## Newest verified macOS compatibility (as of 2026-11-08)

Sources checked, not assumed:

| Release | Latest version (Apple) | This hardware |
| --- | --- | --- |
| macOS 27 Golden Gate | [27.2](https://support.apple.com/en-us/109033) (26 Oct 2026) | **Incompatible.** Apple silicon only. |
| macOS Tahoe 26 | [26.7.2](https://support.apple.com/en-us/109033) | **Not a default target.** Last Intel macOS, but Apple dropped 2018 15-inch MacBook Pro. Analog audio via AppleALC is broken because AppleHDA was removed. Would need experimental OCLP/VoodooHDA. See `docs/EXPERIMENTAL.md`. |
| **macOS Sequoia 15** | **[15.8.2](https://support.apple.com/en-us/109033)** | **Recommended.** [Apple Sequoia list](https://support.apple.com/en-us/120282) still includes MacBook Pro (15-inch, 2018) (`MacBookPro15,1`), which is this tree's SMBIOS and has UHD 630. |
| macOS Sonoma 14 | 14.8.9 | Supported fallback. |
| macOS Ventura 13 | 13.7.8 | Last convenient release if you need **native Broadcom Wi-Fi without OCLP**. |

**Do not upgrade to Tahoe 26 or Golden Gate 27 with this default EFI.** `BlacklistAppleUpdate` is enabled so Software Update does not offer those.

## Hardware evidence (verified vs assumed)

**Independently stated for this work:** Lenovo Legion Y530-15ICH, NVIDIA GTX 1050 Ti.

**Documented in this repository's previous README / EFI (original author Hamza; not re-verified on Mahmoud's machine):**

- Intel Core i7-8750H (Coffee Lake H) + Intel UHD Graphics 630
- 16 GB DDR4, HP EX950 2 TB NVMe
- Realtek ALC236, Realtek RTL8168H Ethernet
- Lenovo BCM94352Z (`FRU 04X6020`) replacing the stock WLAN card
- ELAN061B I2C precision trackpad (SYNA2B46 variant also existed; see extras)
- BIOS `8JCN56WW` (2020-11-30)

Y530-15ICH units were also sold with other CPUs (commonly i5-8300H) and GTX 1050 non-Ti. This EFI is built around the **Coffee Lake H + UHD 630 + GTX 1050 Ti + the USB/audio/trackpad mappings already in the tree**. Confirm your own CPU, WLAN, trackpad ID, and BIOS version before treating every kext as gospel.

**Not invented here:** no extra iGPU device-id spoof, no NVIDIA PCI path, no Intel Wi-Fi kext enabled.

## Graphics (read this)

The GTX 1050 Ti is **Pascal**. Apple never shipped Metal drivers for Pascal after High Sierra 10.13 web drivers. There is **no useful modern-macOS acceleration** on this dGPU, and this EFI does not install NVIDIA web drivers or OCLP root patches to fake it.

Default dGPU handling (keep both):

1. `ACPI/SSDT-NoHybGfx.aml` — ACPI power-off of the hybrid NVIDIA device on macOS (original hardware-specific SSDT).
2. boot-arg `-wegnoegpu` — WhateverGreen also ignores non-Intel GPUs.

**Outputs**

- Internal LCD is driven by **UHD 630**. Framebuffer from the previous working tree is **preserved**, not replaced with a generic Dortania laptop ID:
  - `AAPL,ig-platform-id` = `00009B3E`
  - unused connectors `con1` / `con2` indexed to `0xFFFFFFFF`
  - `framebuffer-portcount` = 1
- HDMI on this chassis is conventionally wired to the NVIDIA GPU. With the dGPU powered down, **HDMI-out is expected not to work**. Do not "fix" that by enabling the 1050 Ti on Sequoia.
- Dortania's current UHD 630 laptop ID is `0900A53E`. That is **not** applied by default because it would discard a known connector-disable mapping. Only try it if the internal display fails, and keep a USB rollback.

## What this EFI updates

- OpenCore **1.0.8** RELEASE (Acidanthera, 27 Sep 2026) plus matching `ocvalidate`
- Current stable Acidanthera / Mieze / VoodooI2C kexts (pinned in `docs/UPSTREAM_PINS.md`)
- OpenCore 1.0.8 schema (`HideVerbose` drivers, `ClearTaskSwitchBit`, `UEFI.Unload`, NVRAM `LegacySchema`, BlueToolFixup NVRAM vars)
- Hardware mappings kept: ACPI SSDTs, USBPorts.kext, ALC236 layout-id **18**, iGPU connector patch, `MacBookPro15,1`
- SMBIOS serial / MLB / UUID replaced with **local placeholders** (generate your own; do not commit them)
- Unused or OS-mismatched kexts moved out of the live EFI (`AirportItlwm`, Intel Bluetooth, USBToolBox map)

## Backup USB, rollback, and BIOS

No installer, format, or firmware flash is part of this repo.

1. On a spare FAT32 USB, copy **your current working `EFI` folder** first. That USB is the rollback.
2. Copy this repo's `EFI` onto another USB (or the same stick's second partition) and boot it via the firmware boot menu (`F12`).
3. Only after a successful USB boot, copy `EFI` onto the internal ESP. Do not format macOS or Windows volumes to do this.
4. If the internal copy fails to boot, `F12` back to the backup USB and restore the previous `EFI`.
5. After any EFI swap, use OpenCore picker **Reset NVRAM** (`ResetNvramEntry.efi`), then boot macOS once.

### BIOS assumptions (confirm; do not flash from this repo)

Original documented Advanced menu: `Fn+D+O`, reboot, then `F2`.

| Setting | Value | Why |
| --- | --- | --- |
| Boot Mode | UEFI | OpenCore |
| Storage | AHCI | NVMe/SATA |
| Secure Boot | Disabled | Third-party bootloader |
| CFG Lock | Disabled | `AppleXcpmCfgLock` is **false** in this config |
| DVMT Pre-Allocated | 64 MB | UHD 630 |
| Force unlock on all GPIO pads | Enabled | I2C trackpad |
| Kernel Debug Serial Port | Legacy UART | Original tree requirement |

If CFG Lock cannot be disabled, set `Kernel -> Quirks -> AppleXcpmCfgLock` to **true**. `ControlMsrE2.efi` is included as a hidden picker tool to **read** MSR 0xE2 status only. Do not use it to write firmware/MSR from this guide.

## SMBIOS / iServices (private)

`config.plist` ships:

- `SystemProductName`: `MacBookPro15,1` (15-inch Coffee Lake + UHD 630 analogue; still on Apple's Sequoia list)
- `SystemSerialNumber` / `MLB`: `REPLACE_WITH_GENSMBIOS_*`
- `SystemUUID`: zeros
- `ROM`: dummy `11:22:33:44:55:66`

Generate a unique **MacBookPro15,1** serial, MLB, ROM (from a real NIC MAC), and UUID locally with [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS) or OpenCore's `macserial`. Do not reuse sample serials, do not commit real ones, and do not log into iCloud until [Dortania iServices](https://dortania.github.io/OpenCore-Post-Install/universal/iservices.html) checks pass.

`USBPorts.kext` is bound to `MacBookPro15,1`. Changing SMBIOS model without remapping USB will break ports / Bluetooth.

## Networking, audio, input, USB

| Device | Default expectation |
| --- | --- |
| RTL8168H Ethernet | RealtekRTL8111 3.0.0 — primary network on Sequoia |
| BCM94352Z Wi-Fi | Native with AirportBrcmFixup through **Ventura**. Sonoma/Sequoia removed the legacy Broadcom stack; Wi-Fi on this card class needs **opt-in OCLP modern wireless** (SIP off, not default). |
| BCM Bluetooth | BlueToolFixup 2.7.2 + required NVRAM vars |
| Stock Intel CNVi (if still installed) | **Not enabled.** Confirm `ioreg`/`lspci` first, then see `extras/intel-wireless/` |
| ALC236 | layout-id **18** + `alc-verbs` / `alc-delay` preserved. Headphone fix: run `AudioFix.sh` from this clone (local files, no foreign curl). |
| ELAN061B trackpad | VoodooI2C 2.9.1 + HID satellite. Uncheck Force Click. If buttons regress, see `extras/legacy-voodooi2chid-elan061b/`. SYNA2B46: stock VoodooI2CHID as before. |
| USB | Existing `USBPorts.kext` (CNL XHCI `0xa36d8086`) kept. Alternate USBToolBox map is in extras, not loaded. |

## Supported upgrade path

Existing OpenCore installs on this tree (Big Sur / Monterey / Ventura / Sonoma) can move to **Sequoia 15.8.2** after replacing EFI from USB and resetting NVRAM. Stay on the same APFS volume; this repo never asks to wipe a disk.

- Create a full Time Machine or clone backup first.
- Download Sequoia 15.8.2 from Apple on a supported Mac, or use OpenCore `macrecovery` for the current Sequoia board-id. Do not recover Golden Gate/Tahoe.
- Install with `SecureBootModel` = `Default`. If the installer rejects the snapshot, set it to `Disabled` **for that install only**, then restore `Default`. Do not leave Apple Secure Boot off.
- After 15.8.2, apply Sequoia security updates only. Do not take a Tahoe/Golden Gate seed.

## Hardware test checklist (on the laptop)

Boot the **USB** copy first.

1. OpenCore picker (OpenCanopy) appears; Reset NVRAM once.
2. Internal display, brightness keys, backlight after sleep.
3. About This Mac: UHD 630 with more than 7 MB VRAM (QE/CI). No NVIDIA in GPU list.
4. HDMI: expected **no picture** while dGPU is off. Note the result; do not enable Pascal to chase it.
5. Ethernet link and a download.
6. Wi-Fi: likely absent on Sequoia without OCLP; Bluetooth pair a mouse if the BCM card is present.
7. Trackpad buttons + gestures; PS/2 keyboard including brightness.
8. Speakers, HDMI-unrelated analog headphone jack (run `AudioFix.sh` if needed).
9. Battery percentage, lid sleep, power-button sleep, wake, USB ports (USB-A, USB-C, webcam).
10. Confirm CFG Lock still disabled if XCPM fails (`AppleIntelInfo` / panic on boot).

## Validation in this PR (static only)

```bash
./tools/ocvalidate.linux EFI/OC/config.plist
python3 scripts/verify_efi.py
```

CI runs the same two commands. There is **no** remote boot of a Y530, no I/OKit dump, and no claim that sleep or Wi-Fi were proven on hardware.

## Credits

Hamza (original Y530 tree), Acidanthera, VoodooI2C, Mieze, RehabMan, xiaoM, and Dortania.
