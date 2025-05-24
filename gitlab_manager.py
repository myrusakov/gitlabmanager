import os
import sys

from core.backup import perform_backup
from core.env import load_dotenv
from core.gitlab_service import show_status, start_gitlab, stop_gitlab
from core.restore import perform_restore
from core.runner_manager import perform_runner_registration
from core.utils import fail

load_dotenv()

GITLAB_CONTAINER_NAME = os.getenv("GITLAB_CONTAINER_NAME")
GITLAB_BASE_DIR = os.getenv("GITLAB_BASE_DIR")
BACKUP_BASE_DIR = os.getenv("BACKUP_BASE_DIR")
GITLAB_BACKUPS_DIR = os.getenv("GITLAB_BACKUPS_DIR")
BACKUP_BACKUPS_DIR = os.getenv("BACKUP_BACKUPS_DIR")
GITLAB_CONFIG_DIR = os.getenv("GITLAB_CONFIG_DIR")
BACKUP_CONFIG_DIR = os.getenv("BACKUP_CONFIG_DIR")
GITLAB_SECRETS_DIR = os.getenv("GITLAB_SECRETS_DIR")
BACKUP_SECRETS_DIR = os.getenv("BACKUP_SECRETS_DIR")
GITLAB_APP_DIR = os.getenv("GITLAB_APP_DIR")
GITLAB_HOST = os.getenv("GITLAB_HOST")
GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_RUNNER_CONFIG_FILE = os.getenv("GITLAB_RUNNER_CONFIG_FILE")
GITLAB_RUNNER_DOCKER_IMAGE = os.getenv("GITLAB_RUNNER_DOCKER_IMAGE")
AUTO_BACKUP = os.getenv("AUTO_BACKUP").lower() == "true"


def start_with_optional_backup():
    start_gitlab(GITLAB_URL)
    if AUTO_BACKUP:
        backup()


def backup():
    perform_backup(
        GITLAB_CONTAINER_NAME,
        GITLAB_BASE_DIR,
        BACKUP_BASE_DIR,
        GITLAB_BACKUPS_DIR,
        BACKUP_BACKUPS_DIR,
        GITLAB_CONFIG_DIR,
        BACKUP_CONFIG_DIR,
        GITLAB_SECRETS_DIR,
        BACKUP_SECRETS_DIR,
        GITLAB_APP_DIR
    )


def stop_with_optional_backup():
    if AUTO_BACKUP:
        backup()
    stop_gitlab()


def register_runner():
    perform_runner_registration(GITLAB_HOST,
                                GITLAB_URL,
                                GITLAB_RUNNER_CONFIG_FILE,
                                GITLAB_RUNNER_DOCKER_IMAGE
                                )


def restore():
    perform_restore(
        GITLAB_CONTAINER_NAME,
        GITLAB_APP_DIR,
        BACKUP_BACKUPS_DIR,
        GITLAB_BACKUPS_DIR,
        BACKUP_CONFIG_DIR,
        GITLAB_CONFIG_DIR,
        BACKUP_SECRETS_DIR,
        GITLAB_SECRETS_DIR,
        lambda: start_gitlab(GITLAB_URL),
        stop_gitlab
    )


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
