#!/usr/bin/env python3
"""
Remote Machine Hardware Name Finder
Input: Target IP Address (and optionally SSH username/password)
Output: Machine hardware name only (e.g., x86_64, aarch64, armv7l)
"""

import socket
import subprocess
import re
import sys

def check_ssh_port(ip, timeout=2):
    """Check if SSH port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, 22))
        sock.close()
        return result == 0
    except:
        return False

def get_hardware_via_ssh(ip, username, password):
    """Connect via SSH and run uname -m to get hardware name"""
    try:
        # Try using sshpass
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "uname -m" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        # If sshpass fails, try with -o PreferredAuthentications=password
        cmd2 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o PreferredAuthentications=password {username}@{ip} "uname -m" 2>/dev/null"""
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
        
        if result2.returncode == 0 and result2.stdout.strip():
            return result2.stdout.strip()
            
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        return None
    
    return None

def get_hardware_via_nmap(ip):
    """Use nmap to detect hardware architecture from OS fingerprinting"""
    try:
        result = subprocess.run(
            ["nmap", "-O", "--osscan-guess", ip, "-T4", "--max-os-tries=1"],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout
        
        # Direct architecture indicators
        arch_patterns = {
            'x86_64': r'x86_64|amd64|Intel 64|x64|x86-64|i686|x86',
            'aarch64': r'aarch64|arm64|ARM64|ARM 64',
            'armv7l': r'armv7|ARMv7|armhf|ARM 32',
            'mips': r'mips|MIPS',
            'ppc64': r'ppc64|PowerPC|POWER'
        }
        
        for arch, pattern in arch_patterns.items():
            if re.search(pattern, output, re.IGNORECASE):
                return arch
        
        # Check OS details for architecture hints
        os_details = re.search(r'OS details: (.+)', output)
        if os_details:
            os_text = os_details.group(1)
            if 'Linux' in os_text:
                if 'ARM' in os_text or 'aarch' in os_text:
                    return 'aarch64'
                elif 'MIPS' in os_text:
                    return 'mips'
                else:
                    return 'x86_64'
            elif 'Windows' in os_text:
                return 'AMD64'
            elif 'RouterOS' in os_text or 'MikroTik' in os_text:
                return 'x86_64'  # MikroTik usually runs on x86_64
        
        # Aggressive OS guesses also
        aggressive = re.search(r'Aggressive OS guesses: (.+)', output)
        if aggressive:
            return aggressive.group(1).split(',')[0].strip()
            
    except:
        pass
    return None

def get_hardware_via_ping_ttl(ip):
    """Use TTL values to guess OS architecture"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", ip],
            capture_output=True,
            text=True,
            timeout=5
        )
        ttl_match = re.search(r'ttl=(\d+)', result.stdout, re.IGNORECASE)
        if ttl_match:
            ttl = int(ttl_match.group(1))
            if ttl <= 64:
                return 'x86_64'  # Linux/Unix
            elif ttl <= 128:
                return 'AMD64'   # Windows
    except:
        pass
    return None

def main():
    print("")  # Just newline, no extra text
    
    # Check if arguments passed
    if len(sys.argv) >= 2:
        target_ip = sys.argv[1]
        username = sys.argv[2] if len(sys.argv) >= 3 else "root"
        password = sys.argv[3] if len(sys.argv) >= 4 else ""
    else:
        target_ip = input("Enter Target IP: ").strip()
        
        # Ask for SSH credentials if port 22 is open
        if check_ssh_port(target_ip):
            use_ssh = input("SSH port 22 is open. Use SSH? (y/n): ").strip().lower()
            if use_ssh == 'y':
                username = input("Enter SSH username (default: root): ").strip() or "root"
                password = input("Enter SSH password: ").strip()
            else:
                username = None
                password = None
        else:
            username = None
            password = None
    
    hardware_name = None
    
    # Method 1: SSH (most accurate)
    if username and password:
        print("[*] Trying SSH...", file=sys.stderr)
        hardware_name = get_hardware_via_ssh(target_ip, username, password)
        if hardware_name:
            print(hardware_name)
            return
    
    # Method 2: Nmap OS detection
    print("[*] Trying Nmap OS detection...", file=sys.stderr)
    hardware_name = get_hardware_via_nmap(target_ip)
    if hardware_name:
        print(hardware_name)
        return
    
    # Method 3: Ping TTL guess
    print("[*] Trying Ping TTL analysis...", file=sys.stderr)
    hardware_name = get_hardware_via_ping_ttl(target_ip)
    if hardware_name:
        print(hardware_name)
        return
    
    # Fallback
    print("x86_64")

if __name__ == "__main__":
    main()
