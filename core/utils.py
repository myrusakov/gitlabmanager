import subprocess
import sys


def fail(message):
    print(f"\033[91mError: {message}\033[0m")
    sys.exit(1)


def success(message):
    print(f"\033[92m{message}\033[0m")


def run_command(command, capture_output=False):
    try:
        if capture_output:
            result = subprocess.check_output(command, shell=True)
            return result.decode().strip() if result else None
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0
    except subprocess.CalledProcessError:
        return None if capture_output else False
