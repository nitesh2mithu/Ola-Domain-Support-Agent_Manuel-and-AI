"""Set offline controls before any framework import and audit network attempts."""

import os
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NETWORK_ATTEMPTS: list[str] = []
FORBIDDEN_PROCESS_ATTEMPTS: list[str] = []
SOCKET_CONSTRUCTIONS: list[str] = []


class OfflineViolation(RuntimeError):
    """A forbidden operation was attempted during the offline check."""


def prepare_runtime() -> None:
    # Apply before importing CrewAI/AutoGen, including their telemetry modules.
    os.environ.update({
        "MOCK_LLM": "true",
        "CREWAI_DISABLE_TELEMETRY": "true",
        "OTEL_SDK_DISABLED": "true",
        "CREWAI_TRACING_ENABLED": "false",
        "ANONYMIZED_TELEMETRY": "false",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "CREWAI_STORAGE_DIR": str(ROOT / ".runtime" / "crewai"),
        "XDG_CACHE_HOME": str(ROOT / ".cache"),
    })
    # Never print credential values. Remove keys even if the parent shell has them.
    for name in list(os.environ):
        if name.endswith(("_API_KEY", "_API_TOKEN", "_ACCESS_TOKEN")):
            os.environ.pop(name)
    os.environ.pop("CREWAI_API_KEY", None)


def configure_project_credential_storage() -> None:
    """Local storage shim for pinned CrewAI's otherwise hard-coded macOS path.

    Changes only the credential directory, never model calls or orchestration.
    No existing personal credentials are read; generated local keys are gitignored.
    Remove this shim when CrewAI exposes a supported credential-path setting.
    """
    from crewai_core.token_manager import TokenManager

    def project_path() -> Path:
        path = ROOT / ".runtime" / "crewai" / "credentials"
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.chmod(0o700)
        return path

    TokenManager._get_secure_storage_path = staticmethod(project_path)


def install_offline_audit() -> None:
    """Deny Python internet connections/DNS and child processes for this process.

    Local AF_UNIX sockets remain available for asyncio's internal wakeup pipe.
    This is a test harness, not an application guardrail or OS-wide firewall.
    """
    def audit(event: str, args: tuple) -> None:
        if event == "socket.__new__" and args[1] in (socket.AF_INET, socket.AF_INET6):
            # urllib3 probes IPv6 support by constructing/binding a local socket.
            # Construction sends no traffic; actual DNS/connect/sendto stay denied.
            import traceback
            frame = traceback.extract_stack(limit=5)[-3]
            SOCKET_CONSTRUCTIONS.append(f"{Path(frame.filename).name}:{frame.name}")
        internet_connect = (
            event in ("socket.connect", "socket.sendto")
            and args[0].family in (socket.AF_INET, socket.AF_INET6)
        )
        dns = event in ("socket.getaddrinfo", "socket.gethostbyname", "socket.gethostbyaddr")
        if internet_connect or dns:
            NETWORK_ATTEMPTS.append(event)
            raise OfflineViolation(f"Offline test blocked {event}")
        if event in ("subprocess.Popen", "os.system", "os.posix_spawn"):
            FORBIDDEN_PROCESS_ATTEMPTS.append(event)
            raise OfflineViolation(f"Offline test blocked {event}")

    sys.addaudithook(audit)
