import builtins

if hasattr(builtins, "sentinel"):
	_DEFAULT = builtins.sentinel("_DEFAULT")
else:
	_DEFAULT = object()