from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class LocalSandbox:
    name = "local"

    def __init__(self, timeout_seconds: int = 30, output_limit: int = 1_000_000):
        self.timeout_seconds = timeout_seconds
        self.output_limit = output_limit

    @staticmethod
    def _limits() -> None:
        try:
            import resource

            resource.setrlimit(resource.RLIMIT_CPU, (25, 25))
            resource.setrlimit(resource.RLIMIT_AS, (1_610_612_736, 1_610_612_736))
            resource.setrlimit(resource.RLIMIT_FSIZE, (16_777_216, 16_777_216))
            resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
            if hasattr(resource, "RLIMIT_NPROC"):
                resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
        except (ImportError, OSError, ValueError):
            return

    def run_command(self, command: list[str], candidate: Path, scratch: Path) -> RunResult:
        executable = [sys.executable, *command[1:]] if command and command[0] == "python" else command
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "HOME": str(scratch),
            "TMPDIR": str(scratch),
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTEST_ADDOPTS": "-p no:cacheprovider",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        }
        process = subprocess.Popen(
            executable,
            cwd=candidate,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
            preexec_fn=self._limits if os.name == "posix" else None,
        )
        try:
            stdout, stderr = process.communicate(timeout=self.timeout_seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            stdout, stderr = process.communicate()
        if len(stdout) + len(stderr) > self.output_limit:
            return RunResult(125, stdout[: self.output_limit], stderr[: self.output_limit], timed_out)
        return RunResult(124 if timed_out else process.returncode, stdout, stderr, timed_out)

    def run_worker(self, candidate: Path, request: Path, output: Path, scratch: Path) -> RunResult:
        worker = Path(__file__).with_name("_worker.py")
        return self.run_command(
            ["python", "-I", str(worker), str(candidate), str(request), str(output)],
            candidate,
            scratch,
        )

    def manifest(self) -> dict[str, object]:
        return {
            "mode": self.name,
            "network_isolation": False,
            "filesystem_isolation": False,
            "wall_timeout_seconds": self.timeout_seconds,
            "cpu_limit_seconds": 25,
            "memory_limit_mb": 1536,
            "process_limit": 64,
            "output_limit_bytes": self.output_limit,
            "use": "development only",
        }


class DockerSandbox:
    name = "docker"
    image = "pipelineproof-task:0.3.0"

    def __init__(self, timeout_seconds: int = 30, output_limit: int = 1_000_000):
        self.timeout_seconds = timeout_seconds
        self.output_limit = output_limit

    def available(self) -> bool:
        return shutil.which("docker") is not None

    def _base(self, candidate: Path, scratch: Path) -> list[str]:
        scratch.mkdir(parents=True, exist_ok=True)
        scratch.chmod(0o777)
        return [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--cpus",
            "1",
            "--memory",
            "512m",
            "--pids-limit",
            "64",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--user",
            "65532:65532",
            "-e",
            "PYTHONDONTWRITEBYTECODE=1",
            "-e",
            "PYTEST_ADDOPTS=-p no:cacheprovider",
            "-e",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            "-v",
            f"{candidate.resolve()}:/workspace:ro",
            "-v",
            f"{scratch.resolve()}:/scratch:rw",
            "-w",
            "/workspace",
            self.image,
        ]

    def _run(self, command: list[str], candidate: Path, scratch: Path) -> RunResult:
        try:
            completed = subprocess.run(
                [*self._base(candidate, scratch), *command],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            stdout, stderr = completed.stdout, completed.stderr
            if len(stdout) + len(stderr) > self.output_limit:
                return RunResult(125, stdout[: self.output_limit], stderr[: self.output_limit])
            return RunResult(completed.returncode, stdout, stderr)
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else error.stdout or ""
            stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else error.stderr or ""
            return RunResult(124, stdout, stderr, True)

    def run_command(self, command: list[str], candidate: Path, scratch: Path) -> RunResult:
        return self._run(command, candidate, scratch)

    def run_worker(self, candidate: Path, request: Path, output: Path, scratch: Path) -> RunResult:
        request.chmod(0o644)
        return self._run(
            [
                "python",
                "-I",
                "/opt/pipelineproof/worker.py",
                "/workspace",
                f"/scratch/{request.name}",
                f"/scratch/{output.name}",
            ],
            candidate,
            scratch,
        )

    def manifest(self) -> dict[str, object]:
        return {
            "mode": self.name,
            "image": self.image,
            "network": "none",
            "root_filesystem": "read-only",
            "candidate_mount": "read-only",
            "scratch_mount": "read-write",
            "tmpfs": "/tmp, noexec, nosuid, 64 MB",
            "cpu_limit": 1,
            "memory_limit_mb": 512,
            "process_limit": 64,
            "capabilities": "dropped",
            "no_new_privileges": True,
            "user": "65532:65532",
            "wall_timeout_seconds": self.timeout_seconds,
            "output_limit_bytes": self.output_limit,
        }
