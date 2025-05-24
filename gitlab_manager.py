import os
import sys

from core.backup import perform_backup
from core.env import load_dotenv, parse_runner_settings
from core.gitlab_service import show_status, start_gitlab, stop_gitlab
from core.restore import perform_restore
from core.runner_manager import perform_runner_registration
from core.utils import fail

load_dotenv()

GITLAB_CONTAINER_NAME = os.getenv("GITLAB_CONTAINER_NAME")
GITLAB_HOST = os.getenv("GITLAB_HOST")
GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_PAT = os.getenv("GITLAB_PAT")

GITLAB_RUNNER_CONTAINER_NAME = os.getenv("GITLAB_RUNNER_CONTAINER_NAME")
GITLAB_RUNNER_DOCKER_IMAGE = os.getenv("GITLAB_RUNNER_DOCKER_IMAGE")
GITLAB_RUNNER_SETTINGS = parse_runner_settings(os.getenv("GITLAB_RUNNER_SETTINGS"))

AUTO_BACKUP = os.getenv("AUTO_BACKUP").lower() == "true"
BACKUP_DIR = os.getenv("BACKUP_DIR")


def start_with_optional_backup():
    start_gitlab(GITLAB_URL)
    if AUTO_BACKUP:
        backup()


def backup():
    perform_backup(BACKUP_DIR, GITLAB_CONTAINER_NAME, GITLAB_RUNNER_CONTAINER_NAME)


def stop_with_optional_backup():
    if AUTO_BACKUP:
        backup()
    stop_gitlab()


def register_runner():
    perform_runner_registration(GITLAB_URL,
                                GITLAB_HOST,
                                GITLAB_PAT,
                                GITLAB_RUNNER_CONTAINER_NAME,
                                GITLAB_RUNNER_DOCKER_IMAGE,
                                GITLAB_RUNNER_SETTINGS
                                )


def restore():
    perform_restore(BACKUP_DIR, GITLAB_CONTAINER_NAME, GITLAB_RUNNER_CONTAINER_NAME)


commands = {
    "start": start_with_optional_backup,
    "stop": stop_with_optional_backup,
    "restart": lambda: (stop_gitlab(), start_gitlab(GITLAB_URL)),
    "status": lambda: show_status(GITLAB_URL),
    "register_runner": register_runner,
    "backup": backup,
    "restore": restore
}


def main():
    if len(sys.argv) < 2:
        fail(f"Usage: python gitlab_manager.py [{'|'.join(commands.keys())}]")

    command = sys.argv[1].lower()
    if command in commands:
        commands[command]()
    else:
        fail(f"Unknown command: {command}; Available commands: {', '.join(commands.keys())}")


if __name__ == "__main__":
    main()
