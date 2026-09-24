from __future__ import annotations

import pathlib

import pytest

from scripts.check_release_version import validate_release_version


def _write_versions(root: pathlib.Path, project_version: str, package_version: str) -> None:
    (root / "src/model_router").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "model-routers"\nversion = "{project_version}"\n',
        encoding="utf-8",
    )
    (root / "src/model_router/__init__.py").write_text(
        f'__version__ = "{package_version}"\n',
        encoding="utf-8",
    )


def test_matching_release_versions_are_accepted(tmp_path: pathlib.Path) -> None:
    _write_versions(tmp_path, "1.2.3", "1.2.3")

    assert validate_release_version("v1.2.3", tmp_path) == "1.2.3"


def test_mismatched_package_version_is_rejected(tmp_path: pathlib.Path) -> None:
    _write_versions(tmp_path, "1.2.3", "1.2.4")

    with pytest.raises(ValueError, match="Version mismatch"):
        validate_release_version("v1.2.3", tmp_path)


def test_mismatched_release_tag_is_rejected(tmp_path: pathlib.Path) -> None:
    _write_versions(tmp_path, "1.2.3", "1.2.3")

    with pytest.raises(ValueError, match="must equal"):
        validate_release_version("1.2.3", tmp_path)
