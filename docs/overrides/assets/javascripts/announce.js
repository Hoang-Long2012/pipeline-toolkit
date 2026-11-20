const announce = document.querySelector(
	"[data-md-component=announce]"
);

if (announce) {
	const content = announce.querySelector(".md-typeset");
	const button = announce.querySelector(".md-banner__button");
	const key = __md_scope.pathname + ".__announce_dismissed";

	const getContent = () => {
		const clone = content.cloneNode(true);
		clone.querySelector(".md-banner__button")?.remove();

		return clone.innerHTML;
	};

	const current = getContent();

	if (localStorage.getItem(key) === current) {
		announce.hidden = true;
	}

	button.addEventListener("click", () => {
		localStorage.setItem(key, getContent());
		announce.hidden = true;
	});
}
