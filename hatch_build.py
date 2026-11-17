from inspect import cleandoc
from pathlib import Path
from tempfile import TemporaryDirectory

import libcst as cst
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from markdown_it import MarkdownIt
from mdit_plain.renderer import RendererPlain

_MARKDOWN = MarkdownIt("commonmark", renderer_cls=RendererPlain)


def _clean_docstring(owner):
	docstring = owner.get_docstring()
	if docstring is None:
		return owner

	plain_text = _MARKDOWN.render(cleandoc(docstring)).strip()
	body = owner.body
	if isinstance(owner, cst.Module):
		statements = list(body)
	else:
		statements = list(body.body)

	first_statement = statements[0]
	if isinstance(first_statement, (cst.SimpleStatementLine, cst.SimpleStatementSuite)):
		small_statements = list(first_statement.body)
		first = small_statements[0]
		if not isinstance(first, cst.Expr) or not isinstance(first.value, cst.BaseString):
			return owner
		small_statements[0] = first.with_changes(value=cst.SimpleString(repr(plain_text)))
		statements[0] = first_statement.with_changes(body=tuple(small_statements))
	else:
		return owner

	if isinstance(owner, cst.Module):
		return owner.with_changes(body=tuple(statements))
	return owner.with_changes(body=body.with_changes(body=tuple(statements)))


class CleanDocstrings(BuildHookInterface):
	_tempdir = None

	def initialize(self, version, build_data):
		if self.target_name == "wheel" and (Path(self.root) / "PKG-INFO").is_file():
			return

		package_dir = Path(self.root) / "src" / "pipeline"
		if not package_dir.is_dir():
			raise RuntimeError(f"Package source directory not found: {package_dir}")

		self._tempdir = TemporaryDirectory(prefix="pipeline-toolkit-build-")
		output_dir = Path(self._tempdir.name)
		destination_prefix = "pipeline" if self.target_name == "wheel" else "src/pipeline"

		force_include = build_data.setdefault("force_include", {})
		for source in package_dir.rglob("*.py"):
			relative_path = source.relative_to(package_dir)
			tree = cst.parse_module(source.read_text(encoding="utf-8"))
			cleaned_tree = tree.visit(CleanDocstringsTransformer())
			output = output_dir / relative_path
			output.parent.mkdir(parents=True, exist_ok=True)
			output.write_bytes(cleaned_tree.code.encode("utf-8"))
			force_include[str(output)] = (Path(destination_prefix) / relative_path).as_posix()

	def finalize(self, version, build_data, artifact_path):
		if self._tempdir is not None:
			self._tempdir.cleanup()
			self._tempdir = None


class CleanDocstringsTransformer(cst.CSTTransformer):
	def leave_Module(self, original_node, updated_node):
		return _clean_docstring(updated_node)

	def leave_ClassDef(self, original_node, updated_node):
		return _clean_docstring(updated_node)

	def leave_FunctionDef(self, original_node, updated_node):
		return _clean_docstring(updated_node)
