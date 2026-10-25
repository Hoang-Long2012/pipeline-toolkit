from justhtml import JustHTML


def on_post_page(output, page, config):
	doc = JustHTML(output, sanitize=False)
	return doc.to_html(pretty=True, indent_size=2) + "\n"
