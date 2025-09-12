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

## Provider Support

The attackbox extension supports all major GOAD providers:

### VirtualBox
- Uses `kalilinux/rolling` Vagrant box
- 2 CPUs, 4GB RAM
- SSH forwarded to host port 2222

### VMware
- Uses `kalilinux/rolling` Vagrant box
- Same specifications as VirtualBox

### Ludus
- Uses `kali-2024-x64` template
- Fully automated deployment

## Prerequisites

### For Local Providers (VirtualBox/VMware)
- Install the Kali Linux Vagrant box:
  ```bash
  vagrant box add kalilinux/rolling
  ```

### For Ludus
- Ensure `kali-2024-x64` template is available in your Ludus environment

## Security Considerations

⚠️ **Warning**: This attackbox is configured with default credentials for lab use only. 

- Default SSH credentials (`kali:kali`) are intentionally weak for easy access
- Password authentication is enabled for convenience
- This configuration should **NEVER** be used in production environments
- Ensure proper network isolation when deploying in shared environments

## Customization

You can customize the attackbox by modifying:

- `ansible/install.yml` - Add/remove tools and configurations
- Provider-specific files - Adjust CPU, memory, or network settings

## Troubleshooting

### SSH Connection Issues
- Verify the machine is accessible: `ping <IP_ADDRESS>`
- Check SSH service: `systemctl status ssh` (on the attackbox)
- Ensure firewall allows SSH traffic

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
