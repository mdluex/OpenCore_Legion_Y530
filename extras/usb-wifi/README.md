# External USB Wi-Fi (`0bda:8179`)

Owner System Information (USB tree), transcribed — no screenshots and no serials:

- **802.11n NIC:** Vendor `0x0bda` (Realtek), Product `0x8179`, USB up to **480 Mb/s**
- **Separate Bluetooth Radio:** VID `0x0bda` PID `0xb023` (Realtek), Built-in **Yes** — catalog clue only, not PCI Wi-Fi proof

This stick is the daily network path on **Sonoma 14.3**. This Sequoia-only EFI still does **not** inject a Wi-Fi kext.

## Chipset identity (VID/PID mapping)

| Source | What it names `0bda:8179` |
| --- | --- |
| [USB ID Repository](https://usb-ids.gowdy.us/read/UD/0bda/8179) | **RTL8188EUS** 802.11n (1T1R, 2.4 GHz) |
| chris1111 Wireless-USB-OC-Big-Sur-Adapter **V17** `RtWlanU.kext` (inspected, **not copied**) | Personality **`RTL8188EU_8179`**: `idVendor` 3034 (`0x0bda`), `idProduct` 33145 (`0x8179`) |

`RTL8188EU` is the Realtek family name in that kext; `RTL8188EUS` is the USB-variant catalog name. Same VID/PID. This is **not** inferred from a Linux driver.

## Sequoia compatibility is unknown

There is no Apple native driver and no Acidanthera kext. The only still-updated packaging is chris1111’s closed Realtek blob (`com.realtek.driver.RtWlanU` 1830.32.b27, dated 2020-11-19).

chris1111 lists Sequoia 15, but:

- Default README: SIP must be **fully disabled** (`csrutil disable`)
- Sequoia extra: Disable Gatekeeper
- Optional “SIP enable yes” still needs Recovery `spctl kext-consent add ZYM2ETK3E7` and a temporary `csr-active-config` change

**This tree does not apply any of that.** `csr-active-config` stays zeros. `RtWlanU` is not shipped. **Wi-Fi after a Sequoia upgrade is not guaranteed.** Use Ethernet (`RealtekRTL8111.kext`) for the installer and for downloading Xcode 26.3.

If the owner later installs chris1111 themselves, that is outside this EFI and is a security tradeoff.

## What this tree will not do

- Vendor `RtWlanU.kext`
- Lower SIP or AMFI
- Enable AirportItlwm or AirportBrcmFixup for this USB stick
- Infer PCI Wi-Fi from Bluetooth `0bda:b023` or from spoofed Bluetooth VendorID `0x004c`
