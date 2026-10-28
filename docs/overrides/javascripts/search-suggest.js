const observer = new MutationObserver(() => {
	const suggest = document.querySelector(
		"[data-md-component='search-suggest']"
	)

	if (!suggest)
		return

	suggest.setAttribute("aria-live", "polite")
	suggest.setAttribute("aria-atomic", "true")

	console.log(
		JSON.stringify(suggest.textContent),
		[...suggest.textContent].map(char => char.codePointAt(0).toString(16))
	)
})

observer.observe(document.body, {
	childList: true,
	subtree: true
})
