---
name: auto-coder
description: A never-ending, autonomous software development loop. Manages a project from initial spec Q&A through task breakdown, execution via sub-agents, and proactive feature brainstorming. Use when a user wants to start a coding project and just have the AI 'do it'.
license: MIT
metadata:
  author: Keith Vassallo
  version: "1.0"
compatibility: Designed for OpenClaw agents. Requires Python, configured 'coder' agent.
---

# Auto Coder

This skill implements a perpetual development cycle. It ensures that projects don't stall by integrating with the OpenClaw heartbeat system.

---

## Assumptions

1. You are working within OpenClaw. You have access to OpenClaw system tools including file I/O, shell execution, web search, messaging, and the `sessions_spawn` API for spawning sub-agents.
2. OpenClaw is running a heartbeat every ~30 minutes. During this heartbeat, you must check the status of the backlog (see below) and continue coding, coming up with new features, or updating the user. Failing to carry out at least one of these three tasks per heartbeat is a critical failure.
3. The user is communicating with you via a messaging client (Telegram, WhatsApp, etc.). Do not give the user links to local files they can't open. When starting a development server, ensure it is bound to LAN IPs, not `localhost`, otherwise the user can't see the result.
4. You have access to spawn coding agents using robust AI coding models. Ideally, the user has set up an agent in their `openclaw.json` file called `coder`, which specifies a coding model to use. If this is missing, inform the user and help them create it.

> **On first run**, verify all of the above. If anything is missing, inform the user.

---

## Workflow

### Step 1 — User Request

1. The user will ask for something to be created which requires coding. Since Auto Coder is not suitable for all situations, you must confirm with the user whether or not they want to use Auto Coder — unless their original request specifically mentions Auto Coder by name.
2. Once confirmed, proceed to Discovery Mode.

### Step 2 — Discovery Mode

1. **Expand the Request** — Ask the user to elaborate on their initial request with more detail. Clarify the scope, target audience, and core functionality of the project they want to build.

2. **Grill the User** — Do not accept the spec at face value. Ask 3–5 sharp, technical questions to fill in gaps. You MUST cover ALL of the following areas:
   - **Tech Stack** — Which languages, frameworks, and tools to use for both frontend and backend (e.g., Java, Python, React, Svelte, FastAPI, SQLite).
   - **Platform** — Desired front-end platform (web, desktop, mobile) and deployment target.
   - **Data Model** — What are the core entities and their relationships? What data needs to be stored, and how should it be structured?
   - **Edge Cases** — What happens on invalid input, network failure, empty states, or concurrent access? Identify at least 2 edge cases relevant to the project.
   - **Auth & Access** — Does the project need authentication or authorization? If so, what kind (e.g., session-based, JWT, OAuth)?

   Additionally, ask any other project-specific questions that would prevent ambiguity during implementation.

3. **Tech Research** — Proactively search for the latest stable versions of libraries and frameworks mentioned in the spec (e.g., Vite, Tailwind, FastAPI). Ensure the project uses modern, non-deprecated patterns. Unless the user specifies a version, you MUST:
   - Run a web search to discover the latest stable version of each technology, library, or framework being used.
   - Record the version number and ensure it will be used in the final project.

### Step 3 — Planning Mode

1. **Create Project Folder** — Create a folder for this project in the OpenClaw workspace.
2. **Init Git** — Run `git init` within this folder.
3. **Init Backlog** — Run `python3 scripts/backlog_manager.py init "<project_name>"`.
4. **Write Spec** — Write a `SPEC.md` file in the project root containing the finalized project specification from Discovery Mode. This is the single source of truth for what is being built.
5. **Domain Contract** *(mandatory)* — Create a `CONTRACT.md` in the project root. This file must define the **Semantic Assertions** and **Product Rules** for the project — non-negotiable truths the software must uphold. Examples:
   - *"Users must be logged in to access /dashboard"*
   - *"Guest users must never see Admin buttons"*
   - *"All API responses must include appropriate error codes"*

   No task can be added to the backlog without its corresponding semantic rule being recorded here.
6. **Intent Recording** — For every task added to the backlog, record the **Intended User Experience** in plain English. This acts as the behavioral reference for the auditor.
7. **Init Changelog** — Create a `CHANGELOG.md` in the project root. Use [Keep a Changelog](https://keepachangelog.com/) format with an `## [Unreleased]` section. This file will be updated after every successful task completion.
8. **Create Backlog** — Break the project spec into discrete tasks. Create the backlog using `scripts/backlog_manager.py add`.
9. **Coding Agent Setup** — Ensure an agent called `coder` is configured in `openclaw.json` with appropriate models and fallbacks. If it is missing, inform the user and help them create it. The `auto-coder` skill will target this agent for all execution and audit tasks.
10. **Install Dependencies** — Install the project's dependencies based on the chosen tech stack (e.g., `npm install`, `pip install -r requirements.txt`, `cargo build`). Ensure the project compiles/resolves cleanly before any tasks begin.
11. **Register Heartbeat** *(mandatory)* — Add an entry in `HEARTBEAT.md` in the OpenClaw workspace. Include:
    - Instructions to check the backlog for this project (per Step 4).
    - The absolute path of the project.
    - The path to the `skills/` folder for auto-coder.

    Failing to do this means the heartbeat system will not pick up this project.

### Step 4 — Execution Mode

This mode applies in two situations:

- Planning Mode (Step 3) has just been concluded, and you will now start coding.
- You are returning to this skill after a heartbeat.

**Steps:**

1. **Pick Task** — Run `scripts/backlog_manager.py next` to get the top pending task.
2. **Claim Task** — Run `scripts/backlog_manager.py start <id>` to mark it as `in-progress` and record it as the current task in state.
3. **Spawn Sub-agent** — Use the OpenClaw `sessions_spawn` API to create a sub-agent targeting the `coder` agent.
4. **Instruct** — Tell the sub-agent to use the built-in `coding-agent` skill to complete the specific task in the project directory.

### Step 5 — Verification Mode *(mandatory)*

1. **Verify** — After the sub-agent finishes, run a verification step (e.g., `npm run lint`, `npm run build`, `pytest`, or `ruff check`) to catch errors and maintain code quality. Run as many checks as possible.

2. **Audit** — Spawn a separate sub-agent targeting the `coder` agent to audit the task completion:
   - **Contract Validation** — The auditor MUST read `CONTRACT.md` and verify that the implementation does not violate any semantic assertions.
   - **Behavioral Check** — The auditor must verify that the feature is not just coded, but integrated and functional.
   - **Expectation Check** — If API credentials or configurations are provided, the auditor must verify that the resulting data is present and non-empty (if applicable).
   - Inform the user of the audit result. Also verify that the task the agent claimed to complete has actually been implemented. If not, re-spawn an agent with the current task.

3. **Correction** *(max 3 retries)* — If verification or audit fails (including Contract violations), re-spawn a sub-agent with the failure details to fix the errors. You may retry up to **3 times** per task. If the task still fails after 3 attempts, mark it as failed and pause — notify the user with the failure details and ask how to proceed.

4. **Git Commit** — After successful verification and audit:
   - **Update Changelog** — Append an entry to `CHANGELOG.md` under the `## [Unreleased]` section describing what was added, changed, or fixed. Use the appropriate sub-heading (`Added`, `Changed`, `Fixed`, `Removed`) per Keep a Changelog conventions.
   - Commit the changes (including the changelog update) with a descriptive message referencing the task ID and title (e.g., `git commit -m "Task #4: Implement user login form"`).

5. **Update State** — Run `scripts/backlog_manager.py complete <id>` only after successful verification, a passing audit, and a committed change. If the task exhausted all retries, use `scripts/backlog_manager.py fail <id> --reason "<explanation>"`.

6. **Inform the User** — Tell the user what was accomplished, which audits were run, and the status of each. Also inform them how they can check on progress (e.g., provide a URL, show them how to run a desktop app, etc.).

---

## Execution Protocol *(mandatory)*

- **No Asking for Permission** — If there are tasks in the backlog, execute them. Do not end a turn by asking "Should I start?" or "Ready to proceed?".
- **Proactive Continuation** — After a task passes audit, immediately pick up the next task.
- **Zero Theatrics** — Skip the "I am starting now" or "I am your engineer" fluff. Just provide the status of the current run or the results of the audit.
- **Audit Is Law** — If a task fails audit, it is NOT complete. Re-spawn the sub-agent with the audit findings and fix it (up to the 3-retry limit defined in Verification Mode). Never report a failed task as "done".

---

## User Communication *(mandatory)*

- **Do Not Spam** — If you have many things to tell the user, prepare one coherent message and send it. Do not send 10 messages in rapid succession.
- **Debounce** — You are not allowed to send more than two messages per minute about each ongoing project, unless the user specifically asks a question or wants your input. NOTE: this only applies to tasks directly related to this skill (auto-coder); other messages are of course allowed. 
- **Status Updates** — During your heartbeat, you will ascertain whether you need to notify the user about the status of ongoing projects. You will follow this algorithm:
1. If there are no ongoing projects, do not send a message.
2. If there are ongoing projects, check when the last message about each project was sent.
3. If less than 60 minutes have passed since the last message about a project, you will only send a message if there is a significant update (e.g., a task was completed, an audit failed, or a new feature was proposed).
4. If more than 60 minutes have passed since the last message about a project, you will send a message regardless of whether there is a significant update, to ensure the user knows the project is still active and being worked on. This message can be brief if there are no significant updates (e.g., "Still working on Task #N, no blockers").

Every heartbeat must include a status update to the user about ongoing projects. If more than 30 minutes have passed since your last message, send a status update even if there is nothing new — a brief "still working on Task #N, no blockers" is sufficient. Note: this only applies to items in the heartbeat related to ongoing coding projects. You do not also need to update the user on other items in the heartbeat file.

- **Menu Reminder** — The first status update sent to a user for a given project must include a note that they can type **"help"** or **"menu"** at any time to see available commands. Do not repeat this reminder in subsequent messages.

---

## Heartbeat Mode (Autonomous)

During every heartbeat, you MUST first anchor yourself to the correct project root before reading any backlog state.

1. **Pin Project Directory** *(mandatory)* —
   - Read `HEARTBEAT.md` and identify the absolute path of the project (e.g., `/Users/.../workspace/PROJECT_NAME`).
   - Explicitly `cd` into that directory before running ANY `backlog_manager.py` command.
   - Never assume the current working directory is correct.
   - If the project path cannot be determined, fail the heartbeat and report to the user.

2. **Check Status** — Once inside the correct project directory, check `coding_state.json` and `coding_backlog.json`.

3. **Resume** — If tasks remain `pending`, spawn the next one and follow Execution Mode (including Verification).

4. **Quality Assurance** — If all tasks are `completed`, run through the following phases in order:

#### Phase A — Production Audit

- Run build, lint, and tests.
- If any failure is found, create backlog tasks and resume Execution Mode.

#### Phase B — Runtime Validation *(mandatory)*

Run runtime checks appropriate to the project type:

| Project Type | Checks |
|---|---|
| **Web UI** | Launch dev server (if not running). Run browser-based analysis (Playwright-style): check console errors, verify key navigation flows, check data rendering, detect stale UI semantics, validate websocket features. |
| **API / Backend** | Start the server and run smoke tests against key endpoints. Verify response codes, payload structure, and error handling. |
| **CLI / Desktop** | Execute the main entry point with representative inputs. Verify expected output, exit codes, and error messages. |
| **Other** | Identify the most meaningful runtime check and execute it. If unsure, ask the user. |

##### Functional Testing *(mandatory)*

After runtime checks, use Playwright (preferred) or any available testing tool to exercise the application's functionality end-to-end. The goal is to discover bugs, regressions, and broken flows — not just verify that the app starts.

**What to test:**
- Core user flows (e.g., login, create/read/update/delete operations, navigation).
- Form submissions, validation feedback, and error states.
- API integrations — verify that data flows correctly between frontend and backend.
- Edge cases identified in `CONTRACT.md` and `SPEC.md`.
- Any flows that were added or modified by recently completed tasks.

**Safety — Read-Only Tests Only:**
- Tests MUST be non-destructive and MUST NOT alter infrastructure. Never reboot servers, install system updates, modify OS packages, change firewall rules, alter DNS, or perform any system administration actions.
- Tests MUST NOT delete or corrupt production/persistent data. If testing destructive operations (e.g., delete), use test-scoped data created during the test and clean up afterwards.
- If a test requires elevated privileges or infrastructure changes to run, skip it and log it as "skipped — requires infrastructure changes".

**Test Coverage Log:**
- Maintain a `QA_LOG.md` file in the project root.
- After each QA run, append a timestamped entry listing: tests executed, pass/fail status, errors found, and any tests skipped (with reason).
- Before each QA run, review `QA_LOG.md` to identify areas that have not been tested recently or at all, and prioritise those.
- The log ensures cumulative coverage — every QA cycle should expand the tested surface area rather than repeating the same checks.

If ANY issues are detected (from runtime checks or functional testing):

- Do not attempt immediate fixes. Instead, automatically add structured backlog tasks.
- Resume Execution Mode immediately within the same heartbeat.
- Do NOT brainstorm.

#### Phase C — Evolution Mode

Only if Phase A and B pass clean:

1. **Ensure Visibility** — Before presenting proposals, make sure any network-accessible artefacts are running and reachable. Start (or verify) dev servers, API servers, or any other services the user can access over the network. Provide the user with LAN-accessible URLs so they can see the current state of the project for themselves. This does not apply to artefacts that are not network-accessible (e.g., CLI tools, desktop apps).
2. **Propose** — Generate 3 "Next Evolution" proposals. These proposals need to cover three of the following categories: [UX Improvements, Security Hardening, Performance Enhancements, Architectural Enhancements, New Features, Documentation, Internationalisation support, API creation].
3. **Present** — Present the proposals to the user along with the URLs where they can see the project live.
4. **Execute** — Add any user-approved proposals to the backlog and resume Execution Mode.

---

## User Menu

When the user says **"help"** or **"menu"**, present the following options. The user can reply with the number or the name of the command.

| # | Command | What it does |
|---|---------|--------------|
| 1 | **Status** | Show the current task, backlog summary (pending / in-progress / completed / failed), and overall project health. |
| 2 | **Backlog** | List all tasks with their statuses. |
| 3 | **Add Task** | Prompt the user for a title and description, then add a new task to the backlog. |
| 4 | **Reopen Task** | Move a completed or failed task back to pending. Ask the user which task ID to reopen. |
| 5 | **Changelog** | Display the contents of `CHANGELOG.md`. |
| 6 | **QA Log** | Display the contents of `QA_LOG.md`. |
| 7 | **Spec** | Display the project specification (`SPEC.md`). |
| 8 | **Contract** | Display the semantic assertions and product rules (`CONTRACT.md`). |
| 9 | **View App** | Provide the LAN-accessible URL(s) where the user can see the running project. Start the dev server if it is not already running. |
| 10 | **Propose Features** | Trigger Evolution Mode (Phase C) — generate and present 3 feature proposals. |
| 11 | **Pause** | Stop picking up new tasks. The current in-progress task (if any) will finish, but no new tasks will be started until the user resumes. |
| 12 | **Resume** | Resume execution after a pause. |

**Pause / Resume behaviour:**
- When paused, set a `"paused": true` flag in `coding_state.json`. During heartbeats, check this flag before picking up tasks — if paused, skip Execution Mode and only send a status update.
- When resumed, set `"paused": false` and immediately enter Execution Mode.

---

## Backlog Management

Use the provided script to maintain consistency. All commands accept an optional `--project-dir <path>` flag to specify the project root (defaults to current directory).

| Command | Description |
|---|---|
| `python3 scripts/backlog_manager.py init "<project_name>"` | Initialize backlog and state files. |
| `python3 scripts/backlog_manager.py summary` | Get current stats. |
| `python3 scripts/backlog_manager.py list [--status <status>]` | List all tasks, optionally filtered by status (`pending`, `in-progress`, `completed`, `failed`). |
| `python3 scripts/backlog_manager.py next` | Get the top pending task. |
| `python3 scripts/backlog_manager.py add "<Title>" --desc "<Spec>" [--priority <level>]` | Add a task. Priority: `high`, `medium`, or `low`. |
| `python3 scripts/backlog_manager.py start <id>` | Mark a task as `in-progress` and set it as the current task in state. |
| `python3 scripts/backlog_manager.py complete <id>` | Mark a task as `completed` and record the completion timestamp. |
| `python3 scripts/backlog_manager.py fail <id> --reason "<explanation>"` | Mark a task as `failed` with a reason. |
| `python3 scripts/backlog_manager.py reopen <id>` | Move a `completed` or `failed` task back to `pending`. |
| `python3 scripts/backlog_manager.py log <id> --msg "<note>"` | Append a timestamped note (e.g., audit result) to a task. |
| `python3 scripts/backlog_manager.py update <id> <status>` | Directly set a task's status. Prefer `start`/`complete`/`fail` instead. |

---

## Constraints

- Always maintain `coding_backlog.json` and `coding_state.json` in the project root.
- Never delete the backlog without explicit user confirmation.
- If a sub-agent fails, retry up to 3 times (see Verification Mode). After exhausting retries, pause and report the error to the user with full context before continuing.
