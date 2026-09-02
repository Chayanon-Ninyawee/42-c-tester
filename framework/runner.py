import importlib.util
from pathlib import Path

from .builder import BuildError, create_builder
from .c import CContext
from .color import Color, color
from .result import AssertionFailure, TestResult, TestResults, TestStatus


class TestSuite:
    def __init__(self, name: str):
        self.name = name
        self.tests = []

    def case(self, name: str):
        def decorator(function):
            self.tests.append((name, function))
            return function

        return decorator

    def run(
        self,
        context: CContext,
        results: TestResults,
    ):
        print()
        print(color(self.name, Color.BOLD, Color.CYAN))

        for name, function in self.tests:
            if context.debug:
                print("\n")
                print(color(f"[DEBUG] {name}", Color.CYAN))

            try:
                function(context)

                if context.debug:
                    print(f"  {color('[PASS]', Color.GREEN)}")
                else:
                    print(f"  {color('[PASS]', Color.GREEN)} " f"{name}")

                results.add(
                    TestResult(
                        name=name,
                        status=TestStatus.PASS,
                    )
                )

            except AssertionFailure as error:
                if context.debug:
                    print(f"  {color('[FAIL]', Color.RED)}")
                else:
                    print(f"  {color('[FAIL]', Color.RED)} " f"{name}")

                for line in str(error).splitlines():
                    print(f"         {color(line, Color.RED)}")

                results.add(
                    TestResult(
                        name=name,
                        status=TestStatus.FAIL,
                        message=str(error),
                    )
                )

            except Exception as error:
                if context.debug:
                    print(f"  {color('[ERROR]', Color.MAGENTA)} " f"{error}")
                else:
                    print(f"  {color('[ERROR]', Color.MAGENTA)} " f"{name}: {error}")

                results.add(
                    TestResult(
                        name=name,
                        status=TestStatus.ERROR,
                        message=str(error),
                    )
                )


def get_framework_dir():
    return Path(__file__).resolve().parent.parent


def get_project_definition(
    project_name: str,
):
    return get_framework_dir() / "projects" / project_name / "project.py"


def load_project(project_name: str):
    project_file = get_project_definition(project_name)

    if not project_file.exists():
        raise FileNotFoundError(
            f"Unknown project: {project_name}\n"
            f"Missing project definition:\n"
            f"  {project_file}"
        )

    spec = importlib.util.spec_from_file_location(
        f"project_{project_name}",
        project_file,
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load project definition: " f"{project_file}")

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    if not hasattr(module, "project"):
        raise ValueError(f"{project_file} must define " "a 'project' variable")

    return module.project


def load_test(test_file: Path):
    spec = importlib.util.spec_from_file_location(
        test_file.stem,
        test_file,
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {test_file}")

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


def find_test_files(
    project,
):
    test_dir = get_framework_dir() / "projects" / project.name / "tests"

    if not test_dir.exists():
        return []

    test_files = []

    for test_name in project.tests:
        test_file = test_dir / f"test_{test_name}.py"

        if not test_file.exists():
            raise FileNotFoundError(
                f"Test '{test_name}' is listed in the project "
                f"definition but does not exist:\n"
                f"  {test_file}"
            )

        test_files.append(test_file)

    return test_files


def run_project(
    project_name: str,
    project_dir: Path,
    selected_tests: list[str],
    debug: bool = False,
):
    project = load_project(project_name)

    project.directory = project_dir

    print(
        color(
            "42 C Tester",
            Color.BOLD,
            Color.CYAN,
        )
    )
    print(
        color(
            "────────────────────────────────────",
            Color.CYAN,
        )
    )

    print(f"{color('Project:', Color.BOLD)}   " f"{project.name}")

    print(f"{color('Directory:', Color.BOLD)} " f"{project_dir}")

    print()

    print(color("Building...", Color.BOLD, Color.YELLOW))

    try:
        builder = create_builder(
            project_dir,
            project.build,
        )

        builder.build()

    except BuildError as error:
        print()
        print(
            color(
                f"[BUILD ERROR] {error}",
                Color.BOLD,
                Color.RED,
            )
        )
        return

    test_files = find_test_files(project)

    if selected_tests:
        selected = set(selected_tests)

        test_files = [
            path for path in test_files if path.stem.removeprefix("test_") in selected
        ]

    if not test_files:
        print()
        print(
            color(
                "No tests found.",
                Color.YELLOW,
            )
        )
        return

    context = CContext(
        project_dir,
        project.functions,
        debug=debug,
    )

    results = TestResults()

    for test_file in test_files:
        module = load_test(test_file)

        if not hasattr(
            module,
            "suite",
        ):
            print(
                color(
                    f"[WARNING] " f"{test_file.name} " "has no suite",
                    Color.YELLOW,
                )
            )
            continue

        module.suite.run(
            context,
            results,
        )

    print()
    print(
        color(
            "────────────────────────────────────",
            Color.CYAN,
        )
    )

    print(f"{color('Passed:', Color.GREEN)} " f"{results.passed}")

    print(f"{color('Failed:', Color.RED)} " f"{results.failed}")

    print(f"{color('Errors:', Color.MAGENTA)} " f"{results.errors}")

    print(f"{color('Total:', Color.BOLD)}  " f"{results.total}")

    print(
        color(
            "────────────────────────────────────",
            Color.CYAN,
        )
    )
