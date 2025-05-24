import json
import sys
import urllib.parse
import urllib.request

from core.utils import fail, run_command, success


def perform_runner_registration(gitlab_url,
                                gitlab_host,
                                gitlab_pat,
                                gitlab_runner_container_name,
                                gitlab_runner_docker_image,
                                gitlab_runner_settings):
    if not gitlab_pat:
        fail(
            "Personal Access Token is required. Create a PAT with api and admin_node permissions, then specify it in the .env file.")
    print("Using the PAT specified in .env")

    runner_ids = get_registered_runners(gitlab_url, gitlab_pat)
    if runner_ids:
        if "--force" in sys.argv:
            delete_runners(runner_ids, gitlab_url, gitlab_pat, gitlab_runner_container_name)
        else:
            success(f"Found {len(runner_ids)} registered runner(s): {runner_ids}")
            success("Use '--force' to remove all and re-register.")
            return

    print("Requesting registration token from GitLab...")
    registration_token = get_registration_token(gitlab_url, gitlab_pat)
    if not registration_token:
        fail("Failed to obtain registration token from GitLab.")

    print("Registering GitLab Runner...")
    if register_runner(registration_token, gitlab_url, gitlab_host, gitlab_runner_docker_image):
        configure_runner(gitlab_runner_container_name, gitlab_runner_settings)
        success("GitLab Runner registered successfully!")
    else:
        fail("GitLab Runner registration failed.")


def get_registered_runners(gitlab_url, gitlab_pat):
    data = gitlab_api_request(gitlab_url, gitlab_pat, "GET", "runners/all")
    return [runner["id"] for runner in data] if data else []


def gitlab_api_request(gitlab_url, gitlab_pat, method, endpoint, data=None):
    url = f"{gitlab_url}/api/v4/{endpoint}"
    headers = {"PRIVATE-TOKEN": gitlab_pat}

    encoded_data = None
    if data is not None:
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")

    request = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status in (200, 201):
                content = response.read()
                return json.loads(content.decode("utf-8")) if content else None
            elif response.status in (204,):
                return None
            else:
                fail(f"GitLab API error {response.status} on {method} {endpoint}")
    except Exception as e:
        fail(f"GitLab API request failed: {e}")
    return None


def delete_runners(runner_ids, gitlab_url, gitlab_pat, gitlab_runner_container_name):
    for runner_id in runner_ids:
        delete_runner_by_id(runner_id, gitlab_url, gitlab_pat)
    delete_runner_config(gitlab_runner_container_name)


def delete_runner_by_id(runner_id, gitlab_url, gitlab_pat):
    gitlab_api_request(gitlab_url, gitlab_pat, "DELETE", f"runners/{runner_id}")
    success(f"Deleted runner with ID {runner_id} from GitLab.")


def delete_runner_config(gitlab_runner_container_name):
    config_path = "/etc/gitlab-runner/config.toml"
    command = ["docker", "exec", gitlab_runner_container_name, "rm", "-f", config_path]
    if run_command(command):
        success(f"Old Runner config removed inside container: {config_path}")
    else:
        fail(f"Failed to remove Runner config inside container: {config_path}")


def get_registration_token(gitlab_url, gitlab_pat):
    data = gitlab_api_request(gitlab_url, gitlab_pat, "POST", "user/runners", {
        "runner_type": "instance_type",
        "description": "auto-runner",
        "run_untagged": "true"
    })
    return data.get("token") if data else None


def register_runner(token, gitlab_url, gitlab_host, gitlab_runner_docker_image):
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


def configure_runner(gitlab_runner_container_name, gitlab_runner_settings):
    config_path = "/etc/gitlab-runner/config.toml"
    sed_commands = []
    for key, value in gitlab_runner_settings.items():
        sed_commands.append(f"s/{key}.*/{key} = {value}/")

    sed_command = " && ".join([f"sed -i '{cmd}' {config_path}" for cmd in sed_commands])

    run_command([
        "docker", "exec", gitlab_runner_container_name,
        "sh", "-c",
        sed_command
    ])
    run_command(["docker", "restart", gitlab_runner_container_name])
    success(f"Runner config updated: {gitlab_runner_settings}")
