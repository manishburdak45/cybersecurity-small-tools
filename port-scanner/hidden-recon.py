#!/usr/bin/env python3
"""
Universal Hidden File Finder via SSH
Input 1: Target IP Address
Input 2: File/Keyword to search (e.g., history, bashrc, ssh, config)
Output: Hidden file name only (REAL result only)
"""

import socket
import subprocess
import sys
import os

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


def check_ssh_port(ip, timeout=2):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, 22))
        sock.close()
        return result == 0
    except:
        return False


def run_ssh_command(ip, username, password, command, timeout=10):
    try:
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "{command}" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None


def find_hidden_file_ssh(ip, username, password, keyword):
    # Search in home directories (fast + relevant)
    find_cmd = f"""find /home -maxdepth 4 -type f -name ".*{keyword}*" 2>/dev/null | head -5"""
    output = run_ssh_command(ip, username, password, find_cmd)
    
    if output:
        files = output.split('\n')
        return os.path.basename(files[0])

    return None


def check_common_hidden_files(ip, username, password, keyword):
    common_files = {
        'history': ['.bash_history', '.zsh_history'],
        'bashrc': ['.bashrc', '.bash_profile'],
        'ssh': ['.ssh/id_rsa', '.ssh/authorized_keys'],
        'config': ['.config', '.gitconfig'],
    }

    for cat, files in common_files.items():
        if keyword.lower() in cat:
            for f in files:
                check_cmd = f"""test -f /home/*/{f} && echo "{f}" """
                output = run_ssh_command(ip, username, password, check_cmd)
                if output:
                    return output.strip()

    return None


def search_all_users(ip, username, password, keyword):
    # FIXED: correct variable (target_ip bug removed)
    user_list = run_ssh_command(ip, username, password, "ls /home/")
    
    if user_list:
        users = user_list.split('\n')
        for user in users:
            cmd = f"""find /home/{user} -type f -name ".*{keyword}*" 2>/dev/null | head -3"""
            output = run_ssh_command(ip, username, password, cmd)
            if output:
                files = output.split('\n')
                return os.path.basename(files[0])

    return None


def main():
    hacker_banner()

    if len(sys.argv) >= 3:
        target_ip = sys.argv[1]
        keyword = sys.argv[2]
        username = sys.argv[3] if len(sys.argv) >= 4 else "root"
        password = sys.argv[4] if len(sys.argv) >= 5 else ""
    else:
        target_ip = input("Enter Target IP: ").strip()
        keyword = input("Enter file/keyword to find (e.g., history, bashrc, ssh): ").strip()

        if check_ssh_port(target_ip):
            username = input("Enter SSH username (default: root): ").strip() or "root"
            password = input("Enter SSH password: ").strip()
        else:
            print("[-] SSH port 22 is not open")
            sys.exit(1)

    if not keyword:
        print("[-] Please provide a keyword")
        sys.exit(1)

    result = None

    print(f"[*] Searching for '{keyword}'...", file=sys.stderr)

    # Method 1
    result = find_hidden_file_ssh(target_ip, username, password, keyword)

    # Method 2
    if not result:
        result = check_common_hidden_files(target_ip, username, password, keyword)

    # Method 3
    if not result:
        result = search_all_users(target_ip, username, password, keyword)

    # ✅ FINAL OUTPUT (NO FAKE RESULT)
    if result:
        print(result)
    else:
        print("[-] No matching hidden file found")


if __name__ == "__main__":
    main()
