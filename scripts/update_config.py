#!/usr/bin/env python3
"""Regenerate the Sequoia-only OpenCore profile for this Y530 EFI.

Does not invent SMBIOS identity. Writes obvious local placeholders only.
Internal WLAN is unknown; Broadcom and Intel Wi-Fi kexts stay disabled.
This script must not write a Tahoe plist or Tahoe bypass boot-args.
"""
from __future__ import annotations

import copy
import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OC = ROOT / "EFI/OC"
CONFIG_SEQUOIA = OC / "config.plist"

NVRAM_GUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"


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


def kernel_add(*, applealc: bool) -> list:
    # Internal WLAN chipset is unknown and unused. Broadcom kexts remain on disk
    # but disabled so this tree does not assume BCM94352Z or Intel CNVi.
    return [
        kext("Lilu.kext", "1.7.2 | Patch engine", min_kernel="10.0.0"),
        kext("VirtualSMC.kext", "1.3.8 | SMC emulator", min_kernel="10.0.0"),
        kext("SMCBatteryManager.kext", "1.3.8 | Battery"),
        kext("SMCProcessor.kext", "1.3.8 | CPU thermal"),
        kext("RestrictEvents.kext", "1.1.6 | RestrictEvents (no revpatch=sbvmm; Sequoia profile)"),
        kext("WhateverGreen.kext", "1.7.1 | Intel UHD 630 + disable Pascal dGPU", min_kernel="12.0.0"),
        kext(
            "AppleALC.kext",
            "1.9.8 | ALC236 layout-id 18 (original-tree codec mapping)",
            enabled=applealc,
            min_kernel="12.0.0",
        ),
        kext("RealtekRTL8111.kext", "3.0.0 | RTL8168H/RTL8111 Ethernet"),
        kext("CpuTscSync.kext", "1.1.2 | TSC sync on wake"),
        kext("NVMeFix.kext", "1.1.3 | NVMe PM"),
        kext("BrightnessKeys.kext", "1.0.3 | Brightness keys"),
        kext(
            "AirportBrcmFixup.kext",
            "2.2.1 | Optional Broadcom Wi-Fi. Disabled: internal card unknown / unused",
            enabled=False,
        ),
        kext(
            "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcm4360_Injector.kext",
            "Catalina and older injector",
            executable="",
            enabled=False,
            max_kernel="19.9.9",
        ),
        kext(
            "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext",
            "Big Sur through Ventura injector",
            executable="",
            enabled=False,
        ),
        kext(
            "BlueToolFixup.kext",
            "2.7.2 | Optional Broadcom Bluetooth. Disabled until BT chip is identified",
            enabled=False,
            min_kernel="21.0.0",
        ),
        kext(
            "BrcmBluetoothInjector.kext",
            "2.7.2 | Optional Broadcom BT injector",
            executable="",
            enabled=False,
            max_kernel="20.99.99",
        ),
        kext(
            "BrcmFirmwareData.kext",
            "2.7.2 | Optional Broadcom firmware store",
            enabled=False,
        ),
        kext(
            "BrcmPatchRAM3.kext",
            "2.7.2 | Optional Broadcom firmware upload",
            enabled=False,
        ),
        kext("VoodooI2C.kext/Contents/PlugIns/VoodooI2CServices.kext", "VoodooI2C 2.9.1 services"),
        kext("VoodooI2C.kext/Contents/PlugIns/VoodooGPIO.kext", "VoodooI2C 2.9.1 GPIO"),
        kext(
            "VoodooI2C.kext/Contents/PlugIns/VoodooInput.kext",
            "VoodooI2C 2.9.1 input; keep VoodooPS2 VoodooInput disabled",
        ),
        kext("VoodooI2C.kext", "2.9.1 | I2C controller"),
        kext("VoodooI2CHID.kext", "2.9.1 satellite | HID trackpad"),
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
        kext(
            "USBPorts.kext",
            "Hardware USB map MacBookPro15,1 / CNL XHCI 0xa36d8086",
            executable="",
        ),
    ]


def apply_common(cfg: dict) -> None:
    cfg["Booter"]["Quirks"]["ClearTaskSwitchBit"] = False

    nvadd = cfg["NVRAM"]["Add"][NVRAM_GUID]
    nvadd["ForceDisplayRotationInEFI"] = 0
    nvadd["csr-active-config"] = b"\x00\x00\x00\x00"
    nvadd["bluetoothExternalDongleFailed"] = b"\x00"
    nvadd["bluetoothInternalControllerInfo"] = bytes(14)

    cfg["NVRAM"]["Delete"][NVRAM_GUID] = ["boot-args", "ForceDisplayRotationInEFI"]
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

    cfg["Misc"]["Serial"] = {"Init": False, "Override": False}

    generic = cfg["PlatformInfo"]["Generic"]
    generic["MLB"] = "REPLACE_WITH_GENSMBIOS_MLB"
    generic["ROM"] = bytes.fromhex("112233445566")
    generic["SystemProductName"] = "MacBookPro15,1"
    generic["SystemSerialNumber"] = "REPLACE_WITH_GENSMBIOS_SERIAL"
    generic["SystemUUID"] = "00000000-0000-0000-0000-000000000000"

    cfg["Misc"]["Security"]["Vault"] = "Optional"
    cfg["Misc"]["Security"]["ScanPolicy"] = 0
    cfg["Misc"]["Boot"]["PickerMode"] = "External"
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


def write_sequoia(base: dict) -> Path:
    cfg = copy.deepcopy(base)
    apply_common(cfg)
    cfg["#WARNING - Profile"] = (
        "Sequoia 15.8.2 only. SIP on (csr-active-config zeros), AppleALC, "
        "SecureBootModel Default. No Tahoe bypass flags."
    )
    cfg["NVRAM"]["Add"][NVRAM_GUID]["boot-args"] = "keepsyms=1 debug=0x100 -wegnoegpu"
    cfg["Misc"]["Security"]["SecureBootModel"] = "Default"
    cfg["Misc"]["Security"]["BlacklistAppleUpdate"] = True
    cfg["Kernel"]["Add"] = kernel_add(applealc=True)
    CONFIG_SEQUOIA.write_bytes(plistlib.dumps(cfg, sort_keys=False))
    print(f"Wrote {CONFIG_SEQUOIA}")
    return CONFIG_SEQUOIA


def main() -> None:
    if (OC / "config-tahoe-26.plist").exists():
        raise SystemExit("Refuse to run: Tahoe plist is present; this tree is Sequoia-only")
    base = plistlib.loads(CONFIG_SEQUOIA.read_bytes())
    write_sequoia(base)


if __name__ == "__main__":
    main()
