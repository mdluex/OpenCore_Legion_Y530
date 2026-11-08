#!/usr/bin/env python3
"""Static EFI consistency checks. Does not boot hardware."""
from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OC = ROOT / "EFI/OC"
CONFIG = OC / "config.plist"

PLACEHOLDER_SERIALS = {"REPLACE_WITH_GENSMBIOS_SERIAL"}
PLACEHOLDER_MLB = {"REPLACE_WITH_GENSMBIOS_MLB"}
PLACEHOLDER_UUID = "00000000-0000-0000-0000-000000000000"


def main() -> None:
    errors: list[str] = []
    cfg = plistlib.loads(CONFIG.read_bytes())

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
        errors.append("ROM is not the dummy 112233445566 placeholder")

    ig = cfg["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x2,0x0)"]
    if ig["AAPL,ig-platform-id"] != bytes.fromhex("00009b3e"):
        errors.append("iGPU platform-id mapping changed unexpectedly")
    if ig["framebuffer-con1-index"] != b"\xff\xff\xff\xff":
        errors.append("framebuffer-con1-index should remain disabled")
    if ig["framebuffer-con2-index"] != b"\xff\xff\xff\xff":
        errors.append("framebuffer-con2-index should remain disabled")

    audio = cfg["DeviceProperties"]["Add"]["PciRoot(0x0)/Pci(0x1f,0x3)"]
    if audio.get("layout-id") != 18:
        errors.append("ALC layout-id 18 mapping changed unexpectedly")

    boot_args = cfg["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
    if "-wegnoegpu" not in boot_args.split():
        errors.append("missing -wegnoegpu boot-arg for Pascal dGPU disable")
    if "-v" in boot_args.split():
        errors.append("verbose boot should not be default")

    csr = cfg["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"]
    if csr != b"\x00\x00\x00\x00":
        errors.append("SIP is not fully enabled (csr-active-config)")

    if cfg["Misc"]["Security"]["SecureBootModel"] != "Default":
        errors.append("SecureBootModel should remain Default")

    for entry in cfg["ACPI"]["Add"]:
        path = OC / "ACPI" / entry["Path"]
        if not path.exists():
            errors.append(f"missing ACPI {entry['Path']}")

    for entry in cfg["UEFI"]["Drivers"]:
        path = OC / "Drivers" / entry["Path"]
        if not path.exists():
            errors.append(f"missing driver {entry['Path']}")
        if "HideVerbose" not in entry:
            errors.append(f"driver {entry['Path']} missing HideVerbose")

    for entry in cfg["Misc"]["Tools"]:
        path = OC / "Tools" / entry["Path"]
        if not path.exists():
            errors.append(f"missing tool {entry['Path']}")

    enabled_kexts = []
    for entry in cfg["Kernel"]["Add"]:
        bundle = OC / "Kexts" / entry["BundlePath"]
        plist_path = bundle / entry["PlistPath"]
        if not plist_path.exists():
            errors.append(f"missing kext plist {entry['BundlePath']}")
            continue
        exe = entry.get("ExecutablePath") or ""
        if entry["Enabled"] and exe:
            if not (bundle / exe).exists():
                errors.append(f"missing kext executable {entry['BundlePath']}/{exe}")
        if entry["Enabled"]:
            enabled_kexts.append(entry["BundlePath"])

    if enabled_kexts[0] != "Lilu.kext":
        errors.append("Lilu.kext must load first")
    if "USBPorts.kext" not in enabled_kexts:
        errors.append("USBPorts.kext must stay enabled")
    if "SSDT-NoHybGfx.aml" not in [e["Path"] for e in cfg["ACPI"]["Add"] if e["Enabled"]]:
        errors.append("SSDT-NoHybGfx must stay enabled")

    live = {p.name for p in (OC / "Kexts").iterdir() if p.suffix == ".kext"}
    referenced = {e["BundlePath"].split("/")[0] for e in cfg["Kernel"]["Add"]}
    orphan = sorted(live - referenced)
    if orphan:
        errors.append(f"kexts on disk not referenced in config: {orphan}")

    if (OC / "oldConfig.plist").exists():
        errors.append("oldConfig.plist must not be shipped")

    print("Static EFI verification")
    print(f"  config: {CONFIG}")
    print(f"  SMBIOS: {generic['SystemProductName']} (placeholders only)")
    print(f"  enabled kexts: {len(enabled_kexts)}")
    print("  kext versions:")
    for name in sorted(live):
        info = plistlib.loads((OC / "Kexts" / name / "Contents/Info.plist").read_bytes())
        ver = info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")
        print(f"    {name:40} {ver}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        raise SystemExit(1)
    print("OK: file-reference, identity placeholder, and mapping checks passed")


if __name__ == "__main__":
    main()
