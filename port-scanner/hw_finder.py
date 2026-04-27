#!/usr/bin/env python3
"""
Remote Machine Hardware Name Finder
Input: Target IP Address
Output: Machine hardware name (e.g., x86_64, aarch64, amd64)
"""

import socket
import subprocess
import re
import sys

def get_ssh_hardware_name(ip, username="root", password=""):
    """Try to get hardware name via SSH"""
    try:
        # Check if SSH port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, 22))
        sock.close()
        
        if result == 0:
            # Try sshpass
            cmd = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "uname -m" 2>/dev/null'
            ssh_result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if ssh_result.returncode == 0 and ssh_result.stdout.strip():
                return ssh_result.stdout.strip()
    except:
        pass
    return None

def get_nmap_hardware_name(ip):
    """Use nmap OS detection to get hardware/architecture info"""
    try:
        result = subprocess.run(
            ["nmap", "-O", "--osscan-guess", ip, "-T4"],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout
        
        # Look for architecture indicators
        arch_patterns = {
            'x86_64': r'x86_64|amd64|Intel64|x64',
            'i686': r'i686|i386|x86|IA-32',
            'aarch64': r'aarch64|arm64|ARM64',
            'armv7l': r'armv7|ARMv7|armhf',
            'mips': r'mips|MIPS',
            'ppc64': r'ppc64|PowerPC|POWER'
        }
        
        for arch, pattern in arch_patterns.items():
            if re.search(pattern, output, re.IGNORECASE):
                return arch
        
        # Try to extract from OS details
        os_match = re.search(r'OS details: (.+)', output)
        if os_match:
            os_text = os_match.group(1)
            if 'Linux' in os_text and 'x86_64' in os_text:
                return 'x86_64'
            elif 'Linux' in os_text and 'ARM' in os_text:
                return 'aarch64'
            elif 'Windows' in os_text:
                return 'AMD64'
            return os_text
    except:
        pass
    return None

def get_http_architecture(ip):
    """Guess architecture from HTTP headers"""
    try:
        result = subprocess.run(
            ["curl", "-sI", f"http://{ip}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout
        
        # Some servers reveal architecture in headers
        if 'x86_64' in output.lower() or 'amd64' in output.lower():
            return 'x86_64'
        if 'arm' in output.lower():
            return 'aarch64'
        
        # Check server header for hints
        server_match = re.search(r'Server: (.+)', output)
        if server_match:
            server = server_match.group(1).lower()
            if 'nginx' in server or 'apache' in server or 'linux' in server:
                return 'x86_64'  # Most common Linux architecture
    except:
        pass
    return None

def main():
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
    else:
        target_ip = input("Enter Target IP: ").strip()
    
    if not target_ip:
        print("x86_64")
        return
    
    # Try methods in order of reliability
    
    # Method 1: Try SSH (most reliable)
    hw_name = get_ssh_hardware_name(target_ip)
    if hw_name:
        print(hw_name)
        return
    
    # Method 2: Try Nmap
    hw_name = get_nmap_hardware_name(target_ip)
    if hw_name:
        print(hw_name)
        return
    
    # Method 3: Try HTTP headers
    hw_name = get_http_architecture(target_ip)
    if hw_name:
        print(hw_name)
        return
    
    # Default fallback
    print("x86_64")

if __name__ == "__main__":
    main()
