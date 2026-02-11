#!/usr/bin/env python3
import json
import os
import sys
import argparse
from datetime import datetime

BACKLOG_FILE = "coding_backlog.json"
STATE_FILE = "coding_state.json"

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def init(args):
    backlog = {"project_name": args.name, "tasks": []}
    state = {"status": "discovery", "current_task_id": None, "last_heartbeat": None}
    save_json(BACKLOG_FILE, backlog)
    save_json(STATE_FILE, state)
    print(f"Initialized {args.name}")

def add_task(args):
    backlog = load_json(BACKLOG_FILE, {"tasks": []})
    task_id = len(backlog["tasks"]) + 1
    new_task = {
        "id": task_id,
        "title": args.title,
        "description": args.desc,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "priority": args.priority or "medium"
    }
    backlog["tasks"].append(new_task)
    save_json(BACKLOG_FILE, backlog)
    print(f"Added task {task_id}: {args.title}")

def get_next(args):
    backlog = load_json(BACKLOG_FILE, {"tasks": []})
    for task in backlog["tasks"]:
        if task["status"] == "pending":
            print(json.dumps(task))
            return
    print("None")

def update_status(args):
    backlog = load_json(BACKLOG_FILE, {"tasks": []})
    for task in backlog["tasks"]:
        if task["id"] == int(args.id):
            task["status"] = args.status
            save_json(BACKLOG_FILE, backlog)
            print(f"Updated task {args.id} to {args.status}")
            return
    print(f"Task {args.id} not found")

def get_summary(args):
    backlog = load_json(BACKLOG_FILE, {"tasks": []})
    state = load_json(STATE_FILE, {})
    pending = [t for t in backlog["tasks"] if t["status"] == "pending"]
    completed = [t for t in backlog["tasks"] if t["status"] == "completed"]
    in_progress = [t for t in backlog["tasks"] if t["status"] == "in-progress"]
    
    summary = {
        "project": backlog.get("project_name", "Unknown"),
        "counts": {
            "pending": len(pending),
            "in_progress": len(in_progress),
            "completed": len(completed)
        },
        "state": state
    }
    print(json.dumps(summary))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    p_init = subparsers.add_parser("init")
    p_init.add_argument("name")
    p_init.set_defaults(func=init)

    p_add = subparsers.add_parser("add")
    p_add.add_argument("title")
    p_add.add_argument("--desc", default="")
    p_add.add_argument("--priority")
    p_add.set_defaults(func=add_task)

    p_next = subparsers.add_parser("next")
    p_next.set_defaults(func=get_next)

    p_update = subparsers.add_parser("update")
    p_update.add_argument("id")
    p_update.add_argument("status")
    p_update.set_defaults(func=update_status)

    p_summary = subparsers.add_parser("summary")
    p_summary.set_defaults(func=get_summary)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
