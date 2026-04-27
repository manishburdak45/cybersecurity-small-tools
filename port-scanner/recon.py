import socket

target = input("Enter Target IP: ")

# Common useful ports (HTB friendly)
ports = [21, 22, 25, 53, 80, 110, 139, 143, 443, 445, 8080]

print(f"\n[+] Scanning {target}...\n")

open_found = False

for port in ports:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)

        result = s.connect_ex((target, port))

        if result == 0:
            print(f"[OPEN] Port {port}")
            open_found = True

        s.close()

    except:
        pass

if not open_found:
    print("[-] No open ports found (check VPN or target)")

print("\n✅ Scan Complete")
