import pytest

from pathlib import Path
from typing import List, Optional


class TestRunner:
    """
    Orchestrates running pytest for one or more targets (subfolders under tests/),
    wiring common options like reports and config host index.
    """

    def __init__(
        self,
        tests_path: str,
        output_path: str,
        host_index: int = 0,
        mark: Optional[str] = None,
        num_processes: int = 0,
    ):
        self._tests_path = Path(tests_path).resolve()
        self._output_path = Path(output_path).resolve()
        self._output_path.mkdir(parents=True, exist_ok=True)

        self._host_index = host_index
        self._mark = mark
        self._num_processes = max(0, int(num_processes))

    @property
    def tests_path(self) -> Path:
        return self._tests_path

    @property
    def output_path(self) -> Path:
        return self._output_path

    @property
    def host_index(self) -> int:
        return self._host_index

    @property
    def mark(self) -> Optional[str]:
        return self._mark

    @property
    def num_processes(self) -> int:
        return self._num_processes

    def _xdist_available(self) -> bool:
        try:
            import xdist  # noqa: F401
            return True
        except Exception:
            return False

    def _html_available(self) -> bool:
        try:
            import pytest_html  # noqa: F401
            return True
        except Exception:
            return False

    def _pytest_args_for_target(self, target_folder_name: str) -> List[str]:
        target_path = self.tests_path / target_folder_name
        if not target_path.exists():
            raise FileNotFoundError(f"Target folder not found: {target_path}")

        xml_report = self.output_path / "test-report.xml"
        html_report = self.output_path / "test-report.html"

        args: List[str] = [
            "-v",
            "--capture", "no",
            "--host_index", str(self.host_index),
            "--junitxml", str(xml_report),
            str(target_path),
        ]

        # Only add HTML report if plugin is present
        if self._html_available():
            args.extend(["--html", str(html_report)])

        if self.mark:
            args.extend(["-k", self.mark])

        # Add parallelism only if requested and xdist is present
        if self.num_processes > 0 and self._xdist_available():
            args.extend(["-n", str(self.num_processes)])

        return args

    def run(self, targets: List[str]) -> int:
        """
        Run pytest once per target. Aggregate the worst exit code.
        """
        worst_exit = 0
        for target in targets:
            args = self._pytest_args_for_target(target)
            print(f"[runner] pytest args for '{target}': {args}")
            code = pytest.main(args)
            worst_exit = max(worst_exit, int(code))
        return worst_exit
