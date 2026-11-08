# Legacy VoodooI2CHID (ELAN061B button workaround)

The live EFI uses **VoodooI2C 2.9.1** and its HID satellite. Upstream 2.9 listed physical-button fixes, so the default is the current release.

This folder stores the **previous tree's** VoodooI2CHID, which the original README described as a workaround for ELAN061B trackpad buttons. If buttons regress on 2.9.1:

1. Boot a USB EFI.
2. Replace `EFI/OC/Kexts/VoodooI2CHID.kext` with this copy.
3. Keep Force Click unchecked in Trackpad settings.

SYNA2B46 users should use current upstream HID, not this workaround.
