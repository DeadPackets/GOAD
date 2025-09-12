resource "ludus_vm" "attackbox" {
  template            = "kali-x64-desktop-template"
  vm_name             = "{{lab_name}}-attackbox"
  cpus                = 2
  ram_gb              = 4
  hard_disk_size_gb   = 50

  network_config {
    ip_address = "{{ip_range}}.100"
    subnet_mask = "255.255.255.0"
    gateway = "{{ip_range}}.1"
    dns_servers = ["{{ip_range}}.1", "8.8.8.8"]
  }

  # Enable SSH with password authentication
  user_data = <<-EOF
    #!/bin/bash
    # Set up SSH with password authentication
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
    systemctl restart ssh

    # Set kali user password
    echo 'kali:kali' | chpasswd

    # Add kali user to sudoers if not already present
    usermod -aG sudo kali
  EOF

  tags = {
    role = "attackbox"
    os   = "kali"
  }
}
