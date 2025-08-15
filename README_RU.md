🇬🇧 [English version](README.md)

# 🐙 Менеджер локального GitLab

Полностью автоматизированная система для развёртывания, резервного копирования, восстановления и управления локальной
GitLab CE с помощью Docker и Python.

---

## 📌 Возможности

- 🐳 Развёртывание GitLab CE и GitLab Runner через Docker
- 🛠 Удобный CLI-интерфейс через `gitlab_manager.py`
- 🔁 Управление: запуск, остановка, перезапуск и проверка статуса GitLab
- 🧱 Регистрация Runner'ов через API GitLab с использованием Personal Access Token (PAT)
- 📦 Резервное копирование и восстановление конфигурации, секретов и бэкапов GitLab
- ⚙️ Гибкая настройка через файл `.env`
- 🪟 Вспомогательные `.bat`-файлы для пользователей Windows

---

## 🗂 Структура проекта

```
.
├── .env                   # Переменные окружения
├── docker-compose.yml     # Сервисы GitLab и Runner
├── gitlab_manager.py      # Основной CLI-скрипт
├── core/                  # Внутренние модули (бэкап, восстановление и т.д.)
├── *.bat                  # Быстрые скрипты для Windows
└── LICENSE
```

---

## 🚀 Быстрый старт

```bash
python gitlab_manager.py start            # Запуск GitLab
python gitlab_manager.py stop             # Остановка GitLab
python gitlab_manager.py restart          # Перезапуск GitLab
python gitlab_manager.py status           # Проверка статуса GitLab
python gitlab_manager.py register_runner  # Регистрация Runner'а (требуется PAT)
python gitlab_manager.py backup           # Создание резервной копии GitLab
python gitlab_manager.py restore          # Восстановление GitLab из резервной копии
```

В Windows можно использовать `.bat`-файлы для удобства.

---

## ⚙️ Конфигурация

Всё настраивается в файле `.env`:

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

Можно изменить адреса, порты, директорию для бэкапов, настройки для Runner.
Если необходим Runner, то потребуется указать Private Access Token в переменной `GITLAB_PAT` с правами `api` и
`admin_mode`.

**Важно:** Если используется кастомный хост, например gitlab.local, добавьте его в файл hosts системы, чтобы он
адресовался в 127.0.0.1

---

## 🔐 Регистрация Runner'а

Выполните:

```bash
python gitlab_manager.py register_runner
```

Предварительно создайте Private Access Token с правами `api` и `admin_mode`, после чего укажите его в `.env` в
переменной
`GITLAB_PAT`.

Повторная регистрация поддерживается с флагом `--force`.

---

## 🧬 Пример резервного копирования

```bash
python gitlab_manager.py backup
```

Сохраняются:

- Архив с бэкапом (`.tar`)
- gitlab.rb
- gitlab-secrets.json
- config.toml

Все данные сохраняются в директорию `BACKUP_DIR`, указанную в `.env`.

---

## 🔁 Пример восстановления

```bash
python gitlab_manager.py restore
```

Восстанавливает **всё** из резервной копии и перезапускает GitLab.

---

## 📄 Лицензия

[MIT](LICENSE)

Разработано Михаилом Русаковым, 2025

---

## Отказ от ответственности

Этот проект предоставляется "как есть" без каких-либо гарантий, явных или подразумеваемых. Автор не несёт
ответственности за потерю данных, простои сервера или другие проблемы, связанные с использованием инструмента.
Убедитесь, что вы понимаете настройки (например, `.env`, файл `hosts`, конфигурацию Docker) и протестируйте операции
бэкапа/восстановления в безопасной среде перед использованием в продакшене. Всегда создавайте резервные копии важных
данных перед выполнением операций, таких как восстановление.
