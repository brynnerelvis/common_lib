import csv
from pathlib import Path
import xml.etree.ElementTree as ET

from typing import Dict, List


class SuiteSummary:
    """
    Minimal representation of a test suite summary derived from JUnit XML.
    """
    def __init__(self, name: str, tests: int, failures: int, errors: int, skipped: int, time_s: float):
        self.name = name
        self.tests = tests
        self.failures = failures
        self.errors = errors
        self.skipped = skipped
        self.time_s = time_s

    @property
    def passed(self) -> int:
        return max(0, self.tests - (self.failures + self.errors + self.skipped))

    @property
    def pass_rate(self) -> float:
        return round(100.0 * self.passed / self.tests, 1) if self.tests else 0.0


class JUnitResults:
    """
    Parse a single pytest JUnit XML file and provide aggregate metrics
    and a flat list of (classname, name, result).
    """

    def __init__(self, xml_file: str):
        self.path = Path(xml_file).resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"JUnit XML not found: {self.path}")
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()

    def summary(self) -> SuiteSummary:
        # pytest writes a <testsuite> root with attributes we can read directly
        suite = self.root
        name = suite.attrib.get("name", self.path.stem)
        tests = int(suite.attrib.get("tests", 0))
        failures = int(suite.attrib.get("failures", 0))
        errors = int(suite.attrib.get("errors", 0))
        skipped = int(suite.attrib.get("skipped", 0))
        time_s = float(suite.attrib.get("time", 0.0))
        return SuiteSummary(name, tests, failures, errors, skipped, time_s)

    def cases(self) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        for case in self.root.findall(".//testcase"):
            classname = case.attrib.get("classname", "")
            name = case.attrib.get("name", "")
            # Determine result from children
            result = "passed"
            if case.find("failure") is not None:
                result = "failed"
            elif case.find("error") is not None:
                result = "error"
            elif case.find("skipped") is not None:
                result = "skipped"
            out.append({"classname": classname, "name": name, "result": result})
        return out

    def to_csv(self, csv_file: str) -> None:
        rows = self.cases()
        path = Path(csv_file).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["classname", "name", "result"])
            writer.writeheader()
            writer.writerows(rows)
