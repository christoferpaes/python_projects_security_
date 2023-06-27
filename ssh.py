import subprocess

def create_ssh_tunnel(local_port, remote_host, remote_port, ssh_host, ssh_port, ssh_user):
    # SSH command to create the tunnel
    ssh_command = [
        'ssh',
        '-L',
        f'{local_port}:{remote_host}:{remote_port}',
        '-p',
        str(ssh_port),
        f'{ssh_user}@{ssh_host}'
    ]

    # Start the SSH tunnel subprocess
    tunnel_process = subprocess.Popen(ssh_command)

    # Wait for the tunnel process to complete
    tunnel_process.wait()

# Example usage
create_ssh_tunnel(8080, 'localhost', 80, 'example.com', 22, 'username')
