# Attackbox Extension

- Extension Name: attackbox
- Description: Add a Kali Linux attackbox with default SSH credentials for exploitation activities
- Machine name: {{lab_name}}-ATTACKBOX
- Compatible with labs:
  - GOAD
  - GOAD-Light
  - GOAD-Mini
  - NHA
  - SCCM

## Lab Info

- **Hostname**: attackbox
- **IP Address**: {{ip_range}}.100 (e.g., 192.168.10.100)
- **Operating System**: Kali Linux (Latest Rolling)
- **Default Credentials**:
  - Username: `kali`
  - Password: `kali`
- **SSH Access**: Port 22 (enabled with password authentication)

## Features

- **Pre-installed Tools**:
  - Network scanning: nmap, masscan
  - Web enumeration: gobuster, feroxbuster, nikto, wpscan
  - SMB enumeration: smbclient, smbmap, enum4linux-ng
  - Active Directory: bloodhound, crackmapexec, evil-winrm, impacket
  - Password attacks: john, hashcat, hydra
  - Frameworks: metasploit-framework, burpsuite
  - Post-exploitation: responder, mimikatz, PowerSploit
  - General: sqlmap, searchsploit, exploitdb

- **Additional Repositories**:
  - LinEnum, PEASS-ng (linpeas)
  - PowerSploit, Invoke-Obfuscation
  - Rubeus, SharpHound
  - Windows Exploit Suggester

- **Workspace Setup**:
  - `/home/kali/workspace` - Working directory for engagement files
  - `/home/kali/tools` - Custom tools and scripts
  - `/home/kali/wordlists` - Password and enumeration wordlists
  - `/opt/` - Cloned security tools and frameworks

## Provider Support

The attackbox extension supports all major GOAD providers:

### VirtualBox
- Uses `kalilinux/rolling` Vagrant box
- 2 CPUs, 4GB RAM
- SSH forwarded to host port 2222

### Proxmox
- Requires Kali Linux template named `kali-linux-2024`
- 2 cores, 4GB RAM, 50GB disk
- Cloud-init enabled with SSH keys

### VMware
- Uses `kalilinux/rolling` Vagrant box
- Same specifications as VirtualBox

### AWS
- Uses official Kali Linux AMI
- t3.medium instance type
- 50GB EBS volume
- SSH password authentication enabled

### Azure
- Uses Kali Linux marketplace image
- Standard_B2s VM size
- Public IP assigned for external access

### Ludus
- Uses `kali-2024-x64` template
- Fully automated deployment

## Prerequisites

### For Cloud Providers (AWS/Azure)
- Ensure Kali Linux marketplace images are available in your subscription
- Configure appropriate security groups/NSGs to allow SSH access

### For Local Providers (VirtualBox/VMware)
- Install the Kali Linux Vagrant box:
  ```bash
  vagrant box add kalilinux/rolling
  ```

### For Proxmox
- Create a Kali Linux template named `kali-linux-2024`
- Ensure cloud-init is configured on the template

### For Ludus
- Ensure `kali-2024-x64` template is available in your Ludus environment

## Usage

1. **Deploy the extension**:
   ```bash
   cd /path/to/GOAD
   ./goad.py -t install -l <LAB> -p <PROVIDER> -m attackbox
   ```

2. **Access the attackbox**:
   ```bash
   # SSH access
   ssh kali@<IP_ADDRESS>
   # Password: kali
   
   # For VirtualBox with port forwarding
   ssh kali@localhost -p 2222
   ```

3. **Start exploitation activities**:
   ```bash
   # Example: Scan the lab network
   nmap -sC -sV 192.168.10.0/24
   
   # Example: Use BloodHound for AD enumeration
   bloodhound-python -u guest -p guest -ns 192.168.10.1 -d sevenkingdoms.local -c all
   
   # Example: Use CrackMapExec for SMB enumeration
   crackmapexec smb 192.168.10.0/24
   ```

## Security Considerations

⚠️ **Warning**: This attackbox is configured with default credentials for lab use only. 

- Default SSH credentials (`kali:kali`) are intentionally weak for easy access
- Password authentication is enabled for convenience
- This configuration should **NEVER** be used in production environments
- Ensure proper network isolation when deploying in shared environments

## Customization

You can customize the attackbox by modifying:

- `ansible/install.yml` - Add/remove tools and configurations
- `data/config.json` - Modify machine specifications
- Provider-specific files - Adjust CPU, memory, or network settings

## Troubleshooting

### SSH Connection Issues
- Verify the machine is accessible: `ping <IP_ADDRESS>`
- Check SSH service: `systemctl status ssh` (on the attackbox)
- Ensure firewall allows SSH traffic

### Tool Installation Issues
- Update package cache: `sudo apt update`
- Reinstall failed packages: `sudo apt install --reinstall <package>`

### Performance Issues
- Increase CPU/RAM allocation in provider configuration
- Monitor resource usage: `htop` or `top`

## Integration with GOAD Labs

The attackbox is designed to work seamlessly with all GOAD lab environments:

- **GOAD**: Full Active Directory environment with multiple domains
- **GOAD-Light**: Simplified AD environment
- **GOAD-Mini**: Minimal AD setup
- **NHA**: Network and Host Analysis lab
- **SCCM**: System Center Configuration Manager environment

The attackbox provides all necessary tools for:
- Active Directory enumeration and exploitation
- Network reconnaissance and scanning
- Web application testing
- Post-exploitation activities
- Privilege escalation techniques
- Lateral movement simulation
