# Tahoe analog audio (not injected)

`config-tahoe-26.plist` leaves SIP on and AppleALC **off**. Built-in analog will be silent on Tahoe until you choose an opt-in. **ALC236** is repo-original; Sonoma 14.3 only shows Built-in mic/speaker endpoints enumerated, not a codec ID and not a listening test.

Preferred: USB audio interface, SIP unchanged.

If you later want VoodooHDA, follow [Dortania Tahoe analog audio](https://dortania.github.io/OpenCore-Install-Guide/extras/tahoe.html) yourself (`csr-active-config` `03000000` + `/Library/Extensions`). That is a security tradeoff this profile does not apply.
