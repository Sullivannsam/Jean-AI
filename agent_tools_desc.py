#!/usr/bin/env python3
"""
Human-readable descriptions of every agent tool, used by system_prompt.py so the
model actually knows what it can call. Keep in sync with the TOOLS dicts in
agent.py (and the ssh_* tools added by server/agent_core.py when configured).
"""

TOOLS_HELP = {
    "run_shell": "Run a shell command on this machine and return its output. Use for git, npm, pip, nmap, tests, python, etc.",
    "read_file": "Read a file from disk and return its contents. Use before editing code so you see what's there.",
    "write_file": "Create or overwrite a file with the given content. Use to write code, configs, YAML, scripts.",
    "list_dir": "List the files and folders in a directory. Use to explore the project before acting.",
    "ha_turn_on": "Turn on a Home Assistant device. Args: entity_id (e.g. 'light.porch').",
    "ha_turn_off": "Turn off a Home Assistant device. Args: entity_id.",
    "ha_set_temperature": "Set a thermostat temperature. Args: entity_id, temperature.",
    "ha_get_state": "Get the current state of a Home Assistant entity. Args: entity_id.",
    "ha_list_entities": "List Home Assistant entities, optionally filtered by domain (e.g. 'light').",
    "remember": "Remember a fact long-term (key/value). Use for preferences and important info the user wants kept.",
    "recall": "Recall all long-term remembered facts. Use when you need the user's saved preferences/context.",
    "describe_scene": "Describe an image with the vision model. Args: prompt.",
    "kb_search": "Search your knowledge base (curated + auto-researched docs) for a query. Return top matching chunks. Use BEFORE answering anything that might be in your docs.",
    "kb_ingest": "Add a file or folder to the knowledge base index. Args: path.",
    "kb_stats": "Show how many chunks are in the knowledge base and whether embeddings are active.",
    "research": "Research a topic from given URLs: fetch, save as a knowledge doc, ingest it, remember it. Args: topic, urls (list).",
    "search_history": "Search ALL of your past conversation sessions for a word or phrase. Use when the user says 'find where I wrote X' or 'in a previous session'. Args: query, k.",
    "list_sessions": "List all past conversation session logs with timestamps, so you know what was discussed and when.",
    "ssh_shell": "Run a command on a remote machine over SSH if configured. Args: cmd.",
    "ssh_read": "Read a remote file over SSH if configured. Args: path.",
    "ssh_write": "Write a remote file over SSH if configured. Args: path, content.",
    "ssh_list": "List a remote directory over SSH if configured. Args: path.",
}