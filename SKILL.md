---
name: auto-coder
description: A never-ending, autonomous software development loop. Manages a project from initial spec Q&A through task breakdown, execution via sub-agents, and proactive feature brainstorming. Use when a user wants to start a coding project and just have the AI 'do it'.
---

# Auto Coder

This skill implements a perpetual development cycle. It ensures that projects don't stall by integrating with the OpenClaw heartbeat system.

## Assumptions
1. You are working within OpenClaw. You have access to system tools. 

2. OpenClaw is running a heartbeat every 30 or so minutes. During this heartbeat, you must check the status of the backlog (see below) and continue coding, coming up with new features, or updating the user. Failing to carry out at least one of these three tasks per heartbeat is a critical failure.

3. The user is communicating with you via a messagning client (Telegram, WhatsApp etc...). So don't give the user links to local files which they can't open. When starting a development server, you need to ensure it is bound to LAN ips, not localhost, otherwise the user can't see the result.

4. You have access to carry out web searches. 

5. You have access to spawn coding agents using robust AI coding models.

On first run, you will verify the above. If anything is missing you will inform the user.

## Workflow

### 1. User Request
1. The user will ask for something to be created which requires coding. Since Auto Coder is not suitable for all situations, you must confirm with the user whether or not they want to use auto coder - unless their original request specifically mentions Auto Coder by name.

2. Once you have confirmed that the user really does want to user Auto Coder, we go to the next step in the workflow.

### 2. Discovery Mode
1. You will ask the user what they want to create. The user will give you an overview of the project/app/utility/game/website etc... that they want to create. 

2. **Grill the User**: Do not accept the spec immediately. Ask 3-5 sharp, technical questions about edge cases, stack preferences, or data structures. You MUST ask the user ALL of the following questions:

    - Tech stacks to be used. 
    - Desired front-end (web, desktop, mobile)
    - Any specific technologies to use (Java, Python, FastCGI, TailWind, Ruby, React, Angular, Svelte, SQLite and so on). Ensure you have a technology stack for both frontend and backend.

3. **Tech Research**: Proactively search for the latest stable versions of libraries and frameworks mentioned in the spec (e.g., Vite, Tailwind, FastAPI). Ensure the project uses modern, non-deprecated patterns. **IMPORTANT**: Unless the user tells you to use a specific version of a framework, technology, or library, you MUST:

    - Run a web search to discover the latest version of a technology, library, framework being used. 
    - Ensure that version number is remembered and that it will be used in the final project. 

4. **Coding Agent**: Ask the user which coding agent they want to use. They should reply with a provider/agent, such as "anthropic/claude-opus-4-6". 

### 3. Planning Mode
1. Following the discovery, you will write a final spec for this project in memory. 
2. You will create a folder for this project in your workspace. 
3. You will run `git init` within this folder. 
4. **Initialize**: Run `python3 scripts/backlog_manager.py init "<project_name>"`.
5. You will break the project spec into discrete tasks. You will then create a backlog with these tasks using `scripts/backlog_manager.py add`.
6. You will create a `.model` file in the directory. This stores the model to be used as specified by the user.
7. **EXTREMELY IMPORTANT**: You will add an entry in HEARTBEAT.md. You will add instructoins to check the backlog for this project as per Step 4: Execution Mode. You will also list the path of the project you have created, and the path to the skills/ folder for auto-coder. Failing to do this is considered a CRITICAL issue.

### 4. Execution Mode
The steps in this mode are to be followed in one of two situations.

    - Step 3 above has just been concluded, and you will now start coding. 
    - You are returning to this skill after a hearbeat. 

1.  **Pick Task**: Run `scripts/backlog_manager.py next`.

2.  **Spawn Sub-agent**: Use `sessions_spawn` with a high-reasoning model (specifically the one in `.model` in the project directory).

3.  **Instruction**: Instruct the sub-agent to use the `coding-agent` skill to complete the specific task in the workspace.

### 5. Verification Mode (CRITICAL - IF YOU IGNORE THIS, YOU FAIL)

1.  **Verification (CRITICAL)**: After the sub-agent finishes, you MUST run a verification step (e.g., `npm run lint`, `npm run build`, `pytest`, or `ruff check`) to catch errors and maintain code quality. Run as many checks as possible to ensure high code quality. Spawn sub-agents to fix the issues. 

2.  **Audit (MANDATORY)**: Spawn a separate sub-agent (using `.model`) to specifically audit the task completion. It must verify that the feature is not just coded, but integrated and functional. Inform the user of this audit result. You will also verify that the task the agent said it completed has actually been implemented. If not, re-spawn an agent with the current task.

3.  **Correction**: If verification or audit fails, fix the errors (or re-spawn) before marking the task as completed.

4.  **Update State**: Mark the task as `completed` only after successful verification and a passing audit.

5. **Inform the User**: Inform the user of what has been accomplished in this step, what audits were run, and the status of each audit. Also inform the user how they can check on progress (example: provide a URL, show them how to run a desktop app, etc)

## Execution Protocol (CRITICAL - DO NOT IGNORE)
- **NO ASKING FOR PERMISSION**: If there are tasks in the backlog, EXECUTE THEM. Do not end a turn by asking "Should I start?" or "Ready to proceed?".

- **PROACTIVE CONTINUATION**: After a task passes audit, immediately pick up the next task.

- **ZERO THEATRICS**: Skip the "I am starting now" or "I am your engineer" fluff. Just provide the status of the current run or the results of the audit.

- **AUDIT IS LAW**: If a task fails audit, it is NOT complete. Immediately re-spawn the sub-agent with the audit findings and fix it. Never report a failed task as "done".

## User Communication (IGNORE THIS IF YOU WANT TO FAIL MISERABLY)

- **DO NOT SPAM THE USER**: If you have many things to tell the user, don't create 10 messages and send them to the user all at one go. Prepare one coherent longer message, and send it.

- **DEBOUNCE**: You are not allowed to send more than two messages a minute to the user, unless the user specifically asks a question or wants your input. 

- **INFORM**: Every heartbeat must result in the user receiving some sort of status update. If you have not communicated with the user each heartbeat, you have failed. If your last message to the user was over 30 minutes ago, you have failed.

## Heartbeat Mode (Autonomous)
During every heartbeat, check `coding_state.json` and `coding_backlog.json`:
1.  **Check Status**: If a task was recently finished, check for any leftover error logs.

2.  **Resume**: If tasks remain `pending`, spawn the next one and follow the Execution Mode steps (including Verification).

3.  **Autonomous Audit**: If all tasks are `completed`, and the project has a web frontend, you MUST run a browser-based analysis (e.g., via sub-agent with browser access):
    - Verify the UI is functional, responsive, and free of console errors.
    - Identify UX friction or visual inconsistencies.
    - If issues are found, automatically `add` them to the backlog and resume **Execution Mode**.

4.  **Brainstorm**: If all tasks are `completed` AND the Autonomous Audit passes, generate 3 "Next Evolution" feature proposals. Present them to the user in the next interaction.

## Backlog Management
Use the provided script to maintain consistency:
- `python3 scripts/backlog_manager.py summary`: Get current stats.
- `python3 scripts/backlog_manager.py next`: Get the top pending task.
- `python3 scripts/backlog_manager.py add "<Title>" --desc "<Detailed Spec>"`: Add a task.

## Constraints
- Always maintain `coding_backlog.json` and `coding_state.json` in the project root.
- Never delete the backlog without explicit user confirmation.
- If a sub-agent fails, pause and report the error to the user immediately.
