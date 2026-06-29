# Copilot / AI Agent Instructions — vzbot 330

This repo holds the configuration, firmware artifacts, host services, and worklogs for a
**vzbot 330** 3D printer (Klipper + Moonraker on a Raspberry Pi). These notes describe
**how to work in this repo** — conventions, workflow, and safety. For machine/hardware
facts, read the `README.md` instead.

## How we work here

### Source of truth & syncing
- `new_config/` is the **canonical copy of the live Pi config**. When you change config on
  the Pi, mirror it back into `new_config/`; when you change `new_config/`, deploy it to the Pi.
- Don't let the repo and the live Pi drift. State which side you edited and keep them in sync.
- For any config change, update both the live vzbot side and the local repo side as a paired
  change unless the user explicitly asks for one side only.

### Config sync rule (`printer.cfg` and friends)
**Goal:** this repo should always hold the latest config from the live vzbot, with
`new_config/printer.cfg` as the primary file to keep current.
- **Proactively offer to sync.** At natural checkpoints — e.g. after a config/firmware change
  is verified on the Pi, at the end of a work session, or before committing — compare the live
  Pi config against `new_config/` and, if they differ, **ask the user whether to sync the Pi
  copy into the repo**. Don't sync silently.
- **Direction is Pi → repo by default** for this rule (the Pi is where edits happen during
  tuning). Pull the live file and update `new_config/` to match.
- **Show what differs** before syncing (a brief diff or summary of changed sections), so the
  user can confirm the changes are intended and contain no personal data.
- **Scope**: at minimum `printer.cfg`; also offer to refresh the other `new_config/` files
  (`moonraker.conf`, `macro.cfg`, etc.) when they have drifted.
- **Strip/skip secrets and personal details** (hosts, usernames, API keys) — never copy them
  into the repo (see Privacy below).
- After syncing, note it was a Pi → repo update and remind the user to review/commit.

### Editing live config on the Pi
- **Back up before editing**: copy to `<file>.bak.<timestamp>` first.
- After a change, **restart only the affected service** (`klipper`, `moonraker`, etc.) and
  verify it came back healthy before moving on.
- Prefer small, reversible steps. Confirm each step worked before the next.

### Worklog convention (required for hardware/firmware/config changes)
- Add one Markdown file per change to `worklog/`, named by date: `YYYY-MM-DD-<slug>.md`.
- Use these sections: `Goal`, `Pre-change`, `Post-change`, `Steps`, `Key commands`, `Follow-ups`.
- Add a one-line link to the new file under the README `## Worklog` index.
- Keep the **README to current-state facts + the worklog index** — narrative history lives
  in `worklog/`, not the README.

### Firmware / irreversible actions
- Firmware flashing is **hard to reverse**. Verify rollback artifacts exist in
  `doc/firmware_backup/` before flashing, and capture what you did in a worklog entry.
- Ask before destructive or shared-state actions (flashing, force pushes, deleting backups).
  Don't bypass safety checks (`--no-verify`, etc.) or discard in-progress work.

### Privacy in this public repo
- Pi access uses a **personal SSH alias** kept in the user's local shell profile.
- **Never commit** the username, host, IPs, serials, or other personal details.

### Communication
- Be concise. Report what changed, which side (repo vs Pi), and what to verify next.
- When unsure about an irreversible or ambiguous step, ask a short clarifying question first.
