import os
import shutil
import stat
from pathlib import Path

from core.utils import fail, run_command, success


def find_single_backup_file(backup_dir):
    tar_files = list(Path(backup_dir).glob("*.tar"))
    if len(tar_files) == 0:
        fail(f"No .tar backup files found in {backup_dir}")
    if len(tar_files) > 1:
        fail(f"Expected exactly one .tar file in {backup_dir}, found {len(tar_files)}")
    return tar_files[0]


def extract_backup_id(backup_file):
    return backup_file.name.replace("_gitlab_backup.tar", "")


def copy_tree(src, dst, label):
    src_path = Path(src)
    dst_path = Path(dst)
    try:
        if dst_path.exists():
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        success(f"{label} copied")
    except Exception as e:
        fail(f"Failed to copy {label}: {e}")


def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    try:
        func(path)
    except Exception as e:
        print(f"Could not remove {path}: {e}")


def perform_restore(
        gitlab_container_name,
        gitlab_app_dir,
        backup_backups_dir,
        gitlab_backups_dir,
        backup_config_dir,
        gitlab_config_dir,
        backup_secrets_dir,
        gitlab_secrets_dir,
        start_gitlab_fn,
        stop_gitlab_fn
):
    print("Looking for backup archive...")
    backup_file = find_single_backup_file(backup_backups_dir)
    backup_id = extract_backup_id(backup_file)
    print(f"Found backup: {backup_file.name}, ID: {backup_id}")

    stop_gitlab_fn()

    if os.path.exists(gitlab_app_dir):
        print("Removing GitLab app data directory...")
        shutil.rmtree(gitlab_app_dir, onerror=remove_readonly)

    print("Restoring backup file...")
    copy_tree(backup_backups_dir, gitlab_backups_dir, "Backup")

    print("Restoring configuration directory...")
    copy_tree(backup_config_dir, gitlab_config_dir, "Configuration")

    print("Restoring secrets directory...")
    copy_tree(backup_secrets_dir, gitlab_secrets_dir, "Secrets")

    start_gitlab_fn()

    print("Setting backup and SSH permissions...")
    run_command(f"docker exec {gitlab_container_name} chown git:git /var/opt/gitlab/backups/{backup_file.name}")
    run_command(f"docker exec {gitlab_container_name} chmod 600 /etc/gitlab/ssh_host_rsa_key")
    run_command(f"docker exec {gitlab_container_name} chmod 600 /etc/gitlab/ssh_host_ecdsa_key")
    run_command(f"docker exec {gitlab_container_name} chmod 600 /etc/gitlab/ssh_host_ed25519_key")
    run_command(f"docker exec {gitlab_container_name} chown git:git /etc/gitlab/ssh_host_rsa_key")
    run_command(f"docker exec {gitlab_container_name} chown git:git /etc/gitlab/ssh_host_ecdsa_key")
    run_command(f"docker exec {gitlab_container_name} chown git:git /etc/gitlab/ssh_host_ed25519_key")

    print("Stopping Unicorn and Sidekiq...")
    run_command(f"docker exec {gitlab_container_name} gitlab-ctl stop unicorn")
    run_command(f"docker exec {gitlab_container_name} gitlab-ctl stop sidekiq")

    print("Restoring from backup...")
    if not run_command(
            f"docker exec {gitlab_container_name} bash -c \"GITLAB_ASSUME_YES=1 gitlab-backup restore BACKUP={backup_id}\""):
        fail("Restore failed")

    print("Restarting GitLab...")
    stop_gitlab_fn()
    start_gitlab_fn()

    success("Restore completed successfully.")
