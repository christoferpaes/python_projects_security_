import paramiko

# Establish SSH connection with the target machine
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect('target_machine_ip', username='username', password='password')

# Execute commands on the target machine
stdin, stdout, stderr = ssh_client.exec_command('command_to_execute')
print(stdout.read().decode())

# Close the SSH connection
ssh_client.close()
