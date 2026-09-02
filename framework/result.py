from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class AssertionFailure(Exception):
    pass


@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str = ""


class TestResults:
    def __init__(self):
        self.results: list[TestResult] = []

    def add(self, result: TestResult):
        self.results.append(result)

    @property
    def passed(self):
        return sum(r.status == TestStatus.PASS for r in self.results)

    @property
    def failed(self):
        return sum(r.status == TestStatus.FAIL for r in self.results)

    @property
    def errors(self):
        return sum(r.status == TestStatus.ERROR for r in self.results)

    @property
    def total(self):
        return len(self.results)

    def summary(self):
        print()
        print("────────────────────────────────────")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Errors: {self.errors}")
        print(f"Total:  {self.total}")
        print("────────────────────────────────────")
