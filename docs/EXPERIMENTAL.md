# Optional paths that are not applied

This Sequoia-only tree does not turn SIP off, disable Apple Secure Boot, install OCLP, or patch the macOS root volume.

## USB Wi-Fi `0bda:8179`

See `extras/usb-wifi/README.md`. Sequoia runtime for this stick is **unknown**. The usual third-party installer wants SIP off and Gatekeeper off. That is a security change you would apply yourself. This EFI does not inject `RtWlanU` and does not change `csr-active-config`.

## Internal WLAN / Broadcom / Intel CNVi

Unknown and unused. Broadcom kexts remain on disk **disabled**. Bluetooth reported VendorID `0x004c` is spoofed; do not enable Broadcom from it.

## iGPU platform-id

This tree keeps `00009B3E` plus disabled `con1`/`con2` (Sonoma already reports Device ID `0x3e9b`, Metal 3, 1920×1080). Dortania laptop ID `0900A53E` is not the default. Try it only on a USB EFI if the panel has no acceleration after Sequoia.
