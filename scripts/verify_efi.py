#!/usr/bin/env python3
"""Static EFI consistency checks for Sequoia fallback and Tahoe-26 profiles."""
from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OC = ROOT / "EFI/OC"
CONFIG_SEQUOIA = OC / "config.plist"
CONFIG_TAHOE = OC / "config-tahoe-26.plist"
USBPORTS = OC / "Kexts/USBPorts.kext/Contents/Info.plist"

PLACEHOLDER_SERIALS = {"REPLACE_WITH_GENSMBIOS_SERIAL"}
PLACEHOLDER_MLB = {"REPLACE_WITH_GENSMBIOS_MLB"}
PLACEHOLDER_UUID = "00000000-0000-0000-0000-000000000000"
NVRAM_GUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
BRCM_BUNDLES = {
    "AirportBrcmFixup.kext",
    "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcm4360_Injector.kext",
    "AirportBrcmFixup.kext/Contents/PlugIns/AirPortBrcmNIC_Injector.kext",
    "BlueToolFixup.kext",
    "BrcmBluetoothInjector.kext",
    "BrcmFirmwareData.kext",
    "BrcmPatchRAM3.kext",
}
# Closed-source Realtek USB Wi-Fi / Tahoe AMFI helpers: documented, never shipped.
FORBIDDEN_KEXTS = {
    "RtWlanU.kext",
    "RtWlanU1827.kext",
    "AMFIPass.kext",
}


def check_common(cfg: dict, label: str) -> list[str]:
    errors: list[str] = []
    generic = cfg["PlatformInfo"]["Generic"]
    if generic["SystemSerialNumber"] not in PLACEHOLDER_SERIALS:
        errors.append(f"{label}: serial is not a safe placeholder")
    if generic["MLB"] not in PLACEHOLDER_MLB:
        errors.append(f"{label}: MLB is not a safe placeholder")
    if generic["SystemUUID"] != PLACEHOLDER_UUID:
        errors.append(f"{label}: UUID is not the zero placeholder")
    if generic["SystemProductName"] != "MacBookPro15,1":
        errors.append(f"{label}: expected MacBookPro15,1 SMBIOS")
    if generic["ROM"] != bytes.fromhex("112233445566"):
        errors.append(f"{label}: ROM is not the dummy placeholder")

    ig = cfg["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"]
    if ig["AAPL,ig-platform-id"] != bytes.fromhex("00009b3e"):
        errors.append(f"{label}: iGPU platform-id mapping changed unexpectedly")
    if ig["framebuffer-con1-index"] != b"\xff\xff\xff\xff":
        errors.append(f"{label}: framebuffer-con1-index should remain disabled")
    if ig["framebuffer-con2-index"] != b"\xff\xff\xff\xff":
        errors.append(f"{label}: framebuffer-con2-index should remain disabled")

    nvadd = cfg["NVRAM"]["Add"][NVRAM_GUID]
    boot_args = nvadd["boot-args"].split()
    if "-wegnoegpu" not in boot_args:
        errors.append(f"{label}: missing -wegnoegpu")
    if "-v" in boot_args:
        errors.append(f"{label}: verbose boot should not be default")
    if nvadd["csr-active-config"] != b"\x00\x00\x00\x00":
        errors.append(f"{label}: SIP is not fully enabled (csr-active-config)")

    for entry in cfg["ACPI"]["Add"]:
        if not (OC / "ACPI" / entry["Path"]).exists():
            errors.append(f"{label}: missing ACPI {entry['Path']}")
    for entry in cfg["UEFI"]["Drivers"]:
        if not (OC / "Drivers" / entry["Path"]).exists():
            errors.append(f"{label}: missing driver {entry['Path']}")
        if "HideVerbose" not in entry:
            errors.append(f"{label}: driver {entry['Path']} missing HideVerbose")
    for entry in cfg["Misc"]["Tools"]:
        if not (OC / "Tools" / entry["Path"]).exists():
            errors.append(f"{label}: missing tool {entry['Path']}")

    enabled = []
    for entry in cfg["Kernel"]["Add"]:
        bundle = OC / "Kexts" / entry["BundlePath"]
        if not (bundle / entry["PlistPath"]).exists():
            errors.append(f"{label}: missing kext plist {entry['BundlePath']}")
            continue
        exe = entry.get("ExecutablePath") or ""
        if entry["Enabled"] and exe and not (bundle / exe).exists():
            errors.append(f"{label}: missing kext executable {entry['BundlePath']}/{exe}")
        if entry["Enabled"]:
            enabled.append(entry["BundlePath"])
        if entry["BundlePath"] in BRCM_BUNDLES and entry["Enabled"]:
            errors.append(f"{label}: Broadcom kext enabled but internal WLAN is unknown/unused")

    if not enabled or enabled[0] != "Lilu.kext":
        errors.append(f"{label}: Lilu.kext must load first")
    if "USBPorts.kext" not in enabled:
        errors.append(f"{label}: USBPorts.kext must stay enabled")
    if "WhateverGreen.kext" not in enabled:
        errors.append(f"{label}: WhateverGreen.kext required for Intel UHD 630")
    if "SSDT-NoHybGfx.aml" not in [e["Path"] for e in cfg["ACPI"]["Add"] if e["Enabled"]]:
        errors.append(f"{label}: SSDT-NoHybGfx must stay enabled")
    return errors, enabled


def check_usbports() -> list[str]:
    errors: list[str] = []
    data = plistlib.loads(USBPORTS.read_bytes())
    ports = data["IOKitPersonalities"]["MacBookPro15,1-XHC"]["IOProviderMergeProperties"]["ports"]
    for name, port in ports.items():
        if "port" not in port:
            errors.append(f"USBPorts {name} missing port")
        if "usb-port-number" not in port:
            errors.append(f"USBPorts {name} missing usb-port-number (needed for Tahoe)")
        elif port.get("port") != port.get("usb-port-number"):
            errors.append(f"USBPorts {name} port/usb-port-number mismatch")
    return errors


def main() -> None:
    errors: list[str] = []
    if not CONFIG_TAHOE.exists():
        errors.append("missing EFI/OC/config-tahoe-26.plist")

    seq = plistlib.loads(CONFIG_SEQUOIA.read_bytes())
    tah = plistlib.loads(CONFIG_TAHOE.read_bytes()) if CONFIG_TAHOE.exists() else None

    seq_err, seq_enabled = check_common(seq, "sequoia")
    errors.extend(seq_err)
    boot_seq = seq["NVRAM"]["Add"][NVRAM_GUID]["boot-args"].split()
    if "-no_compat_check" in boot_seq or "revpatch=sbvmm" in boot_seq:
        errors.append("sequoia: must not include Tahoe spoofing boot-args")
    if seq["Misc"]["Security"]["SecureBootModel"] != "Default":
        errors.append("sequoia: SecureBootModel should remain Default")
    alc = {e["BundlePath"]: e["Enabled"] for e in seq["Kernel"]["Add"]}
    if not alc.get("AppleALC.kext"):
        errors.append("sequoia: AppleALC must stay enabled")

    if tah is not None:
        tah_err, tah_enabled = check_common(tah, "tahoe")
        errors.extend(tah_err)
        boot_tah = tah["NVRAM"]["Add"][NVRAM_GUID]["boot-args"].split()
        if "-no_compat_check" not in boot_tah:
            errors.append("tahoe: missing -no_compat_check")
        if "revpatch=sbvmm" not in boot_tah:
            errors.append("tahoe: missing revpatch=sbvmm (Dortania OTA/installer)")
        if tah["Misc"]["Security"]["SecureBootModel"] != "Disabled":
            errors.append("tahoe: SecureBootModel must be Disabled (documented spoofing tradeoff)")
        alc_t = {e["BundlePath"]: e["Enabled"] for e in tah["Kernel"]["Add"]}
        if alc_t.get("AppleALC.kext"):
            errors.append("tahoe: AppleALC must be disabled (AppleHDA removed)")
        if tah["NVRAM"]["Add"][NVRAM_GUID]["csr-active-config"] != b"\x00\x00\x00\x00":
            errors.append("tahoe: must not lower SIP by default")
    else:
        tah_enabled = []

    errors.extend(check_usbports())

    live = {p.name for p in (OC / "Kexts").iterdir() if p.suffix == ".kext"}
    shipped_forbidden = sorted(live & FORBIDDEN_KEXTS)
    if shipped_forbidden:
        errors.append(f"closed-source/experimental kexts must not be vendored: {shipped_forbidden}")
    referenced = {e["BundlePath"].split("/")[0] for e in seq["Kernel"]["Add"]}
    if tah is not None:
        referenced |= {e["BundlePath"].split("/")[0] for e in tah["Kernel"]["Add"]}
    orphan = sorted(live - referenced)
    if orphan:
        errors.append(f"kexts on disk not referenced in configs: {orphan}")
    if (OC / "oldConfig.plist").exists():
        errors.append("oldConfig.plist must not be shipped")

    print("Static EFI verification")
    print(f"  sequoia: {CONFIG_SEQUOIA} enabled={len(seq_enabled)}")
    print(f"  tahoe:   {CONFIG_TAHOE} enabled={len(tah_enabled)}")
    print("  kext versions:")
    for name in sorted(live):
        info = plistlib.loads((OC / "Kexts" / name / "Contents/Info.plist").read_bytes())
        ver = info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")
        print(f"    {name:40} {ver}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        raise SystemExit(1)
    print("OK: Sequoia fallback, Tahoe-26 profile, USB map, and identity checks passed")


if __name__ == "__main__":
    main()
