# External USB Wi-Fi (model not in this repo)

The working network path on this laptop is an **external USB adapter**. The chipset/model has not been provided, so **no driver is enabled and none is promised**.

macOS natively supports almost no random USB Wi-Fi sticks. Many Realtek/MediaTek/older Ralink dongles need third-party kexts that may not exist for Sequoia or Tahoe. Do not assume “plug and play.”

## What to send so a driver can be evaluated

Any one of:

- Printed name on the dongle (photo of the chip/label)
- Windows Device Manager → Network adapters → Properties → Details → **Hardware Ids** (`VID_xxxx&PID_xxxx`)
- Linux/macOS: `ioreg -p IOUSB -l -w 0` / `lsusb` vendor:product
- Chipset string if known (example: RTL8812AU, MT7921, AR9271)

Until that exists, use **Ethernet** (`RealtekRTL8111.kext`) for installs and updates.

## What this tree will not do

- Guess Intel internal Wi-Fi from “I use the Intel card” when that referred to **graphics**
- Enable AirportItlwm or AirportBrcmFixup for an unidentified USB stick
- Claim the dongle will work on Tahoe
