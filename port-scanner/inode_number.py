#!/usr/bin/env python3
"""
Universal Inode Number Finder via SSH
Input 1: Target IP Address
Input 2: Directory path (e.g., /var/backups)
Input 3: Filename to check (e.g., shadow.bak)
Output: Inode number only (e.g., 1234567)
"""

import socket
import subprocess
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

def run_ssh_command(ip, username, password, command):
    """Run any command via SSH and return output"""
    try:
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "{command}" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def list_directory(ip, username, password, directory):
    """List all files in directory with inode numbers"""
    command = f"ls -la '{directory}' 2>/dev/null"
    return run_ssh_command(ip, username, password, command)

def get_inode_number(ip, username, password, filepath):
    """Get inode number for a specific file"""
    # Method 1: stat
    inode = run_ssh_command(ip, username, password, f"stat -c '%i' '{filepath}' 2>/dev/null")
    if inode and inode.isdigit():
        return inode
    
    # Method 2: ls -li
    inode = run_ssh_command(ip, username, password, f"ls -li '{filepath}' 2>/dev/null | awk '{{print $1}}'")
    if inode and inode.isdigit():
        return inode
    
    return None

def find_file_recursive(ip, username, password, directory, filename):
    """Search for file recursively in directory"""
    command = f"find '{directory}' -name '{filename}' -type f 2>/dev/null | head -10"
    return run_ssh_command(ip, username, password, command)

def find_file_by_pattern(ip, username, password, directory, pattern):
    """Search for files matching pattern"""
    command = f"find '{directory}' -name '*{pattern}*' -type f 2>/dev/null | head -20"
    return run_ssh_command(ip, username, password, command)

def search_all_backups(ip, username, password):
    """Search for any backup-related files in common locations"""
    commands = [
        "ls -la /var/backups/ 2>/dev/null",
        "ls -la /var/backups/*.bak 2>/dev/null",
        "ls -la /var/backups/*shadow* 2>/dev/null",
        "find /var/backups -name '*.bak' -type f 2>/dev/null | head -20",
        "find /var -name '*shadow*' -type f 2>/dev/null | head -20",
        "find / -name 'shadow.bak' -type f 2>/dev/null | head -10",
        "find / -name '*.bak' -path '*/backups/*' -type f 2>/dev/null | head -20",
    ]
    
    results = {}
    for cmd in commands:
        output = run_ssh_command(ip, username, password, cmd)
        if output:
            key = cmd.split('"')[1] if '"' in cmd else cmd[:50]
            results[key] = output
    return results

def main():
    print("")  # Clean output
    
    # Get inputs
    if len(sys.argv) >= 4:
        target_ip = sys.argv[1]
        directory = sys.argv[2]
        filename = sys.argv[3]
        username = sys.argv[4] if len(sys.argv) >= 5 else "root"
        password = sys.argv[5] if len(sys.argv) >= 6 else ""
    else:
        target_ip = input("Enter Target IP: ").strip()
        directory = input("Enter Directory (e.g., /var/backups): ").strip() or "/var/backups"
        filename = input("Enter Filename (e.g., shadow.bak): ").strip()
        
        if check_ssh_port(target_ip):
            username = input("Enter SSH username (default: root): ").strip() or "root"
            password = input("Enter SSH password: ").strip()
        else:
            print("Error: SSH port 22 is not open on target")
            sys.exit(1)
    
    if not filename:
        print("Error: Please provide a filename")
        sys.exit(1)
    
    print(f"[*] Connected to {target_ip}", file=sys.stderr)
    
    # Step 1: List directory contents
    print(f"[*] Listing contents of {directory}...", file=sys.stderr)
    dir_contents = list_directory(target_ip, username, password, directory)
    if dir_contents:
        print(f"[*] Directory contents:\n{dir_contents}", file=sys.stderr)
    
    # Step 2: Try exact path
    exact_path = f"{directory.rstrip('/')}/{filename}"
    print(f"[*] Checking exact path: {exact_path}", file=sys.stderr)
    inode = get_inode_number(target_ip, username, password, exact_path)
    
    # Step 3: Search recursively in directory
    if not inode:
        print(f"[*] Searching for '{filename}' in {directory}...", file=sys.stderr)
        found_files = find_file_recursive(target_ip, username, password, directory, filename)
        if found_files:
            print(f"[*] Found files:\n{found_files}", file=sys.stderr)
            first_file = found_files.split('\n')[0]
            inode = get_inode_number(target_ip, username, password, first_file)
            if inode:
                print(f"[*] Found at: {first_file}", file=sys.stderr)
    
    # Step 4: Search by pattern (shadow*, *.bak, etc.)
    if not inode:
        print(f"[*] Searching by pattern '*{filename}*'...", file=sys.stderr)
        pattern_files = find_file_by_pattern(target_ip, username, password, directory, filename.replace('.bak', '').replace('.', ''))
        if pattern_files:
            print(f"[*] Pattern matches:\n{pattern_files}", file=sys.stderr)
            first_file = pattern_files.split('\n')[0]
            inode = get_inode_number(target_ip, username, password, first_file)
            if inode:
                print(f"[*] Found at: {first_file}", file=sys.stderr)
    
    # Step 5: Broader search - anywhere in /var or root
    if not inode:
        print(f"[*] Searching entire system for '{filename}'...", file=sys.stderr)
        broad_search = run_ssh_command(target_ip, username, password, f"find / -name '{filename}' -type f 2>/dev/null | head -10")
        if broad_search:
            print(f"[*] Found at:\n{broad_search}", file=sys.stderr)
            first_file = broad_search.split('\n')[0]
            inode = get_inode_number(target_ip, username, password, first_file)
            if inode:
                print(f"[*] Using: {first_file}", file=sys.stderr)
    
    # Step 6: If still not found, show all backup files
    if not inode:
        print(f"[*] '{filename}' not found. Searching for all backup files...", file=sys.stderr)
        all_backups = search_all_backups(target_ip, username, password)
        if all_backups:
            print("[*] All backup-related findings:", file=sys.stderr)
            for cmd_desc, output in all_backups.items():
                if output:
                    print(f"  [{cmd_desc[:60]}]\n  {output}\n", file=sys.stderr)
    
    # Output result
    if inode:
        print(inode)
    else:
        print("0")  # Fallback

if __name__ == "__main__":
    main()
