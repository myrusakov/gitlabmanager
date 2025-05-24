🇷🇺 [Версия на русском](README_RU.md)

# 🐙 GitLab Local Manager

A fully automated system for deploying, backing up, restoring, and managing a local GitLab CE instance using Docker and
Python.

---

## 📌 Features

- 🐳 Docker-based GitLab CE & GitLab Runner setup
- 🛠 Simple CLI interface via `gitlab_manager.py`
- 🔁 Start, stop, restart, and check status of GitLab
- 🧱 Register GitLab Runners via API with PAT
- 📦 Backup and restore GitLab config, secrets, and backups
- ⚙️ `.env`-driven configuration
- 🪟 Windows `.bat` helper scripts

---

## 🗂 Project Structure

```
.
├── .env                    # Environment variables
├── docker-compose.yml     # GitLab and Runner services
├── gitlab_manager.py      # Main CLI script
├── core/                  # Internal modules (backup, restore, etc.)
├── *.bat                  # Windows quick access scripts
└── LICENSE
```

---

## 🚀 Quick Start

```bash
python gitlab_manager.py start            # Start GitLab
python gitlab_manager.py stop             # Stop GitLab
python gitlab_manager.py restart          # Restart GitLab
python gitlab_manager.py status           # Check status
python gitlab_manager.py register_runner  # Register Runner (asks for PAT)
python gitlab_manager.py backup           # Backup GitLab
python gitlab_manager.py restore          # Restore GitLab
```

On Windows, use `*.bat` files for convenience.

---

## ⚙️ Configuration

Everything is controlled from the `.env` file:

```env
# Main Settings
GITLAB_CONTAINER_NAME=gitlab
GITLAB_PROTOCOL=http
GITLAB_HOST=gitlab.local
GITLAB_HTTP_PORT=80
GITLAB_SSH_PORT=2222
GITLAB_REGISTRY_PORT=5050
GITLAB_URL="${GITLAB_PROTOCOL}://${GITLAB_HOST}:${GITLAB_HTTP_PORT}"
GITLAB_REGISTRY_EXTERNAL_URL="${GITLAB_PROTOCOL}://${GITLAB_HOST}:${GITLAB_REGISTRY_PORT}"
GITLAB_PAT=

# GitLab Runner
GITLAB_RUNNER_CONTAINER_NAME=gitlab-runner
GITLAB_RUNNER_DOCKER_IMAGE="node:22"
GITLAB_RUNNER_SETTINGS=concurrent=4,privileged=true,disable_cache=true

# Backup Settings
AUTO_BACKUP=false
BACKUP_DIR=X://MyPrograms/GitLab/backups
```

You can change addresses, ports, backup directory, and Runner settings.
If a Runner is needed, you must provide a Private Access Token in the `GITLAB_PAT` variable with `api` and `admin_mode`
permissions.

**Important:** If using a custom hostname like gitlab.local, add it to your system's hosts file to resolve to 127.0.0.1

---

## 🔐 Runner Registration

Run:

```bash
python gitlab_manager.py register_runner
```

First, create a Private Access Token with `api` and `admin_mode` permissions, then set it in `.env` under `GITLAB_PAT`.

Re-registration is supported with the `--force` flag.

---

## 🧬 Backup Example

```bash
python gitlab_manager.py backup
```

Saves a copy of:

- Backup archive (`.tar`)
- gitlab.rb
- gitlab-secrets.json
- config.toml

Stored in `BACKUP_DIR`, configured via `.env`.

---

## 🔁 Restore Example

```bash
python gitlab_manager.py restore
```

Restores **everything** from backup and reboots GitLab.

---

## 📄 License

[MIT](LICENSE)

Developed by Mikhail Rusakov

---

## Disclaimer

This project is provided "as is" without any warranties, express or implied. The author is not responsible for any data
loss, server downtime, or other issues arising from the use of this tool. Ensure you understand the configuration (e.g.,
`.env`, `hosts` file, Docker setup) and test backups/restore operations in a safe environment before using in
production. Always back up critical data before performing operations like restore.
