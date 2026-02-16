# Claude Code Dialog Logger

A Claude Code `Stop` hook that incrementally appends conversation turns to a `dialog.md` file in the current project's working directory.

## What it does

After every Claude response, the hook reads the session transcript, extracts only the human-readable `user` and `assistant` text (ignoring tool calls and tool results), and appends any new turns to `dialog.md`. State is tracked per session so turns are never duplicated across hook invocations.

### Output format (`dialog.md`)

```markdown
**User:** <message>
**Claude:** <response>

---

**User:** <next message>
**Claude:** <next response>
```

## Installation

1. Copy `log_dialog.py` to `~/.claude/hooks/log_dialog.py`
2. Add the following to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python /home/user/.claude/hooks/log_dialog.py"
          }
        ]
      }
    ]
  }
}
```

> Replace `/home/user/` with your actual home directory path (e.g. `C:/Users/YourName/` on Windows).

## State file

Per-session line counts are stored in `~/.claude/hooks/dialog_state.json` to ensure only new transcript lines are processed on each run.
