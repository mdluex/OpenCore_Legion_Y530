#!/usr/bin/env python3
"""Static EFI checks for the Sequoia-only OpenCore profile."""
from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OC = ROOT / "EFI/OC"
CONFIG = OC / "config.plist"
USBPORTS = OC / "Kexts/USBPorts.kext/Contents/Info.plist"

PLACEHOLDER_SERIALS = {"REPLACE_WITH_GENSMBIOS_SERIAL"}
PLACEHOLDER_MLB = {"REPLACE_WITH_GENSMBIOS_MLB"}
PLACEHOLDER_UUID = "00000000-0000-0000-0000-000000000000"
NVRAM_GUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
TAHOE_BOOT_ARGS = {"-no_compat_check", "revpatch=sbvmm"}
BRCM_BUNDLES = {
    "AirportBrcmFixup.kext",
    "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcm4360_Injector.kext",
    "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext",
    "BlueToolFixup.kext",
    "BrcmBluetoothInjector.kext",
    "BrcmFirmwareData.kext",
    "BrcmPatchRAM3.kext",
}
FORBIDDEN_KEXTS = {
    "RtWlanU.kext",
    "RtWlanU1827.kext",
    "AMFIPass.kext",
}


def check_config(cfg: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    generic = cfg["PlatformInfo"]["Generic"]
    if generic["SystemSerialNumber"] not in PLACEHOLDER_SERIALS:
        errors.append("serial is not a safe placeholder")
    if generic["MLB"] not in PLACEHOLDER_MLB:
        errors.append("MLB is not a safe placeholder")
    if generic["SystemUUID"] != PLACEHOLDER_UUID:
        errors.append("UUID is not the zero placeholder")
    if generic["SystemProductName"] != "MacBookPro15,1":
        errors.append("expected MacBookPro15,1 SMBIOS")
    if generic["ROM"] != bytes.fromhex("112233445566"):
        errors.append("ROM is not the dummy placeholder")

    ig = cfg["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"]
    if ig["AAPL,ig-platform-id"] != bytes.fromhex("00009b3e"):
        errors.append("iGPU platform-id mapping changed unexpectedly")
    if ig["framebuffer-con1-index"] != b"\xff\xff\xff\xff":
        errors.append("framebuffer-con1-index should remain disabled")
    if ig["framebuffer-con2-index"] != b"\xff\xff\xff\xff":
        errors.append("framebuffer-con2-index should remain disabled")

    nvadd = cfg["NVRAM"]["Add"][NVRAM_GUID]
    boot_args = nvadd["boot-args"].split()
    if "-wegnoegpu" not in boot_args:
        errors.append("missing -wegnoegpu")
    if "-v" in boot_args:
        errors.append("verbose boot should not be default")
    leaked = TAHOE_BOOT_ARGS.intersection(boot_args)
    if leaked:
        errors.append(f"Tahoe bypass boot-args must not be present: {sorted(leaked)}")
    if nvadd["csr-active-config"] != b"\x00\x00\x00\x00":
        errors.append("SIP is not fully enabled (csr-active-config)")
    if cfg["Misc"]["Security"]["SecureBootModel"] != "Default":
        errors.append("SecureBootModel must remain Default")

    for entry in cfg["ACPI"]["Add"]:
        if not (OC / "ACPI" / entry["Path"]).exists():
            errors.append(f"missing ACPI {entry['Path']}")
    for entry in cfg["UEFI"]["Drivers"]:
        if not (OC / "Drivers" / entry["Path"]).exists():
            errors.append(f"missing driver {entry['Path']}")
        if "HideVerbose" not in entry:
            errors.append(f"driver {entry['Path']} missing HideVerbose")
        if entry["Path"] == "ToggleSipEntry.efi" and entry["Enabled"]:
            errors.append("ToggleSipEntry.efi must stay disabled")
    for entry in cfg["Misc"]["Tools"]:
        if not (OC / "Tools" / entry["Path"]).exists():
            errors.append(f"missing tool {entry['Path']}")

    enabled = []
    alc_on = False
    for entry in cfg["Kernel"]["Add"]:
        bundle = OC / "Kexts" / entry["BundlePath"]
        if not (bundle / entry["PlistPath"]).exists():
            errors.append(f"missing kext plist {entry['BundlePath']}")
            continue
        exe = entry.get("ExecutablePath") or ""
        if entry["Enabled"] and exe and not (bundle / exe).exists():
            errors.append(f"missing kext executable {entry['BundlePath']}/{exe}")
        if entry["Enabled"]:
            enabled.append(entry["BundlePath"])
        if entry["BundlePath"] in BRCM_BUNDLES and entry["Enabled"]:
            errors.append("Broadcom kext enabled but internal WLAN is unknown/unused")
        if entry["BundlePath"] == "AppleALC.kext":
            alc_on = bool(entry["Enabled"])

    if not enabled or enabled[0] != "Lilu.kext":
        errors.append("Lilu.kext must load first")
    if "USBPorts.kext" not in enabled:
        errors.append("USBPorts.kext must stay enabled")
    if "WhateverGreen.kext" not in enabled:
        errors.append("WhateverGreen.kext required for Intel UHD 630")
    if "RealtekRTL8111.kext" not in enabled:
        errors.append("RealtekRTL8111.kext must stay enabled for Ethernet installs")
    if not alc_on:
        errors.append("AppleALC must stay enabled on Sequoia")
    if "SSDT-NoHybGfx.aml" not in [e["Path"] for e in cfg["ACPI"]["Add"] if e["Enabled"]]:
        errors.append("SSDT-NoHybGfx must stay enabled")
    return errors, enabled


def check_usbports() -> list[str]:
    errors: list[str] = []
    data = plistlib.loads(USBPORTS.read_bytes())
    ports = data["IOKitPersonalities"]["MacBookPro15,1-XHC"]["IOProviderMergeProperties"]["ports"]
    for name, port in ports.items():
        if "port" not in port:
            errors.append(f"USBPorts {name} missing port")
    return errors


def main() -> None:
    errors: list[str] = []
    if (OC / "config-tahoe-26.plist").exists():
        errors.append("Tahoe profile must not be shipped in this Sequoia-only tree")
    if list(ROOT.glob("extras/tahoe-audio/**")):
        errors.append("extras/tahoe-audio must not be shipped in this Sequoia-only tree")

    cfg = plistlib.loads(CONFIG.read_bytes())
    cfg_err, enabled = check_config(cfg)
    errors.extend(cfg_err)
    errors.extend(check_usbports())

    live = {p.name for p in (OC / "Kexts").iterdir() if p.suffix == ".kext"}
    shipped_forbidden = sorted(live & FORBIDDEN_KEXTS)
    if shipped_forbidden:
        errors.append(f"closed-source/experimental kexts must not be vendored: {shipped_forbidden}")
    referenced = {e["BundlePath"].split("/")[0] for e in cfg["Kernel"]["Add"]}
    orphan = sorted(live - referenced)
    if orphan:
        errors.append(f"kexts on disk not referenced in config: {orphan}")
    if (OC / "oldConfig.plist").exists():
        errors.append("oldConfig.plist must not be shipped")

    print("Static EFI verification (Sequoia-only)")
    print(f"  config: {CONFIG} enabled={len(enabled)}")
    print("  kext versions:")
    for name in sorted(live):
        info = plistlib.loads((OC / "Kexts" / name / "Contents/Info.plist").read_bytes())
        ver = info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")
        print(f"    {name:40} {ver}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        raise SystemExit(1)
    print("OK: Sequoia profile, USB map, SIP/SecureBoot, and identity checks passed")


if __name__ == "__main__":
    main()
