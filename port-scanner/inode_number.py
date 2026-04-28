#!/usr/bin/env python3
"""
Debug: List directory contents and find files
"""

import subprocess
import sys

def main():
    target_ip = input("Enter Target IP: ").strip()
    username = input("Enter SSH username: ").strip()
    password = input("Enter SSH password: ").strip()
    directory = input("Enter Directory: ").strip() or "/var/backups"
    
    # List directory
    cmd1 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{target_ip} "ls -la {directory}" 2>/dev/null"""
    result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True, timeout=10)
    
    print("\n[*] Directory Contents:")
    if result1.stdout:
        print(result1.stdout)
    if result1.stderr:
        print(f"[ERROR] {result1.stderr}")
    
    # List all .bak files
    cmd2 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{target_ip} "find / -name '*.bak' -type f 2>/dev/null | head -30" 2>/dev/null"""
    result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=15)
    
    print("\n[*] All .bak files on system:")
    if result2.stdout:
        print(result2.stdout)
    else:
        print("No .bak files found")
    
    # List all shadow files
    cmd3 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{target_ip} "find / -name '*shadow*' -type f 2>/dev/null | head -30" 2>/dev/null"""
    result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True, timeout=15)
    
    print("\n[*] All shadow-related files on system:")
    if result3.stdout:
        print(result3.stdout)
    else:
        print("No shadow files found")
    
    # Inode number of shadow file
    cmd4 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{target_ip} "stat -c '%i' /etc/shadow 2>/dev/null" 2>/dev/null"""
    result4 = subprocess.run(cmd4, shell=True, capture_output=True, text=True, timeout=10)
    
    print("\n[*] Inode number of /etc/shadow:")
    if result4.stdout:
        print(result4.stdout)
    else:
        print("Could not get inode")

if __name__ == "__main__":
    main()
