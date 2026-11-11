from datetime import datetime
from importlib import import_module
from importlib.metadata import version
from inspect import getdoc
from pathlib import Path
from pkgutil import walk_packages

from justhtml import JustHTML
from zoneinfo import ZoneInfo


def on_config(config):
	now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
	config["extra"]["version"] = version("pipeline-toolkit")
	config["extra"]["material_version"] = version("mkdocs-material")
	config["extra"]["deployment_date"] = now.strftime("%Y-%m-%d")
	config["extra"]["deployment_time"] = now.strftime("%H:%M")
	config["nav"].append({"api": {Path(api_file).stem: str(Path(api_file).relative_to("docs")) for api_file in sorted(Path("docs/api").glob("*.md"))}})
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


def find_api(package, name):
	if name in getattr(package, "__all__", ()):
		api = getattr(package, name, None)
		if api is not None:
			return api

	for info in walk_packages(package.__path__, package.__name__ + "."):
		module = import_module(info.name)
		api = getattr(module, name, None)

		if api is not None:
			return api

def on_page_markdown(markdown, page, config, files):
	if not page.file.src_uri.startswith("api/"):
		return markdown

	if "description" in page.meta:
		return markdown

	package = import_module("pipeline")
	name = Path(page.file.src_uri).stem
	api = find_api(package, name)

	if api is None:
		return markdown

	module_name = getattr(api, "__module__", None)
	if module_name is None:
		return markdown

	module = import_module(module_name)
	docstring = getdoc(module)

	if docstring:
		summary = docstring.split("\n\n", 1)[0]
		page.meta["description"] = " ".join(summary.split())

	return markdown


def on_post_page(output, page, config):
	doc = JustHTML(output, sanitize=False)
	return doc.to_html(pretty=True, indent_size=2) + "\n"
