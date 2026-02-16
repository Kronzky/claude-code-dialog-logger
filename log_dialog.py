#!/usr/bin/env python3
"""
Claude Code Stop hook — appends new conversation turns to dialog.md
in the current project's working directory.

State is tracked per session in ~/.claude/hooks/dialog_state.json
so only new lines are written on each hook invocation.
"""

import json
import os
import sys
from pathlib import Path

STATE_FILE = Path.home() / '.claude' / 'hooks' / 'dialog_state.json'


def extract_text(content):
    """Extract plain text from a message content field.
    Handles both raw string content and structured block arrays.
    Only extracts 'text' blocks, ignoring tool_use and tool_result blocks.
    """
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                text = block.get('text', '').strip()
                if text:
                    parts.append(text)
        return '\n'.join(parts)

    return ''


def load_state():
    """Load the per-session line-count state file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    """Persist the updated state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        return

    hook_data = json.loads(raw)
    transcript_path = hook_data.get('transcript_path', '')
    cwd           = hook_data.get('cwd', '.')
    session_id    = hook_data.get('session_id', 'unknown')

    if not transcript_path or not os.path.exists(transcript_path):
        return

    # Read full transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Only process lines added since the last hook run for this session
    state      = load_state()
    last_count = state.get(session_id, 0)
    new_lines  = lines[last_count:]

    entries = []
    for line in new_lines:
        line = line.strip()
        if not line:
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Transcript entries may be wrapped: {type, message: {role, content}}
        # or flat: {role, content}
        msg  = record.get('message', record)
        role = msg.get('role', '')

        if role not in ('user', 'assistant'):
            continue

        text = extract_text(msg.get('content', ''))
        if text:
            entries.append((role, text))

    # Append to dialog.md in the project cwd (creates file if it doesn't exist)
    dialog_path = os.path.join(cwd, 'dialog.md')
    if entries:
        # Check if dialog.md already has content (to avoid leading separator)
        file_exists_with_content = (
            os.path.exists(dialog_path) and os.path.getsize(dialog_path) > 0
        )
        with open(dialog_path, 'a', encoding='utf-8') as f:
            for idx, (role, text) in enumerate(entries):
                label = 'User' if role == 'user' else 'Claude'
                # Write separator before each User entry, but not before the very first line
                if role == 'user' and (file_exists_with_content or idx > 0):
                    f.write('---\n')
                f.write(f'**{label}:** {text}\n')

    # Save updated line count for this session
    state[session_id] = len(lines)
    save_state(state)


if __name__ == '__main__':
    main()
