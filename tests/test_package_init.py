"""Tests for package initialization and Python compatibility."""
import builtins
from importlib import metadata, reload
from importlib.metadata import PackageNotFoundError

import pipeline
from pipeline import _compat


def test_package_version_falls_back_when_distribution_is_missing(monkeypatch):
	def missing_distribution(_name):
		raise PackageNotFoundError

	monkeypatch.setattr(metadata, "version", missing_distribution)
	try:
		reload(pipeline)
		assert pipeline.__version__ == "0.0.0-dev0"
	finally:
		monkeypatch.undo()
		reload(pipeline)


def test_compat_default_uses_builtin_sentinel_when_available(monkeypatch):
	created = []

	def sentinel(name):
		created.append(name)
		return object()

	monkeypatch.setattr(builtins, "sentinel", sentinel, raising=False)
	try:
		reload(_compat)
		assert created == ["_DEFAULT"]
	finally:
		monkeypatch.delattr(builtins, "sentinel")
		reload(_compat)
