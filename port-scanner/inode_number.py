# 🔥 Hacker Banner + Warning
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

    print("\033[1;33m")
    print("[!] Authorized Use Only")
    print("[!] This tool is for educational and ethical cybersecurity purposes.")
    print("[!] Do NOT use on systems without permission.\n")
    print("\033[0m")

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

def get_inode_via_ssh(ip, username, password, directory, filename):
    """Get inode number of a file via SSH"""
    try:
        # Using stat command - most reliable for inode
        # stat -c %i gives inode number
        full_path = f"{directory}/{filename}" if not directory.endswith('/') else f"{directory}{filename}"
        
        # Method 1: Using stat
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "stat -c '%i' '{full_path}' 2>/dev/null" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            inode = result.stdout.strip()
            # Validate it's a number
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

def get_inode_via_python_ssh(ip, username, password, directory, filename):
    """Alternative method using paramiko if available"""
    try:
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)
        
        full_path = f"{directory}/{filename}" if not directory.endswith('/') else f"{directory}{filename}"
        
        # Try stat
        stdin, stdout, stderr = ssh.exec_command(f"stat -c '%i' '{full_path}' 2>/dev/null")
        output = stdout.read().decode().strip()
        if output and output.isdigit():
            ssh.close()
            return output
        
        # Try ls -li
        stdin, stdout, stderr = ssh.exec_command(f"ls -li '{full_path}' 2>/dev/null | awk '{{print $1}}'")
        output = stdout.read().decode().strip()
        if output and output.isdigit():
            ssh.close()
            return output
        
        ssh.close()
    except ImportError:
        pass
    except Exception as e:
        pass
    
    return None

def search_file_in_directory(ip, username, password, directory, filename):
    """Search for file if exact path doesn't work"""
    try:
        # Try to find the file anywhere in the directory
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "find '{directory}' -name '{filename}' -type f 2>/dev/null | head -5" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            found_path = result.stdout.strip().split('\n')[0]
            # Now get inode of found path
            cmd2 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "stat -c '%i' '{found_path}' 2>/dev/null" 2>/dev/null"""
            result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
            if result2.returncode == 0 and result2.stdout.strip():
                inode = result2.stdout.strip()
                if inode.isdigit():
                    return inode, found_path
    except:
        pass
    
    return None, None

def list_dir_contents(ip, username, password, directory):
    """List directory contents for debugging"""
    try:
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "ls -la '{directory}' 2>/dev/null" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except:
        pass
    return None

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
    
    inode = None
    
    # Method 1: Direct stat/ls
    print(f"[*] Getting inode number for {directory}/{filename}...", file=sys.stderr)
    inode = get_inode_via_ssh(target_ip, username, password, directory, filename)
    
    # Method 2: Try with trailing slash variations
    if not inode:
        inode = get_inode_via_ssh(target_ip, username, password, directory.rstrip('/'), filename)
    
    # Method 3: Try full path combined
    if not inode:
        combined_path = f"{directory.rstrip('/')}/{filename}"
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "stat -c '%i' '{combined_path}' 2>/dev/null" 2>/dev/null"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip() and result.stdout.strip().isdigit():
                inode = result.stdout.strip()
        except:
            pass
    
    # Method 4: Search for the file
    if not inode:
        print(f"[*] File not found at exact path. Searching in {directory}...", file=sys.stderr)
        inode, found_path = search_file_in_directory(target_ip, username, password, directory, filename)
        if inode:
            print(f"[*] Found at: {found_path}", file=sys.stderr)
    
    # Method 5: Try paramiko
    if not inode:
        inode = get_inode_via_python_ssh(target_ip, username, password, directory, filename)
    
    # Output result
    if inode:
        print(inode)
    else:
        print(f"[!] Could not find inode for {filename} in {directory}", file=sys.stderr)
        # Debug: show directory contents
        contents = list_dir_contents(target_ip, username, password, directory)
        if contents:
            print(f"[*] Directory contents:\n{contents}", file=sys.stderr)
        print("0")  # Fallback

if __name__ == "__main__":
    main()
