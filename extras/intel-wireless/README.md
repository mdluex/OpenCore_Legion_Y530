# Internal Intel Wi-Fi (not confirmed, not loaded)

The current owner’s internal WLAN chipset is **unknown** and is **not used**. Connectivity is an external USB adapter (`extras/usb-wifi/`). “Intel card” in that discussion meant **Intel UHD 630 graphics**, not Intel CNVi Wi-Fi.

Stock Y530 units sometimes shipped with Intel CNVi. That is not evidence for this machine. AirportItlwm is OS-version-specific; a random leftover kext is worse than none.

If you later identify an Intel CNVi device (`lspci` / Device Manager Hardware Ids) **and** you want it instead of USB Wi-Fi:

1. Download AirportItlwm or itlwm matching **that exact macOS version** from [OpenIntelWireless/itlwm](https://github.com/OpenIntelWireless/itlwm/releases).
2. Keep Broadcom kexts disabled.
3. Test from USB EFI.

Do not enable those kexts on a guess.
