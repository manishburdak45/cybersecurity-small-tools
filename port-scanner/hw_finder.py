#!/usr/bin/env python3

import socket
import subprocess
import re

def dns_lookup(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except:
        return None

def http_header(ip):
    try:
        result = subprocess.run(
            ["curl", "-I", f"http://{ip}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        for line in result.stdout.split("\n"):
            if "Server:" in line:
                return line.strip()
    except:
        pass
    return None

def nmap_scan(ip):
    try:
        print("[*] Running Nmap scan...\n")

        result = subprocess.run(
            ["nmap", "-sC", "-sV", ip],
            capture_output=True,
            text=True
        )

        output = result.stdout

        # Extract useful info
        running = re.search(r"Running: (.+)", output)
        os_details = re.search(r"OS details: (.+)", output)
        service_info = re.findall(r"(\d+/tcp\s+open\s+\S+\s+.+)", output)

        return running, os_details, service_info

    except Exception as e:
        print(f"[ERROR] Nmap failed: {e}")
        return None, None, None

def main():
    print("="*50)
    print("   🔐 Simple Hardware / OS Finder")
    print("="*50)

    target_ip = input("\nEnter Target IP: ")

    print(f"\n[+] Target: {target_ip}\n")

    # DNS
    print("[*] Checking hostname...")
    hostname = dns_lookup(target_ip)
    if hostname:
        print(f"[+] Hostname: {hostname}")
    else:
        print("[-] No hostname found")

    # HTTP
    print("\n[*] Checking HTTP headers...")
    header = http_header(target_ip)
    if header:
        print(f"[+] {header}")
    else:
        print("[-] No HTTP server info")

    # Nmap
    running, os_details, services = nmap_scan(target_ip)

    print("\n[*] Service Info:")
    if services:
        for s in services:
            print(f"   {s}")
    else:
        print("   No services detected")

    print("\n[*] OS Info:")
    if running:
        print(f"   Running: {running.group(1)}")
    if os_details:
        print(f"   Details: {os_details.group(1)}")

    if not running and not os_details:
        print("   No clear OS info found")

    print("\n" + "="*50)
    print("✅ Scan Complete")
    print("="*50)

if __name__ == "__main__":
    main()
