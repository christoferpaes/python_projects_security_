import subprocess
import keyboard

def send_packets(ip_address):
    hping_command = f"hping3 {ip_address} -d 65535 -c 0"
    process = subprocess.Popen(hping_command, shell=True)

    while True:
        if keyboard.is_pressed('esc'):
            process.terminate()
            break

if __name__ == "__main__":
    ip_address = input("Enter the IP address to send packets: ")
    print("Press the 'esc' key to stop sending packets.")
    send_packets(ip_address)

