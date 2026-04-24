#!/usr/bin/env python3
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    dataset_root = repo_root / "BESSER-Dataset" / "Dataset"

    model_files = dataset_root.rglob("*_BUML_model.py")
    # missing_count = sum(
    #     1 for model_file in model_files if not model_file.with_suffix(".puml").is_file()
    # )
    for model_file in model_files:
        if not model_file.with_suffix(".puml").is_file():
            print(model_file)

    # print(missing_count)


if __name__ == "__main__":
    main()

