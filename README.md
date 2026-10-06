# Task Tracker CLI

A simple command line tool to track what you need to do, what you're working on, and what's done.
Pure Python 3 standard library, no dependencies. Tasks are stored in `tasks.json` in the current directory (created automatically).

## Usage

```bash
python3 task_cli.py add "Buy groceries"            # Task added successfully (ID: 1)
python3 task_cli.py update 1 "Buy groceries and cook dinner"
python3 task_cli.py delete 1
python3 task_cli.py mark-in-progress 1
python3 task_cli.py mark-done 1
python3 task_cli.py list                           # all tasks
python3 task_cli.py list todo
python3 task_cli.py list in-progress
python3 task_cli.py list done
```

Optional: use `task-cli` instead of `python3 task_cli.py`:

```bash
chmod +x task_cli.py
ln -s "$(pwd)/task_cli.py" /usr/local/bin/task-cli
```

## Task shape

```json
{
  "id": 1,
  "description": "Buy groceries",
  "status": "todo",
  "createdAt": "2026-10-06T09:24:07",
  "updatedAt": "2026-10-06T09:24:07"
}
```

`status` is one of `todo`, `in-progress`, `done`.

## Error handling

Missing/extra arguments, non-numeric or unknown IDs, empty descriptions, unknown commands/statuses,
and a corrupt `tasks.json` all print a clear message to stderr and exit with code 1.
Writes are atomic (temp file + rename) so the JSON can't be left half-written.

Project URL: https://roadmap.sh/projects/task-tracker
