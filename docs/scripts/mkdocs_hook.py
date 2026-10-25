def on_post_page(output, page, config):
	return "\n".join(
		line.strip() for line in output.splitlines()
		if line.strip()
	)
