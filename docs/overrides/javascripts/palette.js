document.addEventListener("DOMContentLoaded", () => {
	const root = document.querySelector(
		"[data-md-component='custom-palette']"
	);

	if (!root)
		return;

	const button = root.querySelector("[data-palette-button]");
	const menu = root.querySelector("[data-palette-menu]");
	const options = [...root.querySelectorAll("[data-palette-option]")];

	if (!button || !menu || !options.length)
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

		for (const item of options) {
			item.setAttribute(
				"aria-checked",
				item === option ? "true" : "false"
			);
		}

		__md_set("__palette", palette);
	}

	function openMenu() {
		menu.hidden = false;
		button.setAttribute("aria-expanded", "true");

		const selected = options.find(
			option => option.getAttribute("aria-checked") === "true"
		);

		(selected || options[0]).focus();
	}

	function closeMenu() {
		menu.hidden = true;
		button.setAttribute("aria-expanded", "false");
	}

	function toggleMenu() {
		if (menu.hidden)
			openMenu();
		else {
			closeMenu();
			button.focus();
		}
	}

	button.addEventListener("click", toggleMenu);

	button.addEventListener("keydown", event => {
		if (
			event.key === "Enter" ||
			event.key === " "
		) {
			event.preventDefault();
			toggleMenu();
		}

		if (event.key === "ArrowDown") {
			event.preventDefault();
			openMenu();
		}
	});

	options.forEach((option, index) => {
		option.addEventListener("click", () => {
			applyPalette(option);
			closeMenu();
			button.focus();
		});

		option.addEventListener("keydown", event => {
			if (event.key === "ArrowDown") {
				event.preventDefault();
				options[(index + 1) % options.length].focus();
			}

			if (event.key === "ArrowUp") {
				event.preventDefault();
				options[
					(index - 1 + options.length) % options.length
				].focus();
			}

			if (event.key === "Home") {
				event.preventDefault();
				options[0].focus();
			}

			if (event.key === "End") {
				event.preventDefault();
				options.at(-1).focus();
			}

			if (event.key === "Escape") {
				event.preventDefault();
				closeMenu();
				button.focus();
			}
		});
	});

	document.addEventListener("click", event => {
		if (!root.contains(event.target))
			closeMenu();
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