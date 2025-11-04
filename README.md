# Shell emulator - Medium

Консольная оболочка с файловыми командами на Python.

## Возможности

### Базовые команды
* `ls [path]` - список файлов и каталогов; опция `-l` для подробного отображения
* `cd <path>` - переход в каталог; поддержка `~` для домашнего каталога и `..` для родительского
* `cat <file>` - вывод содержимого файла
* `cp <source> <dest>` - копирование файлов/каталогов; опция `-r` для рекурсивного копирования
* `mv <source> <dest>` - перемещение/переименование файлов и каталогов
* `rm <path>` - удаление файлов; опция `-r` для рекурсивного удаления каталогов (требует подтверждения)

### Расширенные возможности (Medium)
* Архивы: `zip <folder> <archive.zip>`, `unzip <archive.zip>`, `tar <folder> <archive.tar>`, `untar <archive.tar>`
* Поиск: `grep <pattern> <path>` с опциями `-r` (рекурсивно) и `-i` (без учёта регистра)
* История: `history` - просмотр истории команд, `undo` - отмена последней операции (`cp`, `mv`, `rm`)

### Логирование
* Все команды и ошибки записываются в файл `logs/shell.log`
* Формат: `[YYYY-MM-DD HH:MM:SS] [LEVEL] module: message`

## Примеры

```
F:\Dev\shell-commands-emulator> ls -l
Name         Perms    Links  Size  Modified           Created
src          rwxr-xr-x  1   4096  2025-01-15 10:30:22  2025-01-15 10:30:22
...

F:\Dev\shell-commands-emulator> cd src
F:\Dev\shell-commands-emulator\src> cat main.py
from src.shell import Shell
...

F:\Dev\shell-commands-emulator\src> grep -r "def execute" .
commands/base.py:5:    def execute(self, cmd: ParsedCommand, ctx: Context):

F:\Dev\shell-commands-emulator> history
1: 15 Jan 10:30: ls -l
2: 15 Jan 10:31: cd src
3: 15 Jan 10:32: cat main.py
```

## Установка и запуск

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt

python -m src.main
```

## Структура проекта

```
.
├── src/
│   ├── main.py              # точка входа
│   ├── shell.py             # основной цикл оболочки
│   ├── config.py            # конфигурация и константы
│   ├── core/
│   │   ├── parser.py        # парсинг команд
│   │   ├── validator.py     # валидация команд
│   │   ├── dispatcher.py    # диспетчеризация команд
│   │   ├── models.py         # модели данных
│   │   ├── services.py      # контекст (текущий каталог, история)
│   │   └── errors.py        # исключения
│   ├── commands/
│   │   ├── base.py          # базовый класс Command
│   │   ├── navigation.py    # cd
│   │   ├── listing.py       # ls, cat
│   │   ├── filesystem.py    # cp, mv, rm
│   │   ├── archive.py        # zip, unzip, tar, untar
│   │   ├── search.py        # grep
│   │   └── history.py       # history, undo
│   └── utils/
│       ├── log_utils.py     # настройка логирования
│       ├── path_utils.py    # разрешение путей
│       └── misc_utils.py    # вспомогательные функции
├── tests/                   # тесты
└── logs/
    └── shell.log            # журнал команд
```

## Тесты

```bash
pytest --disable-warnings --cov=src --cov-report=term-missing
```

## Код-стайл и типы

* PEP8/ruff: `ruff check`
* Типы (mypy): `mypy src`
