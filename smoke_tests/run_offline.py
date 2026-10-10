"""Run in a fresh process: .venv311/bin/python -m smoke_tests.run_offline."""

import asyncio
import importlib.metadata
import json
import os
import socket
import subprocess
import sys
import unittest

from smoke_tests.runtime import (
    FORBIDDEN_PROCESS_ATTEMPTS, NETWORK_ATTEMPTS, OfflineViolation,
    SOCKET_CONSTRUCTIONS, configure_project_credential_storage,
    install_offline_audit, prepare_runtime,
)

prepare_runtime()
install_offline_audit()  # Active during framework imports as well as execution.
configure_project_credential_storage()


class MilestoneOneTests(unittest.TestCase):
    def test_01_audit_blocks_network(self):
        with self.assertRaises(OfflineViolation):
            socket.getaddrinfo("example.invalid", 443)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            with self.assertRaises(OfflineViolation):
                client.connect(("192.0.2.1", 443))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            with self.assertRaises(OfflineViolation):
                client.sendto(b"negative-control", ("192.0.2.1", 443))
        with self.assertRaises(OfflineViolation):
            subprocess.Popen(["offline-negative-control-never-executed"])
        self.assertEqual(NETWORK_ATTEMPTS, ["socket.getaddrinfo", "socket.connect", "socket.sendto"])
        self.assertEqual(FORBIDDEN_PROCESS_ATTEMPTS, ["subprocess.Popen"])
        print("NEGATIVE_CONTROLS DNS/connect/sendto/child-process blocked before execution")
        NETWORK_ATTEMPTS.clear()  # Deliberate negative control is separate from framework attempts.
        FORBIDDEN_PROCESS_ATTEMPTS.clear()
        SOCKET_CONSTRUCTIONS.clear()

    def test_02_isolated_python311_and_controls(self):
        self.assertEqual(sys.version_info[:2], (3, 11))
        self.assertNotEqual(sys.prefix, sys.base_prefix)
        self.assertEqual(os.environ["CREWAI_DISABLE_TELEMETRY"], "true")
        self.assertEqual(os.environ["OTEL_SDK_DISABLED"], "true")
        self.assertEqual(os.environ["MOCK_LLM"], "true")
        self.assertFalse(any(k.endswith(("_API_KEY", "_API_TOKEN", "_ACCESS_TOKEN")) for k in os.environ))

    def test_03_real_crew_tool_and_pydantic(self):
        from smoke_tests.crew_smoke import run_crew_smoke
        first = run_crew_smoke()
        second = run_crew_smoke()
        self.assertEqual(first, second)

    def test_04_autogen_approves_crew_draft(self):
        from smoke_tests.crew_smoke import run_crew_smoke
        from smoke_tests.review_smoke import run_review_smoke
        crew_result = run_crew_smoke()
        draft = crew_result["response"]["answer"]
        result = asyncio.run(run_review_smoke(draft, draft))
        self.assertTrue(result["verdict"]["approved"])
        self.assertEqual(result["verdict"]["final_answer"], draft)

    def test_05_autogen_revises_injected_claim(self):
        from smoke_tests.crew_smoke import run_crew_smoke
        from smoke_tests.review_smoke import run_review_smoke
        context = run_crew_smoke()["response"]["answer"]
        draft = context + " A refund is guaranteed."
        first = asyncio.run(run_review_smoke(draft, context))
        second = asyncio.run(run_review_smoke(draft, context))
        self.assertFalse(first["verdict"]["approved"])
        self.assertEqual(first["verdict"]["final_answer"], context)
        self.assertNotEqual(first["verdict"]["final_answer"], draft)
        self.assertEqual(first, second)

    def test_06_no_framework_network_or_child_process_attempts(self):
        self.assertEqual(NETWORK_ATTEMPTS, [])
        self.assertEqual(FORBIDDEN_PROCESS_ATTEMPTS, [])


if __name__ == "__main__":
    print("VERSIONS " + json.dumps({name: importlib.metadata.version(name) for name in
          ("crewai", "crewai-core", "autogen-agentchat", "autogen-core", "pydantic")}, sort_keys=True), flush=True)
    print("PYTHON " + sys.version.split()[0], flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MilestoneOneTests))
    print("OFFLINE_AUDIT " + json.dumps({"framework_network_attempts": NETWORK_ATTEMPTS,
          "child_process_attempts": FORBIDDEN_PROCESS_ATTEMPTS,
          "socket_constructions_without_network": SOCKET_CONSTRUCTIONS}), flush=True)
    sys.exit(0 if result.wasSuccessful() else 1)
