# Optional paths that are not applied by default

Neither profile turns SIP off, installs OCLP, or patches the macOS root volume.

## Analog audio on Tahoe

[Dortania](https://dortania.github.io/OpenCore-Install-Guide/extras/tahoe.html): AppleHDA is gone in macOS 26, so AppleALC cannot drive ALC236 speakers/headphones.

SIP-on options (preferred):

- USB audio dongle (class-compliant; no kext). HDMI audio is not a fallback here because HDMI is wired to the disabled GTX 1050 Ti.
- Ethernet/USB already work without touching SIP.

Options that **lower security** (not in this EFI):

- Dortania VoodooHDA method: `csr-active-config` `03000000`, copy VoodooHDA to `/Library/Extensions`. Quality is often worse. Do this yourself if you accept SIP bits off.
- OCLP / SimpleHDA restoring AppleHDA: root patch, re-apply after every update. Not shipped.

## Internal Wi-Fi / Broadcom / Intel CNVi

The current owner’s internal card is **unknown and unused**. Broadcom kexts in `EFI/OC/Kexts` are disabled in both profiles. Do not enable them to “try.” See `extras/usb-wifi/README.md` for the USB adapter (model still unknown).

OCLP modern wireless and AppleBCMWLANCompanion are irrelevant until a chipset is identified. They are not enabled.

## iGPU platform-id

Dortania laptop UHD 630 ID `0900A53E` is **not** the default. This tree keeps `00009B3E` plus disabled `con1`/`con2`. Try `0900A53E` only on a USB EFI if the internal panel has no acceleration.
