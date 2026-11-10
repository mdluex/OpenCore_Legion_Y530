# OpenCore for Lenovo Legion Y530-15ICH (macOS Sequoia)

This repository is the sanitized source tree of a **working OpenCore 1.0.8 EFI** that is already booting **macOS Sequoia 15.x** on a Lenovo Legion Y530-15ICH. It is no longer a Monterey / Big Sur / Ventura install guide.

The two updates applied on top of that proven EFI:

1. Ethernet kext `RealtekRTL8111.kext` updated from 2.4.2 to **3.0.0** (official [Mieze / RTL8111_driver_for_OS_X](https://github.com/Mieze/RTL8111_driver_for_OS_X) v3.0.0 release).
2. Boot argument **`-wegnoegpu`** added, so WhateverGreen also keeps the GTX 1050 Ti off. `SSDT-NoHybGfx` was already doing this.

`config.plist` was checked with Acidanthera's **ocvalidate 1.0.8** (no issues) and parsed as valid XML.

> **USB-test first.** Do not copy this EFI over the laptop's internal ESP until it has been tested from a USB stick and Sequoia boots cleanly (display, keyboard, trackpad, Ethernet, Wi-Fi, audio). Keep a backup of the current ESP. This repo does not include Windows `Microsoft\` boot files; do not format the EFI partition or you can break Windows dual-boot.

## Hardware (this EFI)

| Item | This machine |
| --- | --- |
| Chassis | Lenovo Legion Y530-15ICH |
| CPU | 6-core Intel Core i7 (Coffee Lake) |
| Memory | 24 GB DDR4 |
| iGPU | Intel UHD 630 (`AAPL,ig-platform-id` `00009B3E`) |
| dGPU | NVIDIA GTX 1050 Ti — disabled under macOS (`SSDT-NoHybGfx` + `-wegnoegpu`). No macOS acceleration, and HDMI on this chassis is wired to the dGPU, so HDMI is expected to stay dead. |
| Audio | Realtek ALC236, AppleALC layout-id **18** |
| Ethernet | Realtek RTL8168 / RTL8111 (`RealtekRTL8111.kext` 3.0.0) |
| Internal Wi-Fi | Intel, via **itlwm** 2.2.0 (`AirportItlwm` is on disk but disabled so the two do not load together) |
| USB Wi-Fi | Realtek RTL8188EUS (`0bda:8179`) via **RtWlanU** 1830.32.b27 and **RtWlanU1827** 1827.4.b36 (chris1111 Wireless USB adapter pack) |
| Bluetooth | Built-in Realtek (`0bda:b023`). BlueToolFixup + BrcmFirmwareData + BrcmPatchRAM3 are enabled in this working config. |
| SMBIOS model | **MacBookPro15,1** (2018 15-inch MacBook Pro) |

The exact CPU stepping, BIOS version, SSD model, and trackpad ID are not claimed here.

## What works on Sequoia (and what this tree does not claim)

This EFI is the one already used to run Sequoia on this laptop. In that working setup:

- The laptop boots Sequoia with the internal UHD 630 display.
- The GTX 1050 Ti is held off.
- Ethernet, USB Wi-Fi (RTL8188EUS), and internal Intel Wi-Fi (itlwm) are injected as listed above.
- ALC236 is set to layout-id 18.
- OpenCore has a Windows picker entry on the live machine (the machine-specific disk path was removed from this repo; see below).
- SIP is **on** (`csr-active-config` is all zeros). `SecureBootModel` is **Disabled** (leave it unless you USB-test a change). ScanPolicy is locked down to APFS/HFS on SATA, NVMe, and USB (not "scan everything").

Not claimed, and not re-tested in the environment that prepared this tree:

- Headphone jack / microphone quality (an older `ALCPlugFix` / `AudioFix.sh` helper is still in the repo if you need it; it has not been re-verified on Sequoia here).
- iMessage / FaceTime / iCloud (these depend on **your** unique SMBIOS values, not the placeholders in git).
- Camera capture, every Bluetooth accessory, and sleep/wake edge cases.
- Official Apple software update reliability.

The GTX 1050 Ti cannot get modern Metal in macOS. That is an architectural limit, not something this EFI can fix.

## SMBIOS identifiers were removed from this repo on purpose

`config.plist` in git does **not** contain a real `SystemSerialNumber`, `MLB`, `SystemUUID`, or `ROM`. Those were replaced with obvious placeholders:

| Key | Placeholder in this repo |
| --- | --- |
| `SystemProductName` | `MacBookPro15,1` (keep this) |
| `SystemSerialNumber` | `REPLACE_WITH_YOUR_SERIAL` |
| `MLB` | `REPLACE_WITH_YOUR_MLB` |
| `SystemUUID` | `00000000-0000-0000-0000-000000000000` |
| `ROM` | six zero bytes |

A machine-specific Windows boot path (it included a disk/partition UUID) was also removed. The Windows 11 picker entry is present but **disabled**, with `Path` set to `REPLACE_WITH_YOUR_WINDOWS_BOOT_PATH`. If you dual-boot, point that entry at your own `EFI\Microsoft\Boot\bootmgfw.efi` (or the bootmgfw variant you already use) and enable it. Do not delete the `Microsoft` folder from the laptop's ESP.

### How to generate your own identifiers

1. Use [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS) (corpnewt).
2. Generate a set for model **MacBookPro15,1**.
3. Copy the generated values into `PlatformInfo → Generic`:
   - `SystemSerialNumber`
   - `MLB` (Board Serial)
   - `SystemUUID`
4. Set `ROM` to the MAC address of your Ethernet interface (en0), 6 bytes, or to 6 random bytes if you do not want to use the NIC MAC.
5. Check the serial on [Apple's Check Coverage](https://checkcoverage.apple.com/) page. You want a result of **invalid / not found**, not a real Mac that already exists.
6. **If you are migrating an already-working install** (this laptop already runs Sequoia): copy the SMBIOS values from your current live `config.plist` into this tree instead of generating new ones. Changing serial / MLB / UUID / ROM on an installed system will drop iCloud and iMessage until you sign in again, and can cause "this Mac is already associated with another Apple ID" problems. Keep the same identifiers.

Never commit real serials, MLB, UUID, or ROM back to git.

## OpenCore, boot-args, and kexts

- **OpenCore 1.0.8** (RELEASE), with matching `OpenRuntime`, `OpenCanopy`, `AudioDxe`, `HfsPlus`, `ExFatDxe`, and `ResetNvramEntry` (the Reset NVRAM driver is on disk; it is not enabled in `UEFI → Drivers` in this working config).
- **boot-args:** `keepsyms=1 -lilubetaall -wegnoegpu`
- **SIP:** on
- **SMBIOS:** MacBookPro15,1

Enabled kexts and the versions actually in this tree (comments inside `config.plist` may still show older numbers; trust the kext `Info.plist`):

| Kext | Version | Role |
| --- | --- | --- |
| Lilu | 1.7.2 | Patch engine |
| VirtualSMC | 1.3.8 | SMC |
| SMCBatteryManager | 1.3.8 | Battery |
| SMCProcessor | 1.3.8 | CPU thermal |
| WhateverGreen | 1.7.1 | UHD 630 + dGPU off |
| AppleALC | 1.9.8 | ALC236, layout-id 18 |
| RealtekRTL8111 | **3.0.0** | Ethernet |
| itlwm | 2.2.0 | Internal Intel Wi-Fi (Heliport-style) |
| RtWlanU | 1830.32.b27 | USB RTL8188EUS |
| RtWlanU1827 | 1827.4.b36 | USB Realtek companion |
| AirportBrcmFixup | 2.1.8 | Present and enabled (Broadcom injector only; the Catalina injector is off) |
| BlueToolFixup | 2.7.2 | Bluetooth (macOS 12+) |
| BrcmFirmwareData | 2.7.2 | Bluetooth firmware store |
| BrcmPatchRAM3 | 2.7.2 | Bluetooth firmware upload |
| CpuTscSync | 1.1.2 | TSC on wake |
| NVMeFix | 1.1.3 | NVMe power management |
| BrightnessKeys | 1.0.3 | Brightness keys |
| VoodooI2C | 2.8 | I2C trackpad controller |
| VoodooI2CHID | 1.0 | I2C HID satellite |
| VoodooPS2Controller + Keyboard | 2.3.7 | PS/2 keyboard (mouse/trackpad plugins off) |
| USBPorts | 1.0 | USB port map |

On disk but **not** enabled: `AirportItlwm` (do not enable together with `itlwm`), unused Broadcom / USBToolBox / Intel Bluetooth / extra VirtualSMC plugin kexts. Leave them alone unless you know you need one.

ACPI is unchanged from the working tree: `SSDT-EC-USBX-LAPTOP`, `SSDT-GPRW`, `SSDT-NoHybGfx`, `SSDT-NumLock`, `SSDT-PLUG`, `SSDT-PNLF`, `SSDT-SBUS-MCHC`, `SSDT-TPD0`, plus the GPRW → XPRW rename patch.

## BIOS (same chassis notes as the original guide)

These BIOS options come from the original Legion Y530 OpenCore guide. Confirm them if you are installing or if something stopped booting. Exact menu names can vary slightly by BIOS revision.

- Boot Mode: UEFI
- Storage Mode: AHCI
- Secure Boot: Disabled
- To reach the Advanced menu: `Fn + D + O`, reboot, then `F2` when the blue box appears
- Kernel Debug Serial Port: Legacy UART
- Force unlock on all GPIO pads: Enabled (needed for the trackpad)
- CFG Lock (MSR E2): Disabled
- DVMT Pre-Allocated Memory: 64 MB

## Install or update (USB first)

1. Back up the current EFI System Partition (it may also contain a `Microsoft` folder for Windows).
2. Build a USB installer or a USB with only an EFI partition, following [Dortania's installer guide](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/) if you need a full installer.
3. Copy this repo's `EFI` folder to the USB ESP.
4. Fill in **your** SMBIOS values (see above) on the **USB copy only**. If Sequoia is already installed, copy the identifiers from the live config, do not generate new ones.
5. Re-add a Windows picker entry if you need it, or use the firmware boot menu for Windows.
6. Boot the USB from the firmware boot picker, then boot Sequoia. Confirm display, input, Ethernet, Wi-Fi, and audio.
7. Only then copy the tested EFI onto the internal ESP. Do not format the ESP.

Ethernet is the safe network path during an install. USB Wi-Fi already works on this Sequoia EFI, but do not depend on it for the installer if something goes wrong.

If the trackpad buttons misbehave, the older guide suggested unchecking "Force Click and haptic feedback" in Trackpad settings.

For iMessage / iCloud, follow [Dortania: Fixing iServices](https://dortania.github.io/OpenCore-Post-Install/universal/iservices.html) after your own unique SMBIOS values are in place.

## Windows dual-boot

This laptop's live ESP also holds Microsoft boot files. They are **not** in this git tree (and must not be deleted from the disk). OpenCore on the live machine already had a Windows 11 picker entry; that path is machine-specific and was stripped from the repo. Use the firmware boot menu, or add your own entry, if you want Windows from the OpenCore picker.

## Credits

- The working Sequoia configuration on this Y530-15ICH
- The original Legion Y530 guide: [Hamza](https://github.com/chilledHamza)
- [Acidanthera](https://github.com/acidanthera) (OpenCore, Lilu, WhateverGreen, AppleALC, VirtualSMC, and others)
- [Mieze](https://github.com/Mieze) (RealtekRTL8111)
- [OpenIntelWireless](https://github.com/OpenIntelWireless) (itlwm)
- [chris1111](https://github.com/chris1111) (Wireless USB / RtWlanU)
- [VoodooI2C](https://github.com/VoodooI2C/VoodooI2C) authors
