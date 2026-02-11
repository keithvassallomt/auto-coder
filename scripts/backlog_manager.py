#!/usr/bin/env python3
import json
import os
import sys
import argparse
from datetime import datetime

BACKLOG_FILE = "coding_backlog.json"
STATE_FILE = "coding_state.json"
VALID_STATUSES = {"pending", "in-progress", "completed", "failed"}


def resolve_path(args, filename):
    base = getattr(args, "project_dir", None) or "."
    return os.path.join(base, filename)


def load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default


def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def init(args):
    backlog = {"project_name": args.name, "tasks": []}
    state = {"status": "discovery", "current_task_id": None, "last_heartbeat": None}
    save_json(resolve_path(args, BACKLOG_FILE), backlog)
    save_json(resolve_path(args, STATE_FILE), state)
    print(f"Initialized {args.name}")


def add_task(args):
    bp = resolve_path(args, BACKLOG_FILE)
    backlog = load_json(bp, {"tasks": []})
    priority = args.priority or "medium"
    if priority not in ("high", "medium", "low"):
        print(f"Invalid priority: {priority}. Must be high, medium, or low.", file=sys.stderr)
        sys.exit(1)
    task_id = next_id(backlog["tasks"])
    new_task = {
        "id": task_id,
        "title": args.title,
        "description": args.desc,
        "status": "pending",
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "log": [],
    }
    backlog["tasks"].append(new_task)
    save_json(bp, backlog)
    print(f"Added task {task_id}: {args.title}")


def get_next(args):
    bp = resolve_path(args, BACKLOG_FILE)
    backlog = load_json(bp, {"tasks": []})
    for task in backlog["tasks"]:
        if task["status"] == "pending":
            print(json.dumps(task))
            return
    print("None")


def start_task(args):
    bp = resolve_path(args, BACKLOG_FILE)
    sp = resolve_path(args, STATE_FILE)
    backlog = load_json(bp, {"tasks": []})
    state = load_json(sp, {})
    task = find_task(backlog["tasks"], int(args.id))
    if not task:
        print(f"Task {args.id} not found", file=sys.stderr)
        sys.exit(1)
    if task["status"] != "pending":
        print(f"Task {args.id} is '{task['status']}', expected 'pending'", file=sys.stderr)
        sys.exit(1)
    task["status"] = "in-progress"
    task["started_at"] = datetime.now().isoformat()
    state["current_task_id"] = task["id"]
    state["status"] = "executing"
    save_json(bp, backlog)
    save_json(sp, state)
    print(f"Started task {args.id}: {task['title']}")


def complete_task(args):
    bp = resolve_path(args, BACKLOG_FILE)
    sp = resolve_path(args, STATE_FILE)
    backlog = load_json(bp, {"tasks": []})
    state = load_json(sp, {})
    task = find_task(backlog["tasks"], int(args.id))
    if not task:
        print(f"Task {args.id} not found", file=sys.stderr)
        sys.exit(1)
    if task["status"] != "in-progress":
        print(f"Task {args.id} is '{task['status']}', expected 'in-progress'", file=sys.stderr)
        sys.exit(1)
    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()
    if state.get("current_task_id") == task["id"]:
        state["current_task_id"] = None
    save_json(bp, backlog)
    save_json(sp, state)
    print(f"Completed task {args.id}: {task['title']}")


def fail_task(args):
    bp = resolve_path(args, BACKLOG_FILE)
    sp = resolve_path(args, STATE_FILE)
    backlog = load_json(bp, {"tasks": []})
    state = load_json(sp, {})
    task = find_task(backlog["tasks"], int(args.id))
    if not task:
        print(f"Task {args.id} not found", file=sys.stderr)
        sys.exit(1)
    task["status"] = "failed"
    task.setdefault("log", []).append({
        "timestamp": datetime.now().isoformat(),
        "message": f"FAILED: {args.reason}",
    })
    if state.get("current_task_id") == task["id"]:
        state["current_task_id"] = None
    save_json(bp, backlog)
    save_json(sp, state)
    print(f"Failed task {args.id}: {args.reason}")


def reopen_task(args):
    bp = resolve_path(args, BACKLOG_FILE)
    backlog = load_json(bp, {"tasks": []})
    task = find_task(backlog["tasks"], int(args.id))
    if not task:
        print(f"Task {args.id} not found", file=sys.stderr)
        sys.exit(1)
    if task["status"] not in ("completed", "failed"):
        print(f"Task {args.id} is '{task['status']}', can only reopen completed or failed tasks", file=sys.stderr)
        sys.exit(1)
    task["status"] = "pending"
    task["started_at"] = None
    task["completed_at"] = None
    save_json(bp, backlog)
    print(f"Reopened task {args.id}: {task['title']}")


def log_task(args):
    bp = resolve_path(args, BACKLOG_FILE)
    backlog = load_json(bp, {"tasks": []})
    task = find_task(backlog["tasks"], int(args.id))
    if not task:
        print(f"Task {args.id} not found", file=sys.stderr)
        sys.exit(1)
    task.setdefault("log", []).append({
        "timestamp": datetime.now().isoformat(),
        "message": args.msg,
    })
    save_json(bp, backlog)
    print(f"Logged to task {args.id}")


def update_status(args):
    if args.status not in VALID_STATUSES:
        print(f"Invalid status: {args.status}. Must be one of: {', '.join(sorted(VALID_STATUSES))}", file=sys.stderr)
        sys.exit(1)
    bp = resolve_path(args, BACKLOG_FILE)
    backlog = load_json(bp, {"tasks": []})
    task = find_task(backlog["tasks"], int(args.id))
    if not task:
        print(f"Task {args.id} not found", file=sys.stderr)
        sys.exit(1)
    task["status"] = args.status
    save_json(bp, backlog)
    print(f"Updated task {args.id} to {args.status}")


def list_tasks(args):
    bp = resolve_path(args, BACKLOG_FILE)
    backlog = load_json(bp, {"tasks": []})
    tasks = backlog["tasks"]
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    if not tasks:
        print("No tasks found.")
        return
    for t in tasks:
        priority = t.get("priority", "medium")
        print(f"  [{t['status']:>11}] #{t['id']}  ({priority})  {t['title']}")


def get_summary(args):
    bp = resolve_path(args, BACKLOG_FILE)
    sp = resolve_path(args, STATE_FILE)
    backlog = load_json(bp, {"tasks": []})
    state = load_json(sp, {})
    counts = {}
    for status in VALID_STATUSES:
        counts[status] = len([t for t in backlog["tasks"] if t["status"] == status])

    summary = {
        "project": backlog.get("project_name", "Unknown"),
        "total": len(backlog["tasks"]),
        "counts": counts,
        "state": state,
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Coder backlog manager")
    parser.add_argument("--project-dir", default=None, help="Project root directory (defaults to current directory)")
    subparsers = parser.add_subparsers()

    p_init = subparsers.add_parser("init", help="Initialize backlog and state files")
    p_init.add_argument("name")
    p_init.set_defaults(func=init)

    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("title")
    p_add.add_argument("--desc", default="")
    p_add.add_argument("--priority", choices=["high", "medium", "low"])
    p_add.set_defaults(func=add_task)

    p_next = subparsers.add_parser("next", help="Get the next pending task")
    p_next.set_defaults(func=get_next)

    p_start = subparsers.add_parser("start", help="Mark a task as in-progress")
    p_start.add_argument("id")
    p_start.set_defaults(func=start_task)

    p_complete = subparsers.add_parser("complete", help="Mark a task as completed")
    p_complete.add_argument("id")
    p_complete.set_defaults(func=complete_task)

    p_fail = subparsers.add_parser("fail", help="Mark a task as failed")
    p_fail.add_argument("id")
    p_fail.add_argument("--reason", required=True)
    p_fail.set_defaults(func=fail_task)

    p_reopen = subparsers.add_parser("reopen", help="Reopen a completed or failed task")
    p_reopen.add_argument("id")
    p_reopen.set_defaults(func=reopen_task)

    p_log = subparsers.add_parser("log", help="Append a note to a task")
    p_log.add_argument("id")
    p_log.add_argument("--msg", required=True)
    p_log.set_defaults(func=log_task)

    p_update = subparsers.add_parser("update", help="Directly set task status (prefer start/complete/fail)")
    p_update.add_argument("id")
    p_update.add_argument("status")
    p_update.set_defaults(func=update_status)

    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument("--status", choices=sorted(VALID_STATUSES))
    p_list.set_defaults(func=list_tasks)

    p_summary = subparsers.add_parser("summary", help="Get backlog summary stats")
    p_summary.set_defaults(func=get_summary)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
