const observer = new MutationObserver(() => {
	const suggest = document.querySelector(
		"[data-md-component='search-suggest']"
	)

	if (!suggest)
		return

	suggest.setAttribute("aria-live", "polite")
	suggest.setAttribute("aria-atomic", "true")

	const content = suggest.textContent
		.replace(/\u200B/g, "")
		.trim()

	suggest.hidden = !content
})

observer.observe(document.body, {
	childList: true,
	subtree: true
})
