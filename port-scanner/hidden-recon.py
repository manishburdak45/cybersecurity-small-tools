#!/usr/bin/env python3
"""
Universal Hidden File Finder via SSH
Input 1: Target IP Address
Input 2: File/Keyword to search (e.g., history, bashrc, ssh, config)
Output: Hidden file name only (e.g., .bash_history)
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


def find_hidden_file_ssh(ip, username, password, keyword):
    
    find_cmd = f"""find /home -maxdepth 3 -name ".*{keyword}*" -type f 2>/dev/null | head -5"""
    
    try:
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "{find_cmd}" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            files = result.stdout.strip().split('\n')
            return os.path.basename(files[0])
        
    except:
        pass
    return None


def list_hidden_files_ssh(ip, username, password):
    
    list_cmd = """ls -la /home/*/ 2>/dev/null | grep "^-.*\." | awk '{print $NF}'"""
    
    try:
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "{list_cmd}" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')
    except:
        pass
    return None


def search_specific_user_hidden_file(ip, username, password, target_user, keyword):
    
    find_cmd = f"""find /home/{target_user} -maxdepth 2 -name ".*{keyword}*" -type f 2>/dev/null | head -5"""
    
    try:
        cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "{find_cmd}" 2>/dev/null"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            files = result.stdout.strip().split('\n')
            return os.path.basename(files[0])
        
        find_cmd2 = f"""find /home/{target_user} -name ".*{keyword}*" -type f 2>/dev/null | head -5"""
        cmd2 = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "{find_cmd2}" 2>/dev/null"""
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
        
        if result2.returncode == 0 and result2.stdout.strip():
            files = result2.stdout.strip().split('\n')
            return os.path.basename(files[0])
            
    except:
        pass
    return None


def check_common_hidden_files(ip, username, password, keyword):
    
    common_files = {
        'history': ['.bash_history', '.zsh_history', '.history', '.sh_history'],
        'bashrc': ['.bashrc', '.bash_profile', '.bash_login'],
        'ssh': ['.ssh/id_rsa', '.ssh/authorized_keys', '.ssh/config', '.ssh/known_hosts'],
        'config': ['.config', '.gitconfig', '.vimrc', '.tmux.conf'],
        'profile': ['.profile', '.bash_profile', '.zprofile'],
        'password': ['.passwd', '.password', '.secret', '.credentials'],
        'token': ['.token', '.auth', '.cred', '.key'],
        'local': ['.local', '.cache', '.mozilla'],
        'vim': ['.vimrc', '.viminfo', '.vim'],
        'git': ['.gitconfig', '.git-credentials', '.gitignore']
    }
    
    for cat, files in common_files.items():
        if keyword.lower() in cat.lower() or cat.lower() in keyword.lower():
            for f in files:
                check_cmd = f"""test -f /home/*/{f} && echo "{f}" 2>/dev/null"""
                try:
                    cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip} "{check_cmd}" 2>/dev/null"""
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except:
                    continue
    
    return None


def main():
    hacker_banner()  # 🔥 Added (only change)

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
            print("Error: SSH port 22 is not open on target")
            sys.exit(1)
    
    if not keyword:
        print("Error: Please provide a keyword to search")
        sys.exit(1)
    
    result = None
    
    print(f"[*] Searching for hidden file matching '{keyword}'...", file=sys.stderr)
    result = find_hidden_file_ssh(target_ip, username, password, keyword)
    
    if not result:
        result = check_common_hidden_files(target_ip, username, password, keyword)
    
    if not result:
        user_cmd = """ls /home/ 2>/dev/null"""
        try:
            cmd = f"""sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{target_ip} "{user_cmd}" 2>/dev/null"""
            user_result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            if user_result.returncode == 0 and user_result.stdout.strip():
                users = user_result.stdout.strip().split('\n')
                for user in users:
                    result = search_specific_user_hidden_file(target_ip, username, password, user, keyword)
                    if result:
                        break
        except:
            pass
    
    if result:
        print(result)
    else:
        print(f".{keyword}")


if __name__ == "__main__":
    main()
