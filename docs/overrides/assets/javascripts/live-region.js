(() => {
	function setupLiveRegion() {
		const dialog = document.querySelector(
			'[data-md-component="dialog"]'
		)

		if (!dialog)
			return

		const liveRegion = dialog.querySelector(".md-typeset")

		if (!liveRegion)
			return

		const descriptor = Object.getOwnPropertyDescriptor(
			Node.prototype,
			"textContent"
		)

		if (!descriptor || !descriptor.get || !descriptor.set)
			return

		const getText = descriptor.get
		const setText = descriptor.set

		let timer

		Object.defineProperty(liveRegion, "textContent", {
		configurable: true,

			get() {
				return getText.call(this)
			},

			set(value) {
				if (!dialog.classList.contains("md-dialog--active")) {
					setText.call(this, value)
					return
				}

				if (timer !== undefined) {
					clearTimeout(timer)
					timer = undefined
				}

				const message = value == null ? "" : String(value)

				if (getText.call(this) !== message) {
					setText.call(this, value)
					return
				}

				setText.call(this, "")

				timer = setTimeout(() => {
					setText.call(this, value)
					timer = undefined
				}, 100)
			}
		})
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", setupLiveRegion, {
			once: true
		})
	} else {
		setupLiveRegion()
	}
})()
