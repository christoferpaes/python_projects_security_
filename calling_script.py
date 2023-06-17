import subprocess
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the path to start the worm.")
    else:
        worm_script = "worm.py"
        path = sys.argv[1]
        subprocess.call(["python", worm_script, path])
