#!/usr/bin/env python3
"""Apply Legion Y530 hardware mappings onto an OpenCore 1.0.8-valid config.plist.

Does not invent SMBIOS identity. Writes obvious local placeholders only.
"""
from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "EFI/OC/config.plist"


def kext(
    bundle: str,
    comment: str,
    *,
    enabled: bool = True,
    executable: str | None = None,
    min_kernel: str = "",
    max_kernel: str = "",
) -> dict:
    name = bundle.split("/")[-1].removesuffix(".kext")
    if executable is None:
        executable = f"Contents/MacOS/{name}"
    return {
        "Arch": "x86_64",
        "BundlePath": bundle,
        "Comment": comment,
        "Enabled": enabled,
        "ExecutablePath": executable,
        "MaxKernel": max_kernel,
        "MinKernel": min_kernel,
        "PlistPath": "Contents/Info.plist",
    }


def driver(path: str, comment: str, *, enabled: bool = True, load_early: bool = False) -> dict:
    return {
        "Arguments": "",
        "Comment": comment,
        "Enabled": enabled,
        "HideVerbose": False,
        "LoadEarly": load_early,
        "Path": path,
    }


def tool(path: str, name: str, comment: str, *, enabled: bool = True, flavour: str = "Auto",
         full_nvram: bool = False, real_path: bool = False, text_mode: bool = False) -> dict:
    return {
        "Arguments": "",
        "Auxiliary": True,
        "Comment": comment,
        "Enabled": enabled,
        "Flavour": flavour,
        "FullNvramAccess": full_nvram,
        "Name": name,
        "Path": path,
        "RealPath": real_path,
        "TextMode": text_mode,
    }


def main() -> None:
    cfg = plistlib.loads(CONFIG.read_bytes())

    # OpenCore 1.0.8 schema additions. Preserve existing Booter quirk choices
    # (EnableWriteUnprotector=True / RebuildAppleMemoryMap=False is the OEM-laptop
    # MAT-missing combination this tree already used).
    cfg["Booter"]["Quirks"]["ClearTaskSwitchBit"] = False

    # Keep iGPU connector disables and ALC236 layout-id 18 exactly.
    # -wegnoegpu is added in boot-args; SSDT-NoHybGfx remains the ACPI dGPU off path.
    boot_args = "keepsyms=1 debug=0x100 -wegnoegpu"
    nvram_guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
    nvadd = cfg["NVRAM"]["Add"][nvram_guid]
    nvadd["boot-args"] = boot_args
    nvadd["ForceDisplayRotationInEFI"] = 0
    nvadd["csr-active-config"] = b"\x00\x00\x00\x00"  # SIP enabled
    # Required by BrcmPatchRAM 2.7.x BlueToolFixup on all macOS versions.
    nvadd["bluetoothExternalDongleFailed"] = b"\x00"
    nvadd["bluetoothInternalControllerInfo"] = bytes(14)

    cfg["NVRAM"]["Delete"][nvram_guid] = [
        "boot-args",
        "ForceDisplayRotationInEFI",
    ]
    cfg["NVRAM"]["LegacySchema"] = {
        "7C436110-AB2A-4BBB-A880-FE41995C9F82": [
            "EFILoginHiDPI",
            "EFIBluetoothDelay",
            "LocationServicesEnabled",
            "SystemAudioVolume",
            "SystemAudioVolumeDB",
            "SystemAudioVolumeSaved",
            "bluetoothActiveControllerInfo",
            "bluetoothInternalControllerInfo",
            "flagstate",
            "fmm-computer-name",
            "fmm-mobileme-token-FMM",
            "fmm-mobileme-token-FMM-BridgeHasAccount",
            "nvda_drv",
            "prev-lang:kbd",
            "backlight-level",
            "BootCampHD",
        ],
        "8BE4DF61-93CA-11D2-AA0D-00E098032B8C": [
            "Boot0080",
            "Boot0081",
            "Boot0082",
            "BootNext",
            "BootOrder",
        ],
    }

    # 1.0.8 Serial schema (Custom block removed). Init/Override unused.
    cfg["Misc"]["Serial"] = {"Init": False, "Override": False}

    # Do not ship previous machine identity. Generate locally with GenSMBIOS
    # for MacBookPro15,1 before using iCloud / iMessage.
    generic = cfg["PlatformInfo"]["Generic"]
    generic["MLB"] = "REPLACE_WITH_GENSMBIOS_MLB"
    generic["ROM"] = bytes.fromhex("112233445566")
    generic["SystemProductName"] = "MacBookPro15,1"
    generic["SystemSerialNumber"] = "REPLACE_WITH_GENSMBIOS_SERIAL"
    generic["SystemUUID"] = "00000000-0000-0000-0000-000000000000"

    # BlacklistAppleUpdate stays true so this SMBIOS is not offered Tahoe /
    # Golden Gate OTAs that this hardware cannot run usefully.
    cfg["Misc"]["Security"]["SecureBootModel"] = "Default"
    cfg["Misc"]["Security"]["Vault"] = "Optional"
    cfg["Misc"]["Security"]["ScanPolicy"] = 0
    cfg["Misc"]["Boot"]["PickerMode"] = "External"

    # Machine-specific Windows path from the previous tree is not portable.
    cfg["Misc"]["Entries"] = [
        {
            "Arguments": "",
            "Auxiliary": False,
            "Comment": "Optional. Fill Path locally if dual-booting Windows via OpenCore.",
            "Enabled": False,
            "Flavour": "Windows",
            "Name": "Windows",
            "Path": "",
            "TextMode": False,
        }
    ]

    cfg["Misc"]["Tools"] = [
        tool("OpenShell.efi", "UEFI Shell", "Not signed for security reasons",
             flavour="OpenShell:UEFIShell:Shell"),
        tool("CleanNvram.efi", "CleanNvram", "Legacy NVRAM cleaner; prefer ResetNvramEntry in picker",
             full_nvram=True, real_path=True, text_mode=True),
        tool("ControlMsrE2.efi", "ControlMsrE2", "Check CFG Lock (MSR 0xE2). Do not flash firmware from here.",
             full_nvram=False, real_path=False, text_mode=True),
    ]

    cfg["UEFI"]["Drivers"] = [
        driver("OpenRuntime.efi", "Required OpenCore runtime"),
        driver("OpenCanopy.efi", "Graphical picker"),
        driver("AudioDxe.efi", "Optional boot chime"),
        driver("HfsPlus.efi", "HFS+ from OcBinaryData"),
        driver("ExFatDxe.efi", "ExFAT volumes"),
        driver("ResetNvramEntry.efi", "Picker Reset NVRAM entry"),
        driver("ToggleSipEntry.efi", "SIP toggle file present but disabled; SIP stays enabled", enabled=False),
    ]
    cfg["UEFI"]["Unload"] = []

    # Kext order: Lilu first, then VirtualSMC family, WEG/ALC, then device kexts.
    # VoodooI2C plugins before VoodooI2C. Do not enable both VoodooInput copies.
    cfg["Kernel"]["Add"] = [
        kext("Lilu.kext", "1.7.2 | Patch engine", min_kernel="10.0.0"),
        kext("VirtualSMC.kext", "1.3.8 | SMC emulator", min_kernel="10.0.0"),
        kext("SMCBatteryManager.kext", "1.3.8 | Battery"),
        kext("SMCProcessor.kext", "1.3.8 | CPU thermal"),
        kext("RestrictEvents.kext", "1.1.6 | Memory tab / process name; no sbvmm boot-arg"),
        kext("WhateverGreen.kext", "1.7.1 | iGPU + dGPU disable helper", min_kernel="12.0.0"),
        kext("AppleALC.kext", "1.9.8 | ALC236 layout-id 18", min_kernel="12.0.0"),
        kext("RealtekRTL8111.kext", "3.0.0 | RTL8168H/RTL8111 Ethernet"),
        kext("CpuTscSync.kext", "1.1.2 | TSC sync on wake"),
        kext("NVMeFix.kext", "1.1.3 | NVMe PM"),
        kext("BrightnessKeys.kext", "1.0.3 | Brightness keys"),
        kext("AirportBrcmFixup.kext", "2.2.1 | Broadcom Wi-Fi (BCM94352Z in original tree)"),
        kext(
            "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcm4360_Injector.kext",
            "Catalina and older injector",
            executable="",
            max_kernel="19.9.9",
        ),
        kext(
            "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext",
            "Big Sur through Ventura injector; Sonoma+ needs OCLP for this card class",
            executable="",
        ),
        kext("BlueToolFixup.kext", "2.7.2 | Bluetooth Monterey+", min_kernel="21.0.0"),
        kext(
            "BrcmBluetoothInjector.kext",
            "2.7.2 | Bluetooth Big Sur and older",
            executable="",
            max_kernel="20.99.99",
        ),
        kext("BrcmFirmwareData.kext", "2.7.2 | Broadcom firmware store"),
        kext("BrcmPatchRAM3.kext", "2.7.2 | Broadcom firmware upload"),
        kext(
            "VoodooI2C.kext/Contents/PlugIns/VoodooI2CServices.kext",
            "VoodooI2C 2.9.1 services",
        ),
        kext(
            "VoodooI2C.kext/Contents/PlugIns/VoodooGPIO.kext",
            "VoodooI2C 2.9.1 GPIO",
        ),
        kext(
            "VoodooI2C.kext/Contents/PlugIns/VoodooInput.kext",
            "VoodooI2C 2.9.1 input; keep VoodooPS2 VoodooInput disabled",
        ),
        kext("VoodooI2C.kext", "2.9.1 | I2C controller"),
        kext("VoodooI2CHID.kext", "2.9.1 satellite | HID trackpad (ELAN061B in original tree)"),
        kext("VoodooPS2Controller.kext", "2.3.7 | PS/2 keyboard"),
        kext(
            "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Keyboard.kext",
            "2.3.7 | Keyboard",
        ),
        kext(
            "VoodooPS2Controller.kext/Contents/PlugIns/VoodooInput.kext",
            "Disabled; VoodooI2C already provides VoodooInput",
            enabled=False,
        ),
        kext(
            "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Mouse.kext",
            "Disabled; I2C trackpad is used",
            enabled=False,
        ),
        kext(
            "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Trackpad.kext",
            "Disabled; I2C trackpad is used",
            enabled=False,
        ),
        kext("USBPorts.kext", "Hardware USB map for MacBookPro15,1 / CNL XHCI 0xa36d8086", executable=""),
    ]

    CONFIG.write_bytes(plistlib.dumps(cfg, sort_keys=False))
    print(f"Wrote {CONFIG}")


if __name__ == "__main__":
    main()
