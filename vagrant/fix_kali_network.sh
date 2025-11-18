#!/bin/bash
# Fix Kali Linux NetworkManager interference with Vagrant networking

echo "Fixing Kali NetworkManager configuration..."

# Stop NetworkManager from managing the eth interfaces
sudo tee /etc/NetworkManager/conf.d/99-unmanaged-devices.conf > /dev/null <<EOF
[keyfile]
unmanaged-devices=interface-name:eth0;interface-name:eth1;interface-name:eth2;interface-name:eth3
EOF

# Restart NetworkManager to apply changes
sudo systemctl restart NetworkManager

# Ensure eth1 (private network) is properly configured
if ! grep -q "eth1" /etc/network/interfaces; then
    echo "Configuring eth1 interface..."
    sudo tee -a /etc/network/interfaces > /dev/null <<EOF

# Vagrant private network interface
auto eth1
iface eth1 inet static
EOF
fi

# Bring up the interface if it's down
sudo ip link set eth1 up 2>/dev/null || true

echo "Kali NetworkManager fix applied successfully"

