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
GITLAB_CONTAINER_NAME=gitlab
GITLAB_PROTOCOL=http
GITLAB_HOST=gitlab.local
GITLAB_HTTP_PORT=80
GITLAB_SSH_PORT=2222
...
```

You can change data/backup paths, ports, and image versions.

**Important:** If using a custom hostname like gitlab.local, add it to your system's hosts file to resolve to 127.0.0.1

---

## 🔐 Runner Registration

Run:

```bash
python gitlab_manager.py register_runner
```

You will be asked to provide a Personal Access Token. Supports automatic re-registration with `--force` flag.

---

## 🧬 Backup Example

```bash
python gitlab_manager.py backup
```

Saves a copy of:

- Backups archive (`.tar`)
- GitLab config
- GitLab secrets
- Runner configs

Stored in `BACKUP_BASE_DIR`, configured via `.env`.

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
