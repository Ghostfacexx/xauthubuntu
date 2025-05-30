#!/bin/bash

# Exit on any error
set -e

# Ensure script is run as root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root. Use sudo or switch to root user."
    exit 1
fi

# Step 1: Remove snap Firefox and any residual packages
echo "Removing snap Firefox and conflicting packages..."
snap remove --purge firefox 2>/dev/null || true
apt remove --purge firefox -y 2>/dev/null || true
rm -f /usr/bin/firefox

# Step 2: Add Mozilla PPA
echo "Adding Mozilla Team PPA..."
apt update
apt install -y software-properties-common
add-apt-repository ppa:mozillateam/ppa -y

# Step 3: Pin Mozilla PPA to prioritize Firefox deb package
echo "Configuring PPA pinning for Mozilla Firefox..."
echo 'Package: firefox*
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001' > /etc/apt/preferences.d/mozilla-firefox

# Step 4: Install Firefox deb version
echo "Installing Firefox deb version..."
apt update
apt install -y -t 'o=LP-PPA-mozillateam' firefox

# Step 5: Verify installation
FIREFOX_PATH=$(which firefox)
FIREFOX_VERSION=$($FIREFOX_PATH --version 2>/dev/null || echo "Unknown")
echo "Firefox installed at: $FIREFOX_PATH"
echo "Firefox version: $FIREFOX_VERSION"

# Step 6: Configure X11 authentication for root
echo "Configuring X11 authentication for root..."
XAUTH_KEY=$(xauth list | grep "unix:10" | head -n 1)
if [ -n "$XAUTH_KEY" ]; then
    echo "$XAUTH_KEY" | xauth -f /root/.Xauthority add
    chown root:root /root/.Xauthority
    chmod 600 /root/.Xauthority
    echo "X11 authentication configured for root."
else
    echo "Warning: No X11 authentication key found for unix:10. Ensure X11 forwarding is enabled."
fi

# Step 7: Provide instructions for testing
echo "Installation complete! To test Firefox with X11 forwarding:"
echo "1. Ensure DISPLAY is set: export DISPLAY=localhost:10.0"
echo "2. Run: firefox --no-remote www.google.com"
echo "If issues persist, verify X11 forwarding in MobaXterm and /etc/ssh/sshd_config."
