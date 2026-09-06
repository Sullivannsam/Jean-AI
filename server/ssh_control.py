#!/usr/bin/env python3
"""
SSH-based control channel to a laptop (or any remote machine).

The server reaches the laptop over SSH using key-based auth (no password).
To enable, on the SERVER generate a keypair, install the PUBLIC key on the
laptop:

    ssh-keygen -t ed25519 -f ~/.ssh/laptop_control -N ""
    ssh-copy-id -i ~/.ssh/laptop_control.pub user@laptop

Then set in .env:
    SSH_TARGET=user@192.168.1.50
    SSH_KEY=/home/youruser/.ssh/laptop_control
    SSH_PORT=22

Every command goes through ssh and is returned to the agent. File ops are
routed through scp. Nothing here opens an inbound port on the laptop — it only
uses the SSH connection the server initiates.
"""
import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

SSH_TARGET = os.getenv("SSH_TARGET", "").strip()
SSH_KEY = os.getenv("SSH_KEY", "").strip()
SSH_PORT = os.getenv("SSH_PORT", "22").strip()
SSH_ALLOWED_DIRS = [d.strip() for d in os.getenv("SSH_ALLOWED_DIRS", "").split(":") if d.strip()]


def _configured() -> bool:
    return bool(SSH_TARGET and SSH_KEY and os.path.exists(SSH_KEY))


def _base_cmd() -> list[str]:
    return ["ssh", "-i", SSH_KEY, "-p", SSH_PORT, "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", SSH_TARGET]


def _run(argv: list[str]) -> dict:
    if not _configured():
        return {"error": "SSH not configured. Set SSH_TARGET, SSH_KEY, SSH_PORT in .env and install the public key on the laptop."}
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        return {
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-2000:],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "SSH command timed out after 60s.", "exit_code": -1}
    except FileNotFoundError:
        return {"error": "'ssh' not found on this server."}


def remote_shell(cmd: str) -> dict:
    """Run a shell command on the laptop over SSH."""
    if not cmd.strip():
        return {"error": "Empty command."}
    return _run(_base_cmd() + [cmd])


def _remote_path_in_scope(remote_path: str) -> bool:
    if not SSH_ALLOWED_DIRS:
        return False  # no dirs allowed until configured
    return any(remote_path.startswith(d.rstrip("/") + "/") or remote_path == d for d in SSH_ALLOWED_DIRS)


def remote_read(path: str) -> dict:
    """Read a file from the laptop (scoped to SSH_ALLOWED_DIRS)."""
    if not _remote_path_in_scope(path):
        return {"error": f"Path '{path}' is not in SSH_ALLOWED_DIRS. Scoped to: {SSH_ALLOWED_DIRS}"}
    return _run(["ssh", "-i", SSH_KEY, "-p", SSH_PORT, "-o", "BatchMode=yes", SSH_TARGET, f"cat {__import__('shlex').quote(path)}"])


def remote_write(path: str, content: str) -> dict:
    """Write a file to the laptop via a heredoc through SSH (scoped)."""
    if not _remote_path_in_scope(path):
        return {"error": f"Path '{path}' is not in SSH_ALLOWED_DIRS. Scoped to: {SSH_ALLOWED_DIRS}"}
    import shlex
    quoted = shlex.quote(path)
    cmd = ["ssh", "-i", SSH_KEY, "-p", SSH_PORT, "-o", "BatchMode=yes", SSH_TARGET,
           f"mkdir -p $(dirname {quoted}) && cat > {quoted} <<'AGENTEOF'\n{content}\nAGENTEOF"]
    return _run(cmd)


def remote_list(path: str) -> dict:
    """List a directory on the laptop (scoped)."""
    if path in ("", "."):
        path = "~"
    return _run(_base_cmd() + [f"ls -la {__import__('shlex').quote(path)}"])


def is_configured() -> bool:
    return _configured()