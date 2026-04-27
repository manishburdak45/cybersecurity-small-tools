import socket

target = input("Enter Target IP: ")

ports = [21, 22, 80, 443, 8080]

print(f"\nScanning {target}...\n")

for port in ports:
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect((target, port))

        print(f"[+] Port {port} OPEN")

        try:
            banner = s.recv(1024).decode().strip()
            print(f"    ↳ Service Info: {banner}")
        except:
            print("    ↳ No banner received")

        s.close()

    except:
        pass

print("\nScan Complete ✅")
