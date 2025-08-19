"""
Universal Test Harness CLI

"""
import os
import time
from pathlib import Path

import click

from typing import Dict
from common_lib.test_harness.runner import TestRunner


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TESTS_DIR = PROJECT_ROOT / "tests"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def print_targets(targets: Dict[str, str]) -> None:
    click.echo("Available targets under ./tests")
    click.echo("---------------------------------")
    click.echo("Index      Name")
    for index, target in targets.items():
        click.echo(f"{index:<10}{target}")


def get_targets(tests_path: str) -> Dict[str, str]:
    """
    Build an index→name mapping for immediate subfolders under tests/.
    """
    p = Path(tests_path)
    counter = 1
    targets: Dict[str, str] = {}
    if p.exists():
        for path in sorted(p.iterdir()):
            if path.is_dir() and not path.name.startswith("__"):
                targets[str(counter)] = path.name
                counter += 1
    return targets


@click.option(
    "--tests-dir",
    default=str(DEFAULT_TESTS_DIR),
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Base directory that contains your target test folders.",
    show_default=True,
)
@click.option(
    "--output-dir",
    default=str(DEFAULT_OUTPUT_DIR),
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Directory where reports (HTML/XML) will be written.",
    show_default=True,
)
@click.option(
    "--run-all",
    is_flag=True,
    help="Run all discovered targets under --tests-dir.",
)
@click.option(
    "--target",
    default=None,
    help="Run a single target folder by name (e.g., task_creation_service).",
    show_default=True,
)
@click.option(
    "--host-index",
    default=lambda: int(os.environ.get("HOST_INDEX", 0)),
    type=int,
    help="Index of a host in ./config.yml. You can also set HOST_INDEX env var.",
    show_default=True,
)
@click.option(
    "-k",
    "--mark",
    default=None,
    help="Pytest -k expression (e.g., smoke or 'not slow').",
    show_default=True,
)
@click.option(
    "-n",
    "--num-procs",
    default=lambda: int(os.environ.get("NUM_PROCS", 0)),
    type=int,
    help="Number of parallel workers (requires pytest-xdist). 0 disables parallelism.",
    show_default=True,
)
@click.command()
def run_tests(
    tests_dir: Path,
    output_dir: Path,
    run_all: bool,
    target: str | None,
    host_index: int,
    mark: str | None,
    num_procs: int,
):
    """
    Command for running pytest targets.

    You can: 
      • run a specific target folder with --target
      • run all targets with --run-all
      • interactively pick a target if neither of the above is provided
    """
    click.echo(f"Tests base: {tests_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = get_targets(str(tests_dir))
    if not targets:
        click.echo(f"No targets found under: {tests_dir}")
        raise SystemExit(1)

    if target and run_all:
        click.echo("Choose either --target or --run-all, not both.")
        raise SystemExit(2)

    if target:
        if target not in targets.values():
            print_targets(targets)
            click.echo(f"Target '{target}' not found under {tests_dir}")
            raise SystemExit(3)
        targets_to_run = [target]
    elif run_all:
        targets_to_run = list(targets.values())
    else:
        print_targets(targets)
        index = click.prompt(
            "Choose target", type=click.Choice(list(targets.keys())), show_choices=False
        )
        targets_to_run = [targets[index]]

    click.echo(f"Running targets: {targets_to_run}")
    start_time = time.time()

    runner = TestRunner(
        tests_path=str(tests_dir),
        output_path=str(output_dir),
        host_index=host_index,
        mark=mark,
        num_processes=num_procs,
    )
    exit_code = runner.run(targets_to_run)

    duration_hours = (time.time() - start_time) / 3600.0
    click.echo(f"--- duration {duration_hours:.3f} Hours ---")
    raise SystemExit(exit_code)
