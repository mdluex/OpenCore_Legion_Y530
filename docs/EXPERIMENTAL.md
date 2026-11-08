# Optional paths that are not applied by default

Neither profile turns SIP off, installs OCLP, or patches the macOS root volume.

## Analog audio on Tahoe

[Dortania](https://dortania.github.io/OpenCore-Install-Guide/extras/tahoe.html): AppleHDA is gone in macOS 26, so AppleALC cannot drive analog speakers/headphones. **ALC236** is the original tree’s codec mapping; owner photos only show Sonoma Built-in Input/Output enumerated (2 ch / 44100 Hz), not a codec string and not a playback test.

SIP-on options (preferred):

- USB audio dongle (class-compliant; no kext). HDMI audio is not a fallback here because HDMI is wired to the disabled GTX 1050 Ti.
- Ethernet/USB already work without touching SIP.

Options that **lower security** (not in this EFI):

- Dortania VoodooHDA method: `csr-active-config` `03000000`, copy VoodooHDA to `/Library/Extensions`. Quality is often worse. Do this yourself if you accept SIP bits off.
- OCLP / SimpleHDA restoring AppleHDA: root patch, re-apply after every update. Not shipped.

## Internal Wi-Fi / Broadcom / Intel CNVi

The current owner’s internal WLAN is **unknown and unused**. Bluetooth Radio USB `0bda:b023` is catalogued as RTL8822BE BT; that still does not identify PCI Wi-Fi. Broadcom kexts in `EFI/OC/Kexts` are disabled in both profiles. Do not enable them to “try.” Daily Wi-Fi is USB `0bda:8179` — see `extras/usb-wifi/README.md`.

OCLP modern wireless and AppleBCMWLANCompanion are irrelevant here. They are not enabled.

## USB Wi-Fi on Tahoe (not applied)

chris1111’s Tahoe instructions for Realtek USB adapters require OCLP-Mod plus `AMFIPass.kext` or `amfi=0x80`, and Ethernet during that procedure. That lowers AMFI / uses a root patcher.

This tree does **not** add those kexts, boot-args, or patches. Sequoia remains the SIP-on fallback. If USB wireless is required on 26.x, that is an owner-applied experiment on a USB EFI, then re-check after every update. Runtime of `0bda:8179` on Tahoe **26.7.2** is unverified.

## iGPU platform-id

Dortania laptop UHD 630 ID `0900A53E` is **not** the default. This tree keeps `00009B3E` plus disabled `con1`/`con2`. Try `0900A53E` only on a USB EFI if the internal panel has no acceleration.
