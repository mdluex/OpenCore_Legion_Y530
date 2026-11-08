# Upstream pins (verified 2026-11-08)

SHA-256 hashes are of the **downloaded GitHub release zip** (or git commit for OcBinaryData), computed locally after `curl -L` from the official repository. Do not assume a version from memory; re-hash if you re-fetch.

## OpenCore

| Artifact | Source | Published | SHA-256 |
| --- | --- | --- | --- |
| OpenCore-1.0.8-RELEASE.zip | https://github.com/acidanthera/OpenCorePkg/releases/tag/1.0.8 | 2026-09-27 | `2011e8b7216ecb2645d97ea710df965947edd406846e92050b9bc4190be6d27b` |

`tools/ocvalidate.linux` is copied from that zip (`Utilities/ocvalidate/ocvalidate.linux`). It reports: *only compatible with OpenCore version 1.0.8*.

## Kexts

| Zip | Source | SHA-256 |
| --- | --- | --- |
| Lilu-1.7.2-RELEASE.zip | https://github.com/acidanthera/Lilu/releases/tag/1.7.2 (2026-03-20) | `53967d7dcfaab01023a33df2e969a89522f13d6654a6a56ac4711b62dabf3ab8` |
| WhateverGreen-1.7.1-RELEASE.zip | https://github.com/acidanthera/WhateverGreen/releases/tag/1.7.1 (2026-09-27) | `1bfdd2d40290ecce237606db121cbc01d7041179f03394bd59660a2ed52e5c95` |
| AppleALC-1.9.8-RELEASE.zip | https://github.com/acidanthera/AppleALC/releases/tag/1.9.8 (2026-09-27) | `d4d36cd2da7863cf7cbfcb0892d45c08457f4f4ddd065a073dd010e46bd63bcb` |
| VirtualSMC-1.3.8-RELEASE.zip | https://github.com/acidanthera/VirtualSMC/releases/tag/1.3.8 (2026-09-27) | `2e29a8aaf91b4eb0bcdf5913ed17e70f5cf76531122acd4132eff7813a54de8b` |
| AirportBrcmFixup-2.2.1-RELEASE.zip | https://github.com/acidanthera/AirportBrcmFixup/releases/tag/2.2.1 (2026-09-27) | `2432c8a62445ad2cdadcc59b73928f01f8bf42bcd3f4386e49bc63a1c91db06f` |
| BrcmPatchRAM-2.7.2-RELEASE.zip | https://github.com/acidanthera/BrcmPatchRAM/releases/tag/2.7.2 (2026-03-20) | `e1c1c55347526d031a8ae2fdd1f52efa3019161e497fb38e1cfa809752f8af21` |
| NVMeFix-1.1.3-RELEASE.zip | https://github.com/acidanthera/NVMeFix/releases/tag/1.1.3 (2026-07-07) | `e1d5657ab7ac31f69771708f7b80bf218ab9aa0b8e4c4fe6ff943983037e3dfb` |
| CpuTscSync-1.1.2-RELEASE.zip | https://github.com/acidanthera/CpuTscSync/releases/tag/1.1.2 (2026-07-07) | `bc289f780c52015ae788827b3db8e6c2ab9f512992b3a157a4a5c15df1eb4ed3` |
| VoodooPS2Controller-2.3.7-RELEASE.zip | https://github.com/acidanthera/VoodooPS2/releases/tag/2.3.7 (2025-12-03) | `d5483298736ba4b3b82c7203d9a46968c668fb7af732b8b22c2096deb0acf83f` |
| BrightnessKeys-1.0.3-RELEASE.zip | https://github.com/acidanthera/BrightnessKeys/releases/tag/1.0.3 (2023-04-03) | `c9a80f6275e39c18886087a70ba0fe615ce45f83b7afa254b74335f7a92b8544` |
| RestrictEvents-1.1.6-RELEASE.zip | https://github.com/acidanthera/RestrictEvents/releases/tag/1.1.6 (2025-07-07) | `98170dfae195ddd28b5d95e3f040125a13ca783bcb9bd1e5b8c588e217b14ee6` |
| VoodooI2C-2.9.1-RELEASE.zip | https://github.com/VoodooI2C/VoodooI2C/releases/tag/v2.9.1 (2024-11-06) | `368e5eb60794583c340764813bd7e8244e94d3d3c06ea5b67034addd539487f4` |
| RealtekRTL8111-V3.0.0.zip | https://github.com/Mieze/RTL8111_driver_for_OS_X/releases/tag/v3.0.0 (2025-12-24) | `a0f2e64ac3c76e2d416ff88f35a197ce229e74ea78e968631a736a43b4d8231c` |

RestrictEvents-1.1.6-RELEASE.zip also matches the GitHub asset digest `sha256:98170dfae195ddd28b5d95e3f040125a13ca783bcb9bd1e5b8c588e217b14ee6`.

## OcBinaryData

| Item | Source |
| --- | --- |
| Commit | `640e7e9240938f2529e725351e1e1150dc3569db` (2026-10-21, https://github.com/acidanthera/OcBinaryData) |
| HfsPlus.efi | `a55b5fff36578864ba6792c4c6369c71f6f35b61dd5a853ddf8583cd36c31d8f` |
| ExFatDxe.efi | `a6d1f20d22b429c2b90e6c37f52260c0dfed9be473906d9547fbafe9e5c5f942` |

Image/Font/Label resources were copied from that commit. Existing OpenCanopy Audio files in this repo were left in place.

## macOS version sources

- Latest versions table: https://support.apple.com/en-us/109033 (published 2026-10-26)
- Sequoia compatibility: https://support.apple.com/en-us/120282 (includes MacBook Pro 15-inch 2018)
- Tahoe compatibility: https://support.apple.com/en-us/122867 (published 2026-09-14; 2018 15-inch MacBook Pro absent)

## Hardware-specific files not replaced from upstream

- `EFI/OC/ACPI/*.aml`
- `EFI/OC/Kexts/USBPorts.kext`
- `ALCPlugFix/`
- DeviceProperties for UHD 630 connectors and ALC236 layout-id 18
