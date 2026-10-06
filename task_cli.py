#!/usr/bin/env python3
"""Task Tracker CLI - manage tasks from the command line.

Tasks are stored in tasks.json in the current working directory.
Uses only the Python standard library.
"""
import json
import os
import sys
from datetime import datetime

DB_FILE = "tasks.json"
STATUSES = ("todo", "in-progress", "done")

USAGE = """Usage: task-cli <command> [arguments]

Commands:
  add <description>             Add a new task
  update <id> <description>     Update a task's description
  delete <id>                   Delete a task
  mark-in-progress <id>         Mark a task as in progress
  mark-done <id>                Mark a task as done
  list [todo|in-progress|done]  List all tasks, or filter by status
"""


def fail(message, show_usage=False):
    """Print an error to stderr and exit with a non-zero code."""
    print(f"Error: {message}", file=sys.stderr)
    if show_usage:
        print("\n" + USAGE, file=sys.stderr)
    sys.exit(1)


def now():
    return datetime.now().isoformat(timespec="seconds")


def save_tasks(tasks):
    """Write atomically so a crash can't leave a half-written file."""
    tmp = DB_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DB_FILE)
    except OSError as e:
        fail(f"could not write {DB_FILE}: {e}")


def load_tasks():
    """Load tasks, creating the JSON file if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        save_tasks([])
        return []
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        fail(f"{DB_FILE} is not valid JSON. Fix or delete it and try again.")
    except OSError as e:
        fail(f"could not read {DB_FILE}: {e}")
    if not isinstance(data, list):
        fail(f"{DB_FILE} has an unexpected format (expected a list).")
    return data


def parse_id(raw):
    try:
        task_id = int(raw)
    except ValueError:
        fail(f"'{raw}' is not a valid task ID (must be a number).")
    if task_id < 1:
        fail("task ID must be a positive number.")
    return task_id


def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    fail(f"no task found with ID {task_id}.")


def next_id(tasks):
    # max + 1 keeps IDs unique (an ID can be reused only if the highest one was deleted)
    return max((t["id"] for t in tasks), default=0) + 1


# ---------- commands ----------

def cmd_add(args):
    if len(args) != 1 or not args[0].strip():
        fail('usage: add "<description>"')
    tasks = load_tasks()
    timestamp = now()
    task = {
        "id": next_id(tasks),
        "description": args[0].strip(),
        "status": "todo",
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {task['id']})")


def cmd_update(args):
    if len(args) != 2 or not args[1].strip():
        fail('usage: update <id> "<new description>"')
    tasks = load_tasks()
    task = find_task(tasks, parse_id(args[0]))
    task["description"] = args[1].strip()
    task["updatedAt"] = now()
    save_tasks(tasks)
    print(f"Task {task['id']} updated successfully")


def cmd_delete(args):
    if len(args) != 1:
        fail("usage: delete <id>")
    tasks = load_tasks()
    task = find_task(tasks, parse_id(args[0]))
    tasks.remove(task)
    save_tasks(tasks)
    print(f"Task {task['id']} deleted successfully")


def set_status(args, status, command):
    if len(args) != 1:
        fail(f"usage: {command} <id>")
    tasks = load_tasks()
    task = find_task(tasks, parse_id(args[0]))
    task["status"] = status
    task["updatedAt"] = now()
    save_tasks(tasks)
    print(f"Task {task['id']} marked as {status}")


def cmd_mark_in_progress(args):
    set_status(args, "in-progress", "mark-in-progress")


def cmd_mark_done(args):
    set_status(args, "done", "mark-done")


def cmd_list(args):
    if len(args) > 1:
        fail("usage: list [todo|in-progress|done]")
    status_filter = args[0] if args else None
    if status_filter and status_filter not in STATUSES:
        fail(f"unknown status '{status_filter}'. Choose from: {', '.join(STATUSES)}.")

    tasks = load_tasks()
    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    if not tasks:
        print("No tasks found.")
        return
    for t in tasks:
        print(f"[{t['id']}] {t['description']}")
        print(f"     status: {t['status']} | created: {t['createdAt']} | updated: {t['updatedAt']}")


COMMANDS = {
    "add": cmd_add,
    "update": cmd_update,
    "delete": cmd_delete,
    "mark-in-progress": cmd_mark_in_progress,
    "mark-done": cmd_mark_done,
    "list": cmd_list,
}


def main(argv):
    if not argv:
        fail("no command given.", show_usage=True)
    command, args = argv[0], argv[1:]
    handler = COMMANDS.get(command)
    if handler is None:
        fail(f"unknown command '{command}'.", show_usage=True)
    handler(args)


if __name__ == "__main__":
    main(sys.argv[1:])
