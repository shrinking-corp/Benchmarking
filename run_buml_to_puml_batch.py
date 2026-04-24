from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import traceback

# Make sibling BESSER package importable for BumlToPuml internals.
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "BESSER"))

from BumlToPuml.main import generate_puml, load_model


@dataclass
class ConversionResult:
	total: int
	succeeded: int
	failed: int


def find_buml_models(dataset_root: Path) -> list[Path]:
	"""Return all BUML Python model files in deterministic order."""
	return sorted(dataset_root.rglob("*_BUML_model.py"))


def convert_all(dataset_root: Path, errors_log: Path) -> ConversionResult:
	model_files = find_buml_models(dataset_root)
	succeeded = 0

	errors_log.write_text("", encoding="utf-8")

	with errors_log.open("a", encoding="utf-8") as err_fh:
		for model_file in model_files:
			output_file = model_file.with_suffix(".puml")
			try:
				model = load_model(str(model_file))
				puml_content = generate_puml(model)
				output_file.write_text(puml_content, encoding="utf-8")
				succeeded += 1
			except Exception:
				err_fh.write(f"[{model_file}]\n")
				err_fh.write(traceback.format_exc())
				err_fh.write("\n")

	total = len(model_files)
	failed = total - succeeded
	return ConversionResult(total=total, succeeded=succeeded, failed=failed)


def write_summary(summary_path: Path, result: ConversionResult, dataset_root: Path) -> None:
	summary = (
		"BUML to PUML batch conversion summary\n"
		f"Dataset root: {dataset_root}\n"
		f"Total models found: {result.total}\n"
		f"Succeeded: {result.succeeded}\n"
		f"Failed: {result.failed}\n"
	)
	summary_path.write_text(summary, encoding="utf-8")


def main() -> None:
	repo_root = REPO_ROOT
	dataset_root = repo_root / "BESSER-Dataset" / "Dataset"
	summary_path = repo_root / "buml_to_puml_summary.txt"
	errors_log = repo_root / "buml_to_puml_errors.log"

	if not dataset_root.exists():
		raise FileNotFoundError(f"Dataset not found: {dataset_root}")

	result = convert_all(dataset_root, errors_log)
	write_summary(summary_path, result, dataset_root)

	print(f"Total models found: {result.total}")
	print(f"Succeeded: {result.succeeded}")
	print(f"Failed: {result.failed}")
	print(f"Summary: {summary_path}")
	print(f"Errors: {errors_log}")


if __name__ == "__main__":
	main()


