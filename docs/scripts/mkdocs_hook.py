def clean_html_whitespace(output):
	lines = output.splitlines(keepends=True)
	cleaned = []

	protected = False

	for line in lines:
		stripped = line.strip()
		lower = line.lower()

		if not protected and not stripped:
			continue

		cleaned.append(line)

		if not protected and "<pre" in lower:
			protected = True

		if protected and "</pre>" in lower:
			protected = False

		if not protected and "<textarea" in lower:
			protected = True

		if protected and "</textarea>" in lower:
			protected = False

	return "".join(cleaned)


def on_post_page(output, page, config):
	return clean_html_whitespace(output)
