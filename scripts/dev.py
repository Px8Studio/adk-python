#!/usr/bin/env python3
# Cross-platform Orkhon Dev CLI (replaces PowerShell scripts)

from __future__ import annotations

import argparse
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# ---------- Paths and constants ----------

SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1] if (SCRIPT_PATH.parent.name == "scripts") else SCRIPT_PATH.parent
TOOLBOX_COMPOSE = PROJECT_ROOT / "backend" / "toolbox" / "docker-compose.dev.yml"
AGENTS_DIR = PROJECT_ROOT / "backend" / "adk" / "agents"
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_BIN = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin")
TOOLBOX_HEALTH_URL = "http://localhost:5000/health"
WEB_PORT = 8000

# ---------- Helpers ----------

def run(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    check: bool = False,
    capture: bool = True,
    text: bool = True,
) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            check=False,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=text,
        )
        if check and proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd, proc.stdout, proc.stderr)
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except FileNotFoundError as e:
        return 127, "", str(e)


def which(cmd: str, extra_paths: Optional[Iterable[Path]] = None) -> Optional[str]:
    env = os.environ.copy()
    if extra_paths:
        prefix = os.pathsep.join(str(p) for p in extra_paths if p)
        env["PATH"] = prefix + os.pathsep + env.get("PATH", "")
    resolved = shutil.which(cmd, path=env.get("PATH"))
    return resolved


def docker_compose_cmd() -> Optional[List[str]]:
    # Prefer modern "docker compose"
    code, _, _ = run(["docker", "compose", "version"], capture=True)
    if code == 0:
        return ["docker", "compose"]
    # Fallback to legacy docker-compose
    if which("docker-compose"):
        return ["docker-compose"]
    return None


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex(("127.0.0.1", port))
        return result == 0


def wait_for_http_ok(url: str, timeout_seconds: int = 15, interval: float = 1.5) -> bool:
    import urllib.request
    import urllib.error

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if 200 <= resp.status < 300:
                    return True
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            pass
        time.sleep(interval)
    return False


def env_with_venv_path(base: Optional[dict] = None) -> dict:
    env = dict(base or os.environ)
    path_parts = [str(VENV_BIN)]
    env["PATH"] = os.pathsep.join(path_parts + [env.get("PATH", "")])
    # On Windows, ensure scripts can find DLLs
    if platform.system() == "Windows":
        env["VIRTUAL_ENV"] = str(VENV_DIR)
    return env


def print_info(msg: str) -> None:
    print(f"[i] {msg}")


def print_ok(msg: str) -> None:
    print(f"[✓] {msg}")


def print_err(msg: str) -> None:
    print(f"[x] {msg}", file=sys.stderr)


# ---------- Diagnostics ----------

def diagnose() -> bool:
    ok = True

    print_info(f"Project root: {PROJECT_ROOT}")
    print_info(f"Python: {sys.version.split()[0]} ({sys.executable})")
    if sys.version_info < (3, 11):
        print_err("Python 3.11+ is required.")
        ok = False
    else:
        print_ok("Python version OK")

    # Docker CLI
    code, out, _ = run(["docker", "--version"])
    if code != 0:
        print_err("Docker not found. Install Docker Desktop/Engine.")
        ok = False
    else:
        print_ok(out.strip() or "Docker found")

    # Docker daemon usable
    code, _, _ = run(["docker", "ps"])
    if code != 0:
        print_err("Docker daemon not reachable. Start Docker Desktop/Engine.")
        ok = False
    else:
        print_ok("Docker daemon OK")

    # docker compose
    dc = docker_compose_cmd()
    if not dc:
        print_err("docker compose not found (neither 'docker compose' nor 'docker-compose').")
        ok = False
    else:
        print_ok(f"Compose command: {' '.join(dc)}")

    # compose file
    if not TOOLBOX_COMPOSE.exists():
        print_err(f"Toolbox compose file missing: {TOOLBOX_COMPOSE}")
        ok = False
    else:
        print_ok(f"Compose file present: {TOOLBOX_COMPOSE}")

    # venv check
    if not VENV_BIN.exists():
        print_err(f"Virtualenv not found at: {VENV_BIN}")
        ok = False
    else:
        print_ok(f"Virtualenv found: {VENV_BIN}")

    # adk in venv
    env = env_with_venv_path()
    code, out, _ = run(["adk", "--version"], env=env)
    if code != 0:
        print_err("ADK CLI not found in virtualenv. Install ADK in .venv.")
        ok = False
    else:
        print_ok(f"ADK CLI: {out.strip()}")

    # agents dir
    if not AGENTS_DIR.exists():
        print_err(f"Agents directory missing: {AGENTS_DIR}")
        ok = False
    else:
        print_ok(f"Agents dir: {AGENTS_DIR}")

    return ok


# ---------- Toolbox control ----------

def toolbox_start_or_restart(restart: bool, wait_seconds: int) -> bool:
    dc = docker_compose_cmd()
    if not dc:
        print_err("Cannot run toolbox: docker compose not available.")
        return False

    cmd = dc + ["-f", str(TOOLBOX_COMPOSE)]
    if restart:
        print_info("Restarting Toolbox containers...")
        code, _, _ = run(cmd + ["restart"])
    else:
        print_info("Starting Toolbox containers...")
        code, _, _ = run(cmd + ["up", "-d"])

    if code != 0:
        print_err("Docker compose command failed.")
        return False

    print_info(f"Waiting up to {wait_seconds}s for Toolbox health...")
    ready = wait_for_http_ok(TOOLBOX_HEALTH_URL, timeout_seconds=wait_seconds)
    if ready:
        print_ok("Toolbox is healthy.")
        return True

    print_err("Toolbox health check failed within timeout.")
    print_info(f"Tip: {(' '.join(dc))} -f {TOOLBOX_COMPOSE} logs")
    return False


def toolbox_down() -> int:
    dc = docker_compose_cmd()
    if not dc:
        print_err("docker compose not available.")
        return 1
    code, out, err = run(dc + ["-f", str(TOOLBOX_COMPOSE), "down"])
    print(out or err)
    return code


def toolbox_logs() -> int:
    dc = docker_compose_cmd()
    if not dc:
        print_err("docker compose not available.")
        return 1
    # Non-follow, print snapshot
    code, out, err = run(dc + ["-f", str(TOOLBOX_COMPOSE), "logs", "--no-color"])
    print(out or err)
    return code


# ---------- Web server ----------

def find_pids_on_port(port: int) -> List[str]:
    pids: List[str] = []
    if platform.system() == "Windows":
        code, out, _ = run(["netstat", "-ano"])
        if code == 0:
            for line in out.splitlines():
                if f":{port} " in line:
                    parts = line.split()
                    if parts and parts[-1].isdigit():
                        pids.append(parts[-1])
    else:
        # lsof may not be available, best effort
        if which("lsof"):
            code, out, _ = run(["lsof", "-t", f"-i:{port}"])
            if code == 0:
                pids = [p for p in out.split() if p.isdigit()]
    return sorted(set(pids))


def kill_pids(pids: List[str]) -> None:
    for pid in pids:
        if platform.system() == "Windows":
            run(["taskkill", "/PID", pid, "/F"], capture=False)
        else:
            run(["kill", "-9", pid], capture=False)


def start_web_server(force_kill_port: bool = False) -> int:
    if port_in_use(WEB_PORT):
        if not force_kill_port:
            print_err(f"Port {WEB_PORT} is in use. Use --force-kill-port to free it.")
            offenders = find_pids_on_port(WEB_PORT)
            if offenders:
                print_info(f"PIDs using {WEB_PORT}: {', '.join(offenders)}")
            return 1
        offenders = find_pids_on_port(WEB_PORT)
        if offenders:
            print_info(f"Killing PIDs on port {WEB_PORT}: {', '.join(offenders)}")
            kill_pids(offenders)
            time.sleep(1)
        if port_in_use(WEB_PORT):
            print_err(f"Port {WEB_PORT} still in use after kill attempt.")
            return 1

    env = env_with_venv_path()
    cmd = [
        "adk",
        "web",
        "--reload_agents",
        "--host=0.0.0.0",
        f"--port={WEB_PORT}",
        str(AGENTS_DIR),
    ]

    print_info("Starting ADK Web Server...")
    print_info(f"URL: http://localhost:{WEB_PORT}")
    print_info("Press CTRL+C to stop.")

    try:
        proc = subprocess.Popen(cmd, env=env, cwd=str(PROJECT_ROOT))
        proc.wait()
        return proc.returncode or 0
    except KeyboardInterrupt:
        print_info("Stopping ADK Web (interrupt)...")
        try:
            proc.terminate()  # type: ignore
        except (OSError, ProcessLookupError, PermissionError):
            pass
        return 0


# ---------- CLI ----------

def main(argv: Optional[List[str]] = None) -> int:
    # Accept being called without args; default to quick-start
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print_info("No command provided. Defaulting to 'quick-start'. Use -h for help.")
        argv = ["quick-start"]

    parser = argparse.ArgumentParser(description="Orkhon Dev CLI (terminal-agnostic).")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("diagnose", help="Run environment diagnostics.")

    tb = sub.add_parser("toolbox", help="Manage GenAI Toolbox.")
    tb_sub = tb.add_subparsers(dest="action", required=True)
    tb_start = tb_sub.add_parser("start", help="Start Toolbox (docker compose up -d).")
    tb_start.add_argument("--wait", type=int, default=15, help="Seconds to wait for Toolbox health.")
    tb_restart = tb_sub.add_parser("restart", help="Restart Toolbox containers.")
    tb_restart.add_argument("--wait", type=int, default=15, help="Seconds to wait for Toolbox health.")
    tb_sub.add_parser("down", help="Stop Toolbox (docker compose down).")
    tb_sub.add_parser("logs", help="Show Toolbox logs (snapshot).")

    web = sub.add_parser("web", help="Run ADK Web server.")
    web.add_argument("--force-kill-port", action="store_true", help="Kill processes on port 8000 if needed.")

    qs = sub.add_parser("quick-start", help="Run diagnostics, start Toolbox, then start ADK Web.")
    qs.add_argument("--skip-diagnostics", action="store_true")
    qs.add_argument("--restart-toolbox", action="store_true")
    qs.add_argument("--wait", type=int, default=15, help="Seconds to wait for Toolbox to become healthy.")
    qs.add_argument("--force-kill-port", action="store_true", help="Kill processes on port 8000 if needed.")

    args = parser.parse_args(argv)

    if args.command == "diagnose":
        return 0 if diagnose() else 1

    if args.command == "toolbox":
        if args.action == "start":
            ok = toolbox_start_or_restart(restart=False, wait_seconds=args.wait)
            return 0 if ok else 1
        if args.action == "restart":
            ok = toolbox_start_or_restart(restart=True, wait_seconds=args.wait)
            return 0 if ok else 1
        if args.action == "down":
            return toolbox_down()
        if args.action == "logs":
            return toolbox_logs()
        return 1

    if args.command == "web":
        return start_web_server(force_kill_port=args.force_kill_port)

    if args.command == "quick-start":
        if not args.skip_diagnostics:
            if not diagnose():
                print_info("Continuing despite diagnostic issues (requested).")
        ok = toolbox_start_or_restart(restart=args.restart_toolbox, wait_seconds=args.wait)
        if not ok:
            print_info("Continuing to web even if Toolbox not yet healthy.")
        # Quick venv/adk recheck before web
        env = env_with_venv_path()
        code, _, _ = run(["adk", "--version"], env=env)
        if code != 0:
            print_err("ADK CLI not found in .venv. Aborting.")
            return 1
        return start_web_server(force_kill_port=args.force_kill_port)

    return 0


if __name__ == "__main__":
    sys.exit(main())