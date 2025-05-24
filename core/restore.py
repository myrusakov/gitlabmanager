import os
from pathlib import Path

from core.utils import fail, run_command, success


def perform_restore(backup_dir, gitlab_container_name, gitlab_runner_container_name):
    backup_dir = Path(backup_dir)

    print(f"Finding latest backup in {backup_dir}...")
    backup_file = find_latest_local_backup(backup_dir)
    if not backup_file:
        fail(f"No backup .tar file found in {backup_dir}")
    print(f"Using backup: {backup_file.name}")

    copy_backup_to_container(backup_file, gitlab_container_name)

    stop_gitlab_services(gitlab_container_name)
    start_gitlab_service("postgresql", gitlab_container_name)
    start_gitlab_service("redis", gitlab_container_name)
    start_gitlab_service("gitaly", gitlab_container_name)

    restore_backup_in_container(backup_file, gitlab_container_name)
    restore_config_files(backup_dir, gitlab_container_name, gitlab_runner_container_name)
    reconfigure_and_start_gitlab(gitlab_container_name)

    success("Backup, configs and secrets restored successfully!")


def find_latest_local_backup(backup_dir):
    tar_files = sorted(Path(backup_dir).glob("*.tar"), key=os.path.getmtime, reverse=True)
    return tar_files[0] if tar_files else None


def stop_gitlab_services(gitlab_container_name):
    print("Stopping GitLab services...")
    if not run_command(f"docker exec {gitlab_container_name} gitlab-ctl stop"):
        fail("Failed to stop GitLab services")


def start_gitlab_service(service_name, gitlab_container_name):
    print(f"Starting {service_name} service...")
    if not run_command(f"docker exec {gitlab_container_name} gitlab-ctl start {service_name}"):
        fail(f"Failed to start {service_name} service inside container")


def copy_backup_to_container(backup_file, gitlab_container_name):
    print(f"Copying backup {backup_file.name} into container...")
    if not run_command(f"docker cp {backup_file} {gitlab_container_name}:/var/opt/gitlab/backups/"):
        fail(f"Failed to copy backup {backup_file} into container")
    success(f"Backup {backup_file.name} copied to container")


def restore_backup_in_container(backup_file, gitlab_container_name):
    backup_timestamp = backup_file.name.replace("_gitlab_backup.tar", "")
    print(f"Restoring backup {backup_file.name} inside container...")
    if not run_command(
            f"docker exec {gitlab_container_name} bash -c \"GITLAB_ASSUME_YES=1 gitlab-backup restore BACKUP={backup_timestamp}\""
    ):
        fail(f"Failed to restore backup {backup_file.name}")


def restore_config_files(backup_dir, gitlab_container_name, gitlab_runner_container_name):
    print("Restoring gitlab.rb and gitlab-secrets.json...")
    files = {
        "gitlab.rb": (gitlab_container_name, "/etc/gitlab/gitlab.rb"),
        "gitlab-secrets.json": (gitlab_container_name, "/etc/gitlab/gitlab-secrets.json"),
        "config.toml": (gitlab_runner_container_name, "/etc/gitlab-runner/config.toml"),
    }
    for file, (container, dest_path) in files.items():
        local_file = Path(backup_dir) / file
        if not local_file.exists():
            fail(f"{file} not found in backup directory: {backup_dir}")
        if not run_command(f"docker cp {local_file} {container}:{dest_path}"):
            fail(f"Failed to restore {file} into {container} container at {dest_path}")

    success("Configuration files restored successfully")


def reconfigure_and_start_gitlab(gitlab_container_name):
    print("Reconfiguring GitLab...")
    if not run_command(f"docker exec {gitlab_container_name} gitlab-ctl reconfigure"):
        fail("Failed to reconfigure GitLab after restore")
    print("Starting GitLab services...")
    if not run_command(f"docker exec {gitlab_container_name} gitlab-ctl start"):
        fail("Failed to start GitLab services")
