# Internal Intel Wi-Fi (not confirmed, not loaded)

The current owner’s internal WLAN chipset is **unknown** and is **not used**. Connectivity is an external USB adapter `0bda:8179` (`extras/usb-wifi/`). “Intel card” in that discussion meant **Intel UHD 630 graphics**, not Intel CNVi Wi-Fi.

USB tree: **Bluetooth Radio** VID `0x0bda` PID `0xb023` (Realtek, Built-in Yes). USB ID Repository: [RTL8822BE Bluetooth 4.2 Adapter](https://usb-ids.gowdy.us/read/UD/0bda/b023). Catalog clue only.

Bluetooth pane on Sonoma 14.3: State **On**, chipset **THIRD_PARTY_DONGLE**, USB transport, reported VendorID **`0x004c` (Apple)**, headphones listed **Not Connected**. The `0x004c` vendor is a **spoofed report**, not Apple or Broadcom silicon. Do not enable Broadcom kexts from it. It does **not** prove pairing works or identify PCI Wi-Fi.

Stock Y530 units sometimes shipped with Intel CNVi. That is not evidence for this machine. AirportItlwm is OS-version-specific; a random leftover kext is worse than none.

If you later identify an Intel CNVi device (`lspci` / Device Manager Hardware Ids) **and** you want it instead of USB Wi-Fi:

1. Download AirportItlwm or itlwm matching **that exact macOS version** from [OpenIntelWireless/itlwm](https://github.com/OpenIntelWireless/itlwm/releases).
2. Keep Broadcom kexts disabled.
3. Test from USB EFI.

Do not enable those kexts on a guess.
