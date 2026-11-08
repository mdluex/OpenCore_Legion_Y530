#!/bin/bash
# Install ALCPlugFix from this repository's ALCPlugFix/ directory.
# Does not download from third-party URLs and does not format disks.

set -euo pipefail

echo "
************************************************************************************
         ALCPlugFix for Legion Y530 ALC236 (local files from this repo)
         Based on Optimzate Script by xiaoM, https://github.com/xiaoMGitHub
************************************************************************************
"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="${SCRIPT_DIR}/ALCPlugFix"
DAEMON_PATH=/Library/LaunchDaemons/
BIN_PATH=/usr/local/bin/
ALC_DAEMON_CONFIG=good.win.ALCPlugFix.plist
ALCPlugFix=ALCPlugFix
ALC_VERB=alc-verb

if [[ ! -f "${SRC}/${ALCPlugFix}" || ! -f "${SRC}/${ALC_VERB}" || ! -f "${SRC}/${ALC_DAEMON_CONFIG}" ]]; then
    echo "Missing files under ${SRC}. Run this script from a clone of this repository."
    exit 1
fi

if [[ ! -d "$BIN_PATH" ]]; then
    sudo mkdir -p "$BIN_PATH"
fi

echo "Copying files from ${SRC} ..."
sudo cp "${SRC}/${ALC_VERB}" "${BIN_PATH}"
sudo cp "${SRC}/${ALCPlugFix}" "${BIN_PATH}"
sudo cp "${SRC}/${ALC_DAEMON_CONFIG}" "${DAEMON_PATH}"

echo "Setting permissions..."
sudo chmod 755 "${BIN_PATH}${ALC_VERB}"
sudo chown "${USER}:admin" "${BIN_PATH}${ALC_VERB}"
sudo chmod 755 "${BIN_PATH}${ALCPlugFix}"
sudo chown "${USER}:admin" "${BIN_PATH}${ALCPlugFix}"
sudo chmod 644 "${DAEMON_PATH}${ALC_DAEMON_CONFIG}"
sudo chown root:wheel "${DAEMON_PATH}${ALC_DAEMON_CONFIG}"

echo "Loading ALCPlugFix..."
if sudo launchctl list | grep --quiet good.win.ALCPlugFix; then
    echo "Stopping existing ALCPlugFix daemon."
    sudo launchctl unload "${DAEMON_PATH}${ALC_DAEMON_CONFIG}"
fi
sudo launchctl load -w "${DAEMON_PATH}${ALC_DAEMON_CONFIG}"

echo "Done."
exit 0
