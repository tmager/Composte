import os, sys
import subprocess

def version():
    here = os.path.basename(__file__)

    p = subprocess.Popen(["git", "log", "-1"], stdout = subprocess.PIPE)

    with p.stdout:
        hash_ = p.stdout.readline().decode().split(" ")[-1]

    return hash_.strip()

if __name__ == "__main__":
    print(version())

