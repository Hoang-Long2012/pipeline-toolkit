import os
import sys
import xml.etree.ElementTree as ET


def main():
	report = "coverage.xml"

	if not os.path.isfile(report):
		print("Coverage report not found.", file=sys.stderr)
		return 1

	try:
		root = ET.parse(report).getroot()
	except ET.ParseError as error:
		print(f"Invalid coverage report: {error}", file=sys.stderr)
		return 1

	files = []

	for element in root.findall(".//class"):
		filename = element.get("filename")
		line_rate = float(element.get("line-rate", 0))
		lines_valid = int(element.get("lines-valid", 0))
		lines_covered = int(element.get("lines-covered", 0))

		if filename is None:
			continue

		if line_rate < 1:
			files.append({
				"filename": filename,
				"coverage": line_rate * 100,
				"missing": lines_valid - lines_covered,
			})

	files.sort(key=lambda item: item["filename"])

	lines = [
		"## Test Coverage",
		"",
		"| File | Coverage | Missing |",
		"| --- | ---: | ---: |",
	]

	for item in files:
		lines.append(
			f"| `{item['filename']}` "
			f"| {item['coverage']:.2f}% "
			f"| {item['missing']} |"
		)

	rate = float(root.get("line-rate", 0)) * 100
	valid = int(root.get("lines-valid", 0))
	covered = int(root.get("lines-covered", 0))
	missing = valid - covered

	lines.extend([
		f"| **Total** | **{rate:.2f}%** | **{missing}** |",
		"",
	])

	summary = os.environ.get("GITHUB_STEP_SUMMARY")

	if not summary:
		print("\n".join(lines))
		return 0

	try:
		with open(summary, "a", encoding="utf-8") as file:
			file.write("\n".join(lines))
	except OSError as error:
		print(f"Could not write coverage summary: {error}", file=sys.stderr)
		return 1

	return 0


if __name__ == "__main__":
	sys.exit(main())
