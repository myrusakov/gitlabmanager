import json
import os
import re
import sys
import urllib.parse
import urllib.request

from .utils import fail, run_command, success


def runner_already_registered(gitlab_runner_config_file):
    return os.path.exists(gitlab_runner_config_file)


def delete_runner_config(gitlab_runner_config_file):
    if os.path.exists(gitlab_runner_config_file):
        os.remove(gitlab_runner_config_file)
        success("Old Runner config removed.")


def get_registration_token(pat, gitlab_url):
    url = f"{gitlab_url}/api/v4/user/runners"
    headers = {
        "PRIVATE-TOKEN": pat,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = urllib.parse.urlencode({
        "runner_type": "instance_type",
        "description": "auto-runner",
        "run_untagged": "true"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read()
            result = json.loads(response_data.decode("utf-8"))
            return result.get("token")
    except Exception as e:
        fail(f"Failed to retrieve REGISTRATION_TOKEN: {e}")
        return None


def register_runner(token, gitlab_host, gitlab_url, gitlab_runner_docker_image):
    command = [
        "docker", "exec", "gitlab-runner", "gitlab-runner", "register",
        "--non-interactive",
        "--name", "DockerRunner",
        "--url", gitlab_url,
        "--token", token,
        "--executor", "docker",
        "--docker-image", gitlab_runner_docker_image,
        "--docker-extra-hosts", f"{gitlab_host}:host-gateway"
    ]
    return run_command(command)


def extract_runner_id_from_config(gitlab_runner_config_file):
    if not os.path.exists(gitlab_runner_config_file):
        return None
    try:
        with open(gitlab_runner_config_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("id ="):
                    match = re.match(r'id\s*=\s*(\d+)', line)
                    if match:
                        return int(match.group(1))
    except Exception as e:
        fail(f"Warning: Failed to read runner ID from config: {e}")
    return None


def delete_runner_by_id(pat, runner_id, gitlab_url):
    url = f"{gitlab_url}/api/v4/runners/{runner_id}"
    headers = {
        "PRIVATE-TOKEN": pat
    }
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 204:
                success(f"Deleted runner with ID {runner_id} from GitLab.")
                return True
            else:
                fail(f"Failed to delete runner. Status: {response.status}")
    except Exception as e:
        fail(f"Error while deleting runner: {e}")
    return False


def perform_runner_registration(gitlab_host, gitlab_url, gitlab_runner_config_file, gitlab_runner_docker_image):
    force = "--force" in sys.argv

    if runner_already_registered(gitlab_runner_config_file) and not force:
        fail(
            f"Runner is already registered (found: {os.path.normpath(gitlab_runner_config_file)}).\n"
            f"Use '--force' to re-register and remove existing runner."
        )

    pat = input("Enter your Personal Access Token for GitLab API: ").strip()
    if not pat:
        fail("Personal Access Token is required.")

    if runner_already_registered(gitlab_runner_config_file):
        runner_id = extract_runner_id_from_config(gitlab_runner_config_file)
        if runner_id:
            delete_runner_by_id(pat, runner_id, gitlab_url)
        else:
            fail("No matching runner found in GitLab.")
        delete_runner_config(gitlab_runner_config_file)

    print("Requesting registration token from GitLab...")
    registration_token = get_registration_token(pat, gitlab_url)
    if not registration_token:
        fail("Failed to obtain registration token from GitLab.")

    print("Registering GitLab Runner...")
    if register_runner(registration_token, gitlab_host, gitlab_url, gitlab_runner_docker_image):
        if runner_already_registered(gitlab_runner_config_file):
            success("GitLab Runner registered successfully!")
        else:
            fail("Runner registration executed, but config.toml not found.")
    else:
        fail("GitLab Runner registration failed.")
