import os
from pathlib import Path

from core.utils import fail, run_command, success


def perform_backup(backup_dir, gitlab_container_name, runner_container_name):
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    create_gitlab_backup(gitlab_container_name)

    print("Finding latest backup in container...")
    latest_file = find_latest_container_backup(gitlab_container_name)
    if not latest_file:
        fail("No .tar backups found inside container")
    print(f"Latest container backup: {latest_file}")

    delete_old_container_backups(gitlab_container_name, latest_file)
    local_file = copy_backup_from_container(gitlab_container_name, latest_file, backup_dir)
    delete_old_local_backups(backup_dir, local_file)
    copy_configs_from_container(gitlab_container_name, runner_container_name, backup_dir)

    success("Backup completed successfully!")


def create_gitlab_backup(gitlab_container_name):
    print("Creating new backup in GitLab container...")
    if not run_command(f"docker exec -t {gitlab_container_name} gitlab-backup create"):
        fail("Failed to create backup inside GitLab container")
    success("Backup created successfully inside container")


def find_latest_container_backup(gitlab_container_name):
    return run_command(
        f"docker exec {gitlab_container_name} bash -c \"ls -t /var/opt/gitlab/backups/*.tar | head -n 1\"",
        True
    )


def delete_old_container_backups(gitlab_container_name, keep_file):
    print("Deleting old backups inside container...")
    try:
        run_command(
            f"docker exec {gitlab_container_name} bash -c \"find /var/opt/gitlab/backups -type f -name '*.tar' ! -name '{os.path.basename(keep_file)}' -delete\""
        )
        success("Old container backups deleted successfully")
    except Exception as e:
        fail(f"Error deleting old backups in container: {e}")


def copy_backup_from_container(gitlab_container_name, container_file, backup_dir):
    print("Copying backup archive to local dir...")
    local_file = Path(backup_dir) / os.path.basename(container_file)
    if not run_command(f"docker cp {gitlab_container_name}:{container_file} {local_file}"):
        fail("Failed to copy backup from container")
    return local_file


def delete_old_local_backups(backup_dir, keep_file):
    print("Deleting old local backups...")
    try:
        for file in Path(backup_dir).glob("*.tar"):
            if file.name != os.path.basename(keep_file):
                file.unlink()
    except Exception as e:
        fail(f"Error deleting old backups in local dir: {e}")


def copy_configs_from_container(gitlab_container_name, runner_container_name, backup_dir):
    print("Copying configs and secrets...")
    files = {
        "/etc/gitlab/gitlab.rb": gitlab_container_name,
        "/etc/gitlab/gitlab-secrets.json": gitlab_container_name,
        "/etc/gitlab-runner/config.toml": runner_container_name,
    }
    for file, container in files.items():
        dest_path = Path(backup_dir) / os.path.basename(file)
        if not run_command(f"docker cp {container}:{file} {dest_path}"):
            fail(f"Failed to copy {file} from {container} container")
