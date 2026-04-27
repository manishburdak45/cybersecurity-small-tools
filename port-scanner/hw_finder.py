#!/usr/bin/env python3
"""
Remote Machine Hardware Name Finder
Usage: python3 script.py <target_ip> [username] [password]
Example: python3 script.py 192.168.1.100 root root123
"""

import sys
import socket
import platform
import subprocess
import re

def get_machine_hardware_name_local():
    """Get local machine hardware name"""
    return platform.machine()

def check_port(ip, port=22, timeout=2):
    """Check if SSH port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def get_remote_hardware_name_ssh(ip, username, password):
    """Get remote machine hardware name via SSH using paramiko or subprocess"""
    try:
        # Method 1: Try using sshpass with uname command
        cmd = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "uname -m"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    try:
        # Method 2: Try using paramiko (if installed)
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)
        stdin, stdout, stderr = ssh.exec_command("uname -m")
        output = stdout.read().decode().strip()
        ssh.close()
        if output:
            return output
    except ImportError:
        pass
    except Exception as e:
        return f"SSH Error: {str(e)}"
    
    return None

def get_remote_hardware_name_smb(ip, username, password):
    """Try to get via SMB/WMI (Windows targets)"""
    try:
        # Method: Using impacket if available
        import impacket
        from impacket.smbconnection import SMBConnection
        # This would need proper implementation based on target OS
        pass
    except:
        pass
    return None

def get_remote_hardware_name_http(ip, ports=[80, 8080, 443, 8443]):
    """Try OS detection via HTTP headers"""
    import urllib.request
    
    for port in ports:
        try:
            protocol = "https" if port in [443, 8443] else "http"
            url = f"{protocol}://{ip}:{port}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                headers = dict(response.headers)
                # Check common headers that reveal server info
                server = headers.get('Server', '')
                if 'nginx' in server.lower() and 'linux' in server.lower():
                    return "Likely Linux (x86_64)"
                elif 'iis' in server.lower() or 'windows' in server.lower():
                    return "Likely Windows (AMD64)"
        except:
            continue
    return None

def nmap_os_detection(ip):
    """Use nmap for OS detection"""
    try:
        cmd = f'nmap -O --osscan-guess {ip} -p 22,80,443 --max-os-tries=1 -T4'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        # Parse nmap output for OS details
        os_match = re.search(r'OS details: (.+)', result.stdout)
        os_cpe = re.search(r'OS CPE: (.+)', result.stdout)
        aggressive = re.search(r'Aggressive OS guesses: (.+)', result.stdout)
        
        if os_match:
            return os_match.group(1)
        if aggressive:
            return aggressive.group(1)
        if os_cpe:
            return os_cpe.group(1)
    except:
        pass
    return None

def dns_recon(ip):
    """Try reverse DNS for hostname hints"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except:
        return None

def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("  Remote Machine Hardware Name Finder")
        print("=" * 60)
        print(f"\nUsage: python3 {sys.argv[0]} <target_ip> [username] [password]")
        print(f"Example: python3 {sys.argv[0]} 192.168.1.100 root root123")
        print(f"Example: python3 {sys.argv[0]} 192.168.1.100 (will try unauthenticated methods)")
        print("\nMethods tried automatically:")
        print("  1. SSH (if credentials provided)")
        print("  2. Nmap OS Detection")
        print("  3. HTTP Header Analysis")
        print("  4. Reverse DNS Lookup")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else None
    password = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"\n[*] Target IP: {target_ip}")
    print(f"[*] Starting reconnaissance...\n")
    
    # Method 0: Check if it's localhost
    if target_ip in ['127.0.0.1', 'localhost', '0.0.0.0']:
        hw_name = get_machine_hardware_name_local()
        print(f"[✓] Local machine hardware name: {hw_name}")
        sys.exit(0)
    
    results = []
    
    # Method 1: Reverse DNS
    print("[*] Trying reverse DNS lookup...")
    hostname = dns_recon(target_ip)
    if hostname:
        print(f"    Hostname: {hostname}")
        results.append(f"Reverse DNS: {hostname}")
    else:
        print("    No reverse DNS record found")
    
    # Method 2: SSH with credentials
    if username and password:
        print(f"[*] Trying SSH login as {username}@{target_ip}...")
        if check_port(target_ip, 22):
            print(f"    Port 22 (SSH) is open")
            hw_name = get_remote_hardware_name_ssh(target_ip, username, password)
            if hw_name:
                print(f"[✓] Remote hardware name via SSH: {hw_name}")
                results.append(f"SSH: {hw_name}")
            else:
                print("    SSH authentication failed or command failed")
        else:
            print("    Port 22 (SSH) is closed")
    else:
        print("[*] No SSH credentials provided, skipping SSH method")
    
    # Method 3: HTTP headers
    print("[*] Trying HTTP header analysis...")
    http_info = get_remote_hardware_name_http(target_ip)
    if http_info:
        print(f"    HTTP Analysis: {http_info}")
        results.append(f"HTTP: {http_info}")
    else:
        print("    No web server detected on common ports")
    
    # Method 4: Nmap OS Detection
    print("[*] Running Nmap OS detection (may take a moment)...")
    nmap_os = nmap_os_detection(target_ip)
    if nmap_os:
        print(f"    Nmap OS Info: {nmap_os}")
        results.append(f"Nmap: {nmap_os}")
    else:
        print("    Nmap OS detection inconclusive")
    
    # Results Summary
    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    
    if results:
        for i, result in enumerate(results, 1):
            print(f"  [{i}] {result}")
    else:
        print("  [!] Could not determine machine hardware name.")
        print("      Try providing SSH credentials or ensure target is reachable.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
