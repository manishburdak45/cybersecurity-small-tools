import socket

target = input("Enter Target IP: ")

# Increase port range
ports = range(1, 1001)   # 1–1000 scan

print(f"\n[+] Scanning {target}...\n")

for port in ports:
    print(f"Checking port {port}")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        result = s.connect_ex((target, port))

        if result == 0:
            print(f"\n[OPEN] Port {port}")

        s.close()

    except Exception as e:
        print(f"[ERROR] {e}")

print("\n✅ Scan Complete")
