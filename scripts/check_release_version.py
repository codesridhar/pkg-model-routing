"""Validate that a release tag agrees with both package version declarations."""

from __future__ import annotations

import argparse
import ast
import pathlib


def _project_version(pyproject_path: pathlib.Path) -> str:
    in_project = False
    for raw_line in pyproject_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("["):
            in_project = line == "[project]"
            continue
        if not in_project or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        if key.strip() != "version":
            continue
        parsed = ast.literal_eval(value.strip())
        if isinstance(parsed, str):
            return parsed
        break
    raise ValueError(f"No string project.version found in {pyproject_path}")


def _package_version(init_path: pathlib.Path) -> str:
    module = ast.parse(init_path.read_text(encoding="utf-8"))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets
        ):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.value.value
    raise ValueError(f"No string __version__ assignment found in {init_path}")


def validate_release_version(tag: str, root: pathlib.Path) -> str:
    """Return the release version or raise when the declarations disagree."""

    project_version = _project_version(root / "pyproject.toml")
    package_version = _package_version(root / "src/model_router/__init__.py")
    expected_tag = f"v{project_version}"

    if package_version != project_version:
        raise ValueError(
            f"Version mismatch: pyproject={project_version}, package={package_version}"
        )
    if tag != expected_tag:
        raise ValueError(f"Release tag {tag!r} must equal {expected_tag!r}")
    return project_version


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag", help="GitHub release tag, such as v0.1.0")
    args = parser.parse_args()
    try:
        version = validate_release_version(args.tag, pathlib.Path.cwd())
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Validated release v{version}")


if __name__ == "__main__":
    main()
