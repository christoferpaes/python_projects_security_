import os
import socket
import struct
import random

ICMP_ECHO_REQUEST = 8  # ICMP message type for Echo Request

def create_icmp_socket():
    try:
        icmp = socket.getprotobyname("icmp")
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        return sock
    except socket.error as e:
        print("Failed to create socket. Error: %s" % e)
        exit(1)

def send_icmp_packet(sock, dest_addr, data):
    # Generate a random ICMP identifier and sequence number
    icmp_id = random.randint(0, 65535)
    icmp_seq = random.randint(0, 65535)
    
    # Calculate ICMP checksum
    checksum = 0
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, checksum, icmp_id, icmp_seq)
    checksum = calculate_checksum(header + data)
    
    # Create ICMP packet
    packet = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, checksum, icmp_id, icmp_seq) + data
    
    # Send ICMP packet
    try:
        sock.sendto(packet, (dest_addr, 1))
    except socket.error as e:
        print("Failed to send ICMP packet. Error: %s" % e)

def receive_icmp_packet(sock):
    try:
        packet, addr = sock.recvfrom(1024)
        return packet
    except socket.error as e:
        print("Failed to receive ICMP packet. Error: %s" % e)

def extract_data_from_packet(packet):
    # Extract data from the ICMP packet
    data = packet[28:]
    return data

def calculate_checksum(data):
    # Calculate the ICMP checksum
    checksum = 0
    count_to = (len(data) // 2) * 2

    for count in range(0, count_to, 2):
        this_val = data[count + 1] * 256 + data[count]
        checksum += this_val
        checksum &= 0xffffffff

    if count_to < len(data):
        checksum += data[count_to]
        checksum &= 0xffffffff

    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    result = ~checksum
    result &= 0xffff
    result = result >> 8 | (result << 8 & 0xff00)
    return result

def main():
    host = "127.0.0.1"  # Destination IP address
    data = b"Hello, World!"  # Data to be sent through the tunnel

    sock = create_icmp_socket()

    send_icmp_packet(sock, host, data)
    packet = receive_icmp_packet(sock)
    received_data = extract_data_from_packet(packet)

    print("Received Data:", received_data)

if __name__ == "__main__":
    main()
