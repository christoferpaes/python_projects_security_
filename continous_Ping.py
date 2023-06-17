from pythonping import ping
import keyboard
import threading

class PingThread(threading.Thread):
    def __init__(self, ip_address):
        threading.Thread.__init__(self)
        self.ip_address = ip_address
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            response_list = ping(self.ip_address)
            if response_list.rtt_avg_ms:
                print(f"Ping to {self.ip_address}: {response_list.rtt_avg_ms} ms")
            else:
                print(f"Unable to ping {self.ip_address}")

def ping_ip(ip_address):
    threads = []
    while True:
        thread = PingThread(ip_address)
        threads.append(thread)
        thread.start()

        if keyboard.is_pressed('esc'):
            for thread in threads:
                thread.stop_event.set()
                thread.join()
            break

if __name__ == "__main__":
    ip_address = input("Enter the IP address to ping: ")
    print("Press the 'esc' key to stop pinging.")
    ping_ip(ip_address)
