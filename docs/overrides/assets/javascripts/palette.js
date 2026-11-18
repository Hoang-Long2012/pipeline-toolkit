document.addEventListener("DOMContentLoaded", () => {
	const root = document.querySelector(
		"[data-md-component='custom-palette']"
	);

	if (!root)
		return;

	const button = root.querySelector("[data-palette-button]");
	const dialog = root.querySelector("[data-palette-menu]");
	const closeButton = root.querySelector("[data-palette-close]");
	const options = [...root.querySelectorAll("[data-palette-option]")];

	if (!button || !dialog || !options.length)
		return;

	const systemMedia = window.matchMedia(
		"(prefers-color-scheme)"
	);

	const lightMedia = window.matchMedia(
		"(prefers-color-scheme: light)"
	);

	const systemOption = options.find(
		option => option.dataset.mdColorMedia ===
			"(prefers-color-scheme)"
	);

	function getSystemPalette() {
		const media = lightMedia.matches
			? "(prefers-color-scheme: light)"
			: "(prefers-color-scheme: dark)";

		return options.find(
			option => option.dataset.mdColorMedia === media
		) || systemOption;
	}

	function applyPalette(option, save = false) {
		const selected = {
			index: Number(option.dataset.paletteIndex),
			color: {
				media: option.dataset.mdColorMedia,
				scheme: option.dataset.mdColorScheme,
				primary: option.dataset.mdColorPrimary,
				accent: option.dataset.mdColorAccent
			}
		};

		const applied = option === systemOption
			? getSystemPalette()
			: option;

		if (!applied)
			return;

		for (const key of ["media", "scheme", "primary", "accent"])
			document.body.setAttribute(
				`data-md-color-${key}`,
				applied.dataset[`mdColor${key[0].toUpperCase()}${key.slice(1)}`]
			);

		for (const item of options)
			item.checked = item === option;

		if (save)
			__md_set("__palette", selected);
	}

	function openDialog() {
		if (!dialog.open)
			dialog.showModal();

		const selected = options.find(option => option.checked);
		(selected || options[0]).focus();
	}

	function closeDialog() {
		if (dialog.open)
			dialog.close();
	}

	button.addEventListener("click", () => {
		if (dialog.open)
			closeDialog();
		else
			openDialog();
	});

	closeButton?.addEventListener("click", () => {
		closeDialog();
		button.focus();
	});

	options.forEach(option => {
		option.addEventListener("change", () => {
			applyPalette(option, true);
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

	systemMedia.addEventListener("change", () => {
		const selected = options.find(option => option.checked);

		if (selected === systemOption)
			applyPalette(systemOption);
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
		applyPalette(systemOption || getSystemPalette());
	}
});
