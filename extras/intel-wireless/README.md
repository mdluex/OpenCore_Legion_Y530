# Intel wireless (opt-in, not in the live EFI)

The previous live config loaded **Broadcom** kexts (AirportBrcmFixup + BrcmPatchRAM) matching the original author's documented BCM94352Z replacement.

Stock Legion Y530 units often shipped with Intel CNVi (model varies). That is **not confirmed** for the current owner. The old `AirportItlwm.kext` 2.2.0 and `IntelBluetoothFirmware.kext` 2.3.0 that sat unused in `EFI/OC/Kexts` were removed so they cannot be enabled by accident: AirportItlwm builds are **macOS-version-specific** and a mismatched kext is worse than no kext.

If you confirm an Intel card (`lspci` / Windows Device Manager / Linux `lshw`):

1. Download the AirportItlwm (or itlwm + Heliport) build that matches **your macOS version** from [OpenIntelWireless](https://github.com/OpenIntelWireless/itlwm/releases).
2. Download a matching IntelBluetoothFirmware + IntelBTPatcher / BlueToolFixup set from [OpenIntelWireless/IntelBluetoothFirmware](https://github.com/OpenIntelWireless/IntelBluetoothFirmware/releases).
3. Disable the Broadcom kexts in `config.plist` (do not load both stacks).
4. Test from USB EFI.

Do not guess the card from this README.
