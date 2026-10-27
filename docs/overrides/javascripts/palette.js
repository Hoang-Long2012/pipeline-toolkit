document.addEventListener("DOMContentLoaded", () => {
	const root = document.querySelector(
		"[data-md-component='custom-palette']"
	);

	if (!root)
		return;

	const button = root.querySelector("[data-palette-button]");
	const dialog = root.querySelector("[data-palette-menu]");
	const options = [...root.querySelectorAll("[data-palette-option]")];

	if (!button || !dialog || !options.length)
		return;

	function applyPalette(option) {
		const palette = {
			index: Number(option.dataset.paletteIndex),
			color: {
				media: option.dataset.mdColorMedia,
				scheme: option.dataset.mdColorScheme,
				primary: option.dataset.mdColorPrimary,
				accent: option.dataset.mdColorAccent
			}
		};

		for (const [key, value] of Object.entries(palette.color))
			document.body.setAttribute(`data-md-color-${key}`, value);

		for (const item of options)
			item.checked = item === option;

		__md_set("__palette", palette);
	}

	function openDialog() {
		if (!dialog.open)
			dialog.showModal();

		const selected = options.find(option => option.checked);
		(selected || options[0]).focus();

		button.setAttribute("aria-expanded", "true");
	}

	function closeDialog() {
		if (dialog.open)
			dialog.close();

		button.setAttribute("aria-expanded", "false");
	}

	button.addEventListener("click", () => {
		if (dialog.open)
			closeDialog();
		else
			openDialog();
	});

	options.forEach(option => {
		option.addEventListener("change", () => {
			applyPalette(option);
			closeDialog();
			button.focus();
		});
	});

	dialog.addEventListener("cancel", event => {
		event.preventDefault();
		closeDialog();
		button.focus();
	});

	dialog.addEventListener("click", event => {
		if (event.target === dialog) {
			closeDialog();
			button.focus();
		}
	});

	const saved = __md_get("__palette");

	if (
		saved &&
		Number.isInteger(saved.index) &&
		options[saved.index]
	) {
		applyPalette(options[saved.index]);
	}
	else {
		const media = window.matchMedia(
			"(prefers-color-scheme: light)"
		);

		const index = options.findIndex(
			option => option.dataset.mdColorMedia === (
				media.matches
					? "(prefers-color-scheme: light)"
					: "(prefers-color-scheme: dark)"
			)
		);

		applyPalette(options[index >= 0 ? index : 0]);
	}
});
