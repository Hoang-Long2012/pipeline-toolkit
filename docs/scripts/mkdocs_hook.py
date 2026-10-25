VOID_TAGS = {
	"area",
	"base",
	"br",
	"col",
	"embed",
	"hr",
	"img",
	"input",
	"link",
	"meta",
	"param",
	"source",
	"track",
	"wbr",
}

RAW_TAGS = {
	"pre",
	"textarea",
	"script",
	"style",
}


def _tag_name(tag):
	tag = tag.lstrip("<").lstrip("/").strip()

	if not tag:
		return ""

	for index, char in enumerate(tag):
		if char.isspace() or char in "/>":
			return tag[:index].lower()

	return tag.lower()


def _tags(line):
	result = []
	index = 0
	quote = None

	while index < len(line):
		if line[index] != "<":
			index += 1
			continue

		if line.startswith("<!--", index):
			end = line.find("-->", index + 4)

			if end == -1:
				result.append(("comment", False, False))
				break

			index = end + 3
			continue

		end = index + 1
		quote = None

		while end < len(line):
			char = line[end]

			if quote:
				if char == quote:
					quote = None
			elif char in "\"'":
				quote = char
			elif char == ">":
				break

			end += 1

		if end >= len(line):
			break

		value = line[index:end + 1]

		if value.startswith(("<!", "<?")):
			index = end + 1
			continue

		closing = value.startswith("</")
		self_closing = value.rstrip().endswith("/>")
		name = _tag_name(value)

		if name:
			result.append((name, closing, self_closing))

		index = end + 1

	return result


def clean_html_whitespace(output):
	lines = output.splitlines(keepends=True)
	cleaned = []

	level = 0
	raw_tag = None

	for line in lines:
		stripped = line.strip()

		if not stripped:
			if raw_tag:
				cleaned.append(line)

			continue

		if raw_tag:
			cleaned.append(line)

			tags = _tags(line)

			for name, closing, self_closing in tags:
				if closing and name == raw_tag:
					raw_tag = None

			continue

		tags = _tags(line)

		if not tags:
			cleaned.append(line)
			continue

		_first_name, first_closing, _ = tags[0]

		if first_closing:
			level = max(0, level - 1)

		if stripped.startswith("</"):
			indentation = "	 " * level
		else:
			indentation = "	 " * level

		cleaned.append(indentation + stripped)

		for name, closing, self_closing in tags:
			if name in RAW_TAGS and not closing and not self_closing:
				raw_tag = name
				break

			if closing or self_closing or name in VOID_TAGS:
				continue

			level += 1

			if any(
				other_name == name and other_closing
				for other_name, other_closing, _ in tags
			):
				level -= 1

	return "".join(cleaned)


def on_post_page(output, page, config):
	return clean_html_whitespace(output)
