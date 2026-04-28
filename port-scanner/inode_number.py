This code is not working so new code is upload soon 

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

# 🔥 ONLY ADDITION (nothing else changed)
def hacker_banner():
    print("\033[1;32m")
    print(r"""
███╗   ███╗     ██████╗██╗   ██╗██████╗ ███████╗██████╗ 
████╗ ████║    ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██╔████╔██║    ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║╚██╔╝██║    ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
██║ ╚═╝ ██║    ╚██████╗   ██║   ██████╔╝███████╗██║  ██║
╚═╝     ╚═╝     ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝

                m_cyber264
""")
    print("\033[0m")


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

def get_inode_via_ssh(ip, username, password, directory, filename):
    """Get inode number of a file via SSH"""
    try:
        full_path = f"{directory.rstrip('/')}/{filename}"
        
        # Method 1: Using stat
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "stat -c '%i' '{full_path}' 2>/dev/null" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            inode = result.stdout.strip()
            if inode.isdigit():
                return inode
        
        # Method 2: Using ls -li
        cmd2 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "ls -li '{full_path}' 2>/dev/null | awk '{{print \\$1}}'" 2>/dev/null"""
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
        
        if result2.returncode == 0 and result2.stdout.strip():
            inode = result2.stdout.strip()
            if inode.isdigit():
                return inode
        
        # Method 3: Using find with printf
        cmd3 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "find '{directory}' -name '{filename}' -printf '%i' 2>/dev/null" 2>/dev/null"""
        result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True, timeout=10)
        
        if result3.returncode == 0 and result3.stdout.strip():
            inode = result3.stdout.strip()
            if inode.isdigit():
                return inode
                
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        pass
    
    return None

def search_file_in_directory(ip, username, password, directory, filename):
    """Search for file if exact path doesn't work"""
    try:
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "find '{directory}' -name '{filename}' -type f 2>/dev/null | head -5" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            found_path = result.stdout.strip().split('\n')[0]
            cmd2 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "stat -c '%i' '{found_path}' 2>/dev/null" 2>/dev/null"""
            result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
            if result2.returncode == 0 and result2.stdout.strip():
                inode = result2.stdout.strip()
                if inode.isdigit():
                    return inode, found_path
    except:
        pass
    
    return None, None

def main():
    hacker_banner()  # 🔥 ONLY THIS LINE ADDED

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
    
    inode = None
    
    # Method 1: Direct stat/ls
    print(f"[*] Getting inode number for {directory}/{filename}...", file=sys.stderr)
    inode = get_inode_via_ssh(target_ip, username, password, directory, filename)
    
    # Method 2: Try with trailing slash handled properly
    if not inode:
        directory_clean = directory.rstrip('/')
        inode = get_inode_via_ssh(target_ip, username, password, directory_clean, filename)
    
    # Method 3: Search for the file if not found at exact path
    if not inode:
        print(f"[*] File not found at exact path. Searching in {directory}...", file=sys.stderr)
        inode, found_path = search_file_in_directory(target_ip, username, password, directory, filename)
        if inode:
            print(f"[*] Found at: {found_path}", file=sys.stderr)
    
    # Output result
    if inode:
        print(inode)
    else:
        # Last resort: try listing directory
        cmd_list = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{target_ip} "ls -la '{directory}' 2>/dev/null" 2>/dev/null"""
        try:
            result = subprocess.run(cmd_list, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print(f"[*] Directory contents:\n{result.stdout}", file=sys.stderr)
        except:
            pass
        print("0")  # Fallback

if __name__ == "__main__":
    main()
