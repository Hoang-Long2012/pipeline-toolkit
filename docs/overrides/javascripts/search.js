const observer = new MutationObserver(() => {
	const suggest = document.querySelector(
		"[data-md-component='search-suggest']"
	)

	if (!suggest)
		return

	suggest.setAttribute("aria-live", "polite")
	suggest.setAttribute("aria-atomic", "true")
})

observer.observe(document.body, {
	childList: true,
	subtree: true
})
