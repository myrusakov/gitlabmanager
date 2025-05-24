import time
import urllib.error
import urllib.request

from core.utils import fail, run_command, success


def start_gitlab(gitlab_url):
    print("Starting GitLab...")
    if not run_command("docker-compose up -d"):
        fail("Failed to start GitLab")
    print("Waiting for GitLab to start (this may take 2-5 minutes)...")
    wait_for_gitlab(gitlab_url)


def wait_for_gitlab(gitlab_url):
    max_attempts = 60  # ~10 minutes
    attempt = 0
    while attempt < max_attempts:
        try:
            with urllib.request.urlopen(gitlab_url, timeout=15) as response:
                if response.status < 400:
                    success(f"GitLab is running at {gitlab_url}!")
                    return
        except:
            print(f"Waiting for GitLab... (Attempt {attempt + 1}/{max_attempts})")
            time.sleep(10)
        attempt += 1
    fail(f"GitLab failed to start after {max_attempts} attempts. Check Docker logs or network settings.")


def stop_gitlab():
    print("Stopping GitLab...")
    if not run_command("docker-compose down"):
        fail("Failed to stop GitLab")
    success("GitLab stopped successfully.")


def show_status(gitlab_url):
    print("Checking GitLab status...")
    try:
        with urllib.request.urlopen(gitlab_url, timeout=10):
            success(f"GitLab is running at {gitlab_url}")
    except Exception as e:
        fail(f"GitLab is not responding. Reason: {e}")
