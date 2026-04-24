from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Iterator, Tuple


class DatasetSplit(Enum):
    TRAIN = "train"
    VALIDATION = "validation"


class DatasetIterator(Iterator[Tuple[str, str]]):
    def __init__(self, split: DatasetSplit, workspace_root: str | Path | None = None) -> None:
        if not isinstance(split, DatasetSplit):
            raise TypeError("split must be DatasetSplit.TRAIN or DatasetSplit.VALIDATION")

        root = Path(workspace_root) if workspace_root else Path(__file__).resolve().parent.parent
        self._root = root
        self._dataset_dir = self._root / "BESSER-Dataset" / "Dataset"

        split_file_name = "train.txt" if split is DatasetSplit.TRAIN else "validation.txt"
        split_file = self._root / "divider" / split_file_name
        self._models = self._read_model_names(split_file)
        self._index = 0

    def __iter__(self) -> "DatasetIterator":
        return self

    def __next__(self) -> Tuple[str, str]:
        return self.next()

    def next(self) -> Tuple[str, str]:
        if self.is_done():
            raise StopIteration

        model_name = self._models[self._index]
        self._index += 1

        python_code_path, puml_path = self._resolve_model_files(model_name)
        return python_code_path.read_text(encoding="utf-8"), puml_path.read_text(encoding="utf-8")

    def is_done(self) -> bool:
        return self._index >= len(self._models)

    @staticmethod
    def _read_model_names(split_file: Path) -> list[str]:
        if not split_file.is_file():
            raise FileNotFoundError(f"Split file not found: {split_file}")

        return [line.strip() for line in split_file.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _resolve_model_files(self, model_name: str) -> tuple[Path, Path]:
        model_dir = self._dataset_dir / model_name
        if not model_dir.is_dir():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")

        puml_path = self._pick_puml_file(model_dir)
        python_code_path = self._pick_python_code_file(model_dir)
        return python_code_path, puml_path

    @staticmethod
    def _pick_puml_file(model_dir: Path) -> Path:
        puml_candidates = sorted(model_dir.glob("*.puml"))
        if not puml_candidates:
            raise FileNotFoundError(f"No .puml file found in: {model_dir}")

        preferred = [p for p in puml_candidates if p.name.endswith("_BUML_model.puml")]
        if len(preferred) == 1:
            return preferred[0]

        if len(puml_candidates) == 1:
            return puml_candidates[0]

        raise FileNotFoundError(
            f"Unable to pick a single .puml file in {model_dir}. Candidates: {[p.name for p in puml_candidates]}"
        )

    @staticmethod
    def _pick_python_code_file(model_dir: Path) -> Path:
        python_code_path = model_dir / "python_code.py"
        if not python_code_path.is_file():
            raise FileNotFoundError(f"python_code.py not found in: {model_dir}")
        return python_code_path


if __name__ == "__main__":
    print("TRAIN subset:")
    for python_code_content, puml_content in DatasetIterator(DatasetSplit.TRAIN):
        print(f"PYTHON: {python_code_content[:100]!r} | PUML: {puml_content[:100]!r}")

    print("\nVALIDATION subset:")
    for python_code_content, puml_content in DatasetIterator(DatasetSplit.VALIDATION):
        print(f"PYTHON: {python_code_content[:100]!r} | PUML: {puml_content[:100]!r}")
