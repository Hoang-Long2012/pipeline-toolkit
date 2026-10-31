from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from justhtml import JustHTML
from zoneinfo import ZoneInfo


def on_config(config):
	now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
	config["extra"]["version"] = version("pipeline-toolkit")
	config["extra"]["material_version"] = version("mkdocs-material")
	config["extra"]["deployment_date"] = now.strftime("%Y-%m-%d")
	config["extra"]["deployment_time"] = now.strftime("%H:%M")
	return config


def on_pre_build(config):
	root = Path(config["config_file_path"]).parent
	docs_dir = Path(config["docs_dir"])

	changelog_src = root / "CHANGELOG.md"
	changelog_dest = docs_dir / "changelog.md"
	if changelog_src.exists():
		content = "---\nhide:\n  - toc\n---\n" + changelog_src.read_text(encoding="utf-8")
		if not changelog_dest.exists() or changelog_dest.read_text(encoding="utf-8") != content:
			changelog_dest.write_text(content, encoding="utf-8")

	contributing_src = root / "CONTRIBUTING.md"
	contributing_dest = docs_dir / "contributing.md"
	if contributing_src.exists():
		content = contributing_src.read_text(encoding="utf-8")
		if not contributing_dest.exists() or contributing_dest.read_text(encoding="utf-8") != content:
			contributing_dest.write_text(content, encoding="utf-8")


def on_post_page(output, page, config):
	doc = JustHTML(output, sanitize=False)
	return doc.to_html(pretty=True, indent_size=2) + "\n"
