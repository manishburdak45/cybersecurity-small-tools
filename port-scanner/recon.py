import socket

target = input("Enter Target IP: ")

ports = [21, 22, 80, 443, 8080]

print(f"\n[+] Scanning {target}...\n")

for port in ports:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)

        result = s.connect_ex((target, port))

        if result == 0:
            print(f"[OPEN] Port {port}")

            try:
                banner = s.recv(1024).decode().strip()
                print(f"   ↳ {banner}")
            except:
                print("   ↳ No banner")

        s.close()

    except Exception as e:
        print(f"[ERROR] {e}")

print("\n✅ Scan Complete")
