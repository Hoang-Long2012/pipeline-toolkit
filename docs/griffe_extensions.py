import griffe


class PreferExportedAliases(griffe.Extension):
	def on_package(self, *, pkg, **kwargs):
		if not pkg.exports:
			return

		for exported_name in pkg.exports:
			name = getattr(exported_name, "name", exported_name)
			member = pkg.members.get(name)

			if member is None or not member.is_module:
				continue

			target = member.members.get(name)

			if target is None or target.is_module:
				continue

			alias = griffe.Alias(
				name,
				target,
				runtime=True,
				parent=pkg,
				analysis="static",
			)
			alias.public = True
			pkg.set_member(name, alias)