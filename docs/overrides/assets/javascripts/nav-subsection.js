document.querySelectorAll(".md-nav__toggle").forEach(toggle => {
	const label = document.getElementById(`${toggle.id}_label`);

	if (!label) {
		return;
	}

	const update = () => {
		label.setAttribute("aria-expanded", String(toggle.checked));
	};

	toggle.addEventListener("change", update);
	update();
});
