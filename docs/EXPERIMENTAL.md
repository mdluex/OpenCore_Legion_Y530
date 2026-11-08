# Experimental paths (not default)

Nothing in this file is enabled in `EFI/OC/config.plist`. These options exist only so "latest macOS" is not claimed by weakening SIP, Secure Boot, or by installing root patches.

## macOS Tahoe 26.7.2

Apple's last Intel macOS. Official hardware list is 2019 16-inch MacBook Pro, 2020 13-inch MacBook Pro (4× Thunderbolt 3), 2020 27-inch iMac, and 2019 Mac Pro. The 2018 15-inch MacBook Pro (`MacBookPro15,1`) is **not** listed.

Even if the installer is forced:

- Analog audio through AppleALC will not work: AppleHDA was removed in macOS 26 (Dortania Tahoe notes).
- Workarounds are VoodooHDA (quality drop) or OpenCore Legacy Patcher restoring AppleHDA (**root patch, SIP off**).
- UHD 630 as the only GPU on a dropped SMBIOS is unproven on this laptop.

Do not add `revpatch=sbvmm`, `-no_compat_check`, or `SecureBootModel=Disabled` as defaults to chase Tahoe.

## OpenCore Legacy Patcher (modern wireless / root patches)

BCM94352Z Wi-Fi on Sonoma and Sequoia generally needs OCLP's modern wireless patches (legacy IO80211). That requires:

- Disabling SIP (`csr-active-config` non-zero)
- AMFI-related patches
- Re-applying patches after every OS update

That is an **opt-in** you do locally if Ethernet is not enough. It is not shipped here. If you go that route, keep this default EFI on a USB so you can boot with SIP enabled again.

## Golden Gate 27.2

Apple silicon only. There is no Intel kernel. Not a Hackintosh target.

## Changing iGPU platform-id

Dortania currently recommends `0900A53E` for UHD 630 laptops. This tree keeps `00009B3E` plus disabled `con1`/`con2` because HDMI is dGPU-wired. If the internal panel will not accelerate, try `0900A53E` on a **USB EFI** only, and restore immediately if you get a black screen.
