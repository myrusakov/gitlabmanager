import subprocess
import sys


def fail(message):
    print(f"\033[91mError: {message}\033[0m")
    sys.exit(1)


def success(message):
    print(f"\033[92m{message}\033[0m")


def run_command(command):
    result = subprocess.run(command, shell=True)
    return result.returncode == 0
