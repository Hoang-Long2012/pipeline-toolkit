import prettierfier

def on_post_page(output, page, config):
	return prettierfier.prettify_html(output)
