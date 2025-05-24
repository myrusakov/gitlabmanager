import os
import shutil
from pathlib import Path

from core.utils import fail, run_command, success


def find_latest_backup(gitlab_backups_dir):
    tar_files = sorted(Path(gitlab_backups_dir).glob("*.tar"), key=os.path.getmtime, reverse=True)
    return tar_files[0] if tar_files else None


def delete_old_backups(gitlab_backups_dir, keep_file):
    try:
        for file in Path(gitlab_backups_dir).glob("*.tar"):
            if file != keep_file:
                os.remove(file)

        for subdir in Path(gitlab_backups_dir).iterdir():
            if subdir.is_dir():
                shutil.rmtree(subdir)
    except Exception as e:
        fail(f"Error deleting old backups: {e}")


def copy_mirror(src, dst, label, exclude_dirs=None):
    def ignore_dirs(directory, files):
        if not exclude_dirs:
            return []
        exclude_paths = {Path(d).resolve() for d in exclude_dirs}
        return [file for file in files if (Path(directory) / file).resolve() in exclude_paths]

    try:
        src_path = Path(src)
        dst_path = Path(dst)
        if dst_path.exists():
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path, ignore=ignore_dirs, dirs_exist_ok=True)
        success(f"{label} copied (mirror)")
    except Exception as e:
        fail(f"Error copying {label}: {e}")


def perform_backup(
        gitlab_container_name,
        gitlab_base_dir,
        backup_base_dir,
        gitlab_backups_dir,
        backup_backups_dir,
        gitlab_config_dir,
        backup_config_dir,
        gitlab_secrets_dir,
        backup_secrets_dir,
        gitlab_app_dir
):
    print("Creating a new backup inside the container...")
    if not run_command(f"docker exec -t {gitlab_container_name} gitlab-backup create"):
        fail("Failed to create backup")

    print("Finding the latest backup...")
    latest = find_latest_backup(gitlab_backups_dir)
    if not latest:
        fail(f"No .tar backups found in {gitlab_backups_dir}")
    print(f"Latest backup: {latest.name}")

    print("Cleaning old backups...")
    delete_old_backups(gitlab_backups_dir, latest)

    print("Copying scripts and files...")
    copy_mirror(gitlab_base_dir, backup_base_dir, "Scripts and files", exclude_dirs=[gitlab_app_dir])

    print("Copying backups...")
    copy_mirror(gitlab_backups_dir, backup_backups_dir, "Backups")

    print("Copying configuration...")
    copy_mirror(gitlab_config_dir, backup_config_dir, "Configuration")

    print("Copying secrets...")
    copy_mirror(gitlab_secrets_dir, backup_secrets_dir, "Secrets")

    success("Backup completed successfully.")
