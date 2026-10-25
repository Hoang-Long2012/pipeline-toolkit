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
	"script",
	"style",
	"textarea",
}


def _tag_name(value):
	value = value.lstrip("<").lstrip("/").strip()

	if not value:
		return ""

	for index, char in enumerate(value):
		if char.isspace() or char in "/>":
			return value[:index].lower()

	return value.lower()


def _find_tags(line):
	tags = []
	index = 0

	while index < len(line):
		if line[index] != "<":
			index += 1
			continue

		if line.startswith("<!--", index):
			end = line.find("-->", index + 4)

			if end == -1:
				break

			index = end + 3
			continue

		end = index + 1
		quote = None

		while end < len(line):
			char = line[end]

			if quote is not None:
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

		if value.startswith("<!") or value.startswith("<?"):
			index = end + 1
			continue

		closing = value.startswith("</")
		self_closing = value.rstrip().endswith("/>")
		name = _tag_name(value)

		if name:
			tags.append((name, closing, self_closing))

		index = end + 1

	return tags


def _raw_state(tags, raw_tag):
	for name, closing, self_closing in tags:
		if name != raw_tag:
			continue

		if closing:
			return None

		if not self_closing:
			return raw_tag

	return raw_tag


def clean_html_whitespace(output):
	lines = output.splitlines(keepends=True)

	cleaned = []
	stack = []
	raw_tag = None

	for line in lines:
		stripped = line.strip()

		if raw_tag is not None:
			cleaned.append(line)

			if f"</{raw_tag}>" in line.lower():
				raw_tag = None

			continue

		if not stripped:
			continue

		tags = _find_tags(line)

		if not tags:
			cleaned.append(line)
			continue

		# A line beginning with a closing tag belongs to the
		# parent level rather than the element being closed.
		first_name, first_closing, _ = tags[0]

		if first_closing and stack and stack[-1] == first_name:
			stack.pop()

		cleaned.append("\t" * len(stack) + stripped)

		for name, closing, self_closing in tags:
			if name in RAW_TAGS:
				if closing or self_closing:
					continue

				raw_tag = name
				continue

			if name in VOID_TAGS or self_closing:
				continue

			if closing:
				if stack and stack[-1] == name:
					stack.pop()

				continue

			stack.append(name)

	return "".join(cleaned)


def on_post_page(output, page, config):
	return clean_html_whitespace(output)
