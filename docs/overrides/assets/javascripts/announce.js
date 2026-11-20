const announce = document.querySelector(
	"[data-md-component=announce]"
);

if (announce) {
	const button = announce.querySelector(".md-banner__button");
	const content = announce.querySelector(".md-typeset");

	button.addEventListener("click", () => {
		const hash = __md_hash(content.innerHTML);

		__md_set("__announce", hash);
		announce.hidden = true;
	});
}
