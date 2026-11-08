# External USB Wi-Fi (`0bda:8179`)

Owner System Information (USB tree), transcribed — no screenshots and no serials:

- **802.11n NIC:** Vendor `0x0bda` (Realtek), Product `0x8179`, USB up to **480 Mb/s** (USB 2.0 High Speed)
- **Separate Bluetooth Radio:** VID `0x0bda` PID `0xb023` (Realtek), Built-in **Yes**

That USB-tree row is a catalog clue only. Sonoma’s Bluetooth pane later reported State On, **THIRD_PARTY_DONGLE**, USB, VendorID **`0x004c`** (spoofed Apple), headphones **Not Connected**. Do not treat `0x004c` as Apple/Broadcom hardware and do not infer pairing. Internal WLAN stays unknown/unused. See `extras/intel-wireless/README.md`.

This stick is already the daily network path on the current **Sonoma 14.3** install. This tree still does **not** inject a Wi-Fi kext.

## Chipset identity (VID/PID mapping)

| Source | What it names `0bda:8179` |
| --- | --- |
| [USB ID Repository](https://usb-ids.gowdy.us/read/UD/0bda/8179) (`usb.ids`) | **RTL8188EUS** 802.11n Wireless Network Adapter (1T1R, 2.4 GHz). Confirming comments 2013-06-30. Same PID noted on TL-WN725N(UN) Ver.2.2. |
| chris1111 Wireless-USB-OC-Big-Sur-Adapter **V17** `RtWlanU.kext` `Info.plist` (inspected 2026-11-08, **not copied into this repo**) | Personality **`RTL8188EU_8179`**: `idVendor` 3034 (`0x0bda`), `idProduct` 33145 (`0x8179`), `IOClass` `RtWlanU`, `IOProviderClass` `IOUSBInterface`, `bInterfaceNumber` 0 |

`RTL8188EU` is the Realtek family name in that kext. `RTL8188EUS` is the USB-interface variant name in the USB ID catalog. They are the same VID/PID, not two different adapters.

This mapping is **not** taken from a Linux driver (`r8188eu` / `rtl8xxxu`). Linux support is irrelevant to whether macOS will attach.

Related IDs that are **not** this stick: `0bda:8176` (RTL8188CUS), `0bda:0179` (RTL8188EU_ETV).

## Maintained macOS driver (if one exists)

There is **no** Apple native driver, **no** Acidanthera kext, and **no** currently maintained Realtek-published macOS source for this PID.

The only still-updated *packaging* that matches this VID/PID in a macOS kext is:

- Project: [chris1111/Wireless-USB-OC-Big-Sur-Adapter](https://github.com/chris1111/Wireless-USB-OC-Big-Sur-Adapter) (OpenCore installer; not the Clover/non-OC sibling)
- Latest GitHub release inspected: **V17** (release page lists 05 Jul 2025 “Support macOS Tahoe 26”; zip dated 2026-01-30 / “Update 10 Jan 2026” icons)
- Kext it would drop into `EFI/OC/Kexts`: `RtWlanU.kext` `com.realtek.driver.RtWlanU` **1830.32.b27** (`CFBundleGetInfoString` `1830.32.b27.11192020, Copyright © Realtek (R)` — Realtek blob dated 2020-11-19)
- Companion `RtWlanU1827.kext` is for older CU/RU IDs; it does **not** contain `0x8179`
- chris1111 `support.md` also lists `RTL8188EU`, `TL-WN725Nv3`, `TPLink_88EUSU`, and “Realtek (RTL8188)”

**This repo does not vendor that package.** chris1111 states there is no source; companies including Realtek abandoned it. Shipping `RtWlanU.kext` here would be license-unclear closed blobs.

Inspected V17 zip SHA-256 (research copy only, not in git):

`f71ab9e6e85767e2a711a919ff10bceb28de612d9df40e7a3d5befc72967bbba`

If the owner reinstalls macOS or moves EFI, install that package **themselves** from GitHub. Do not copy kexts from a forum zip.

## Sequoia vs Tahoe (and SIP / AMFI)

| OS | chris1111 claim | What this OpenCore tree does | Runtime on *this* stick |
| --- | --- | --- | --- |
| Sonoma 14 | Listed | No Wi-Fi kext injected; SIP stays on | Owner already uses the dongle on **14.3** |
| Sequoia 15.8.2 (fallback `config.plist`) | Listed; README says **Disable Gatekeeper** | Same: no `RtWlanU`, SIP `csr-active-config` zeros | **Not verified in this PR.** Expect the chris1111 installer, not Apple Wi-Fi. |
| Tahoe 26.7.2 (`config-tahoe-26.plist`) | README “Support macOS Tahoe 26” (05 Jul 2025) | Same: no `RtWlanU`, SIP on, **no** OCLP, **no** `AMFIPass`, **no** `amfi=0x80` | **Unverified.** Do not treat 26.7.2 USB Wi-Fi as supported by this EFI. |

chris1111 default README: *“To using any relase SIP Security must be disable! (Fully disable)”* (`csrutil disable`). Sequoia extra: [Disable-Gatekeeper](https://github.com/chris1111/Disable-Gatekeeper).

Optional “SIP SECURITY ENABLE YES” path ([discussion #167](https://github.com/chris1111/Wireless-USB-OC-Big-Sur-Adapter/discussions/167)): Recovery `spctl kext-consent add ZYM2ETK3E7`, temporary `csr-active-config` `03080000`, then back to zeros. That is still a security change. **Neither profile in this PR does it.**

chris1111 [Usage-macOS-Tahoe.md](https://github.com/chris1111/Wireless-USB-OC-Big-Sur-Adapter/blob/master/Usage-macOS-Tahoe.md) additionally requires:

1. A Tahoe 26 install
2. **Ethernet** during the procedure
3. [OCLP-Mod](https://github.com/laobamac/OCLP-Mod) (root patcher)
4. `AMFIPass.kext` **or** boot-arg `amfi=0x80`

That path is experimental and is documented in `docs/EXPERIMENTAL.md`. It is **not** applied to `config-tahoe-26.plist`. Community reports for RTL8188EUS / TL-WN725N on Tahoe are mixed (success only with those extra patches; other reports of the dongle not associating). None of that was run on this Y530.

`IOProviderClass` in the inspected personality is still `IOUSBInterface` (legacy USB family). That is a maintenance risk on newer kernels; it is not evidence the kext is Tahoe-ready.

## What this tree will not do

- Vendor `RtWlanU.kext` / `RtWlanU1827.kext`
- Lower SIP or AMFI in either plist
- Enable AirportItlwm or AirportBrcmFixup for this USB stick
- Infer PCI Wi-Fi from Bluetooth `0bda:b023`
- Promise Tahoe 26.7.2 wireless

Installers and OS upgrades: use **Ethernet** (`RealtekRTL8111.kext`). The Tahoe chris1111 procedure explicitly needs Ethernet anyway.
