"""Stratified 2:1 train/validation split for the BESSER-Dataset.

For each category found dynamically in the dataset, 2/3 of its models go to
training and 1/3 go to validation. The split is reproducible via a fixed
random seed.

Usage:
    python split_dataset.py                          # uses default paths
    python split_dataset.py --dataset-dir ../BESSER-Dataset/Dataset
    python split_dataset.py --dataset-dir ../BESSER-Dataset/Dataset --seed 99
    python split_dataset.py --output-dir my_splits

Outputs (written to --output-dir, default: ./splits):
    train.txt        -- one model folder name per line
    validation.txt   -- one model folder name per line
    split_report.txt -- summary with per-category counts
"""

import argparse
import random
from collections import defaultdict
from pathlib import Path

def load_category(model_dir: Path) -> str:
    """Read the category label for a model folder."""
    category_file = model_dir / "category.txt"
    if not category_file.exists():
        return "unknown"
    return category_file.read_text(encoding="utf-8").strip()


def discover_models(dataset_dir: Path) -> dict[str, list[str]]:
    """Scan dataset_dir and group model folder names by their category.

    Categories are discovered dynamically — no hardcoding needed.

    Returns:
        A dict mapping category -> [model_folder_name, ...]
    """
    categories: dict[str, list[str]] = defaultdict(list)

    # Sort entries so the order is deterministic before the shuffle
    for entry in sorted(dataset_dir.iterdir()):
        if entry.is_dir():
            category = load_category(entry)
            categories[category].append(entry.name)

    return dict(categories)


def stratified_split(
    categories: dict[str, list[str]],
    train_ratio: float = 2 / 3,
    seed: int = 42,
) -> tuple[list[str], list[str]]:
    """Perform a stratified split across all categories.

    For each category the models are shuffled (reproducibly) and then split
    at floor(n * train_ratio).  The leftover always goes to validation so that
    no model is ever duplicated or dropped.

    Returns:
        (train_models, validation_models) -- lists of model folder names.
    """
    rng = random.Random(seed)
    train: list[str] = []
    validation: list[str] = []

    for category, models in sorted(categories.items()):  # sorted for determinism
        shuffled = models[:]
        rng.shuffle(shuffled)

        split_idx = max(1, int(len(shuffled) * train_ratio))

        # A lone model in a category always goes to training
        if len(shuffled) == 1:
            train.extend(shuffled)
        else:
            train.extend(shuffled[:split_idx])
            validation.extend(shuffled[split_idx:])

    return train, validation


def write_splits(
    train: list[str],
    validation: list[str],
    categories: dict[str, list[str]],
    output_dir: Path,
    dataset_dir: Path,
) -> None:
    """Write train.txt, validation.txt, and a human-readable split_report.txt."""
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "train.txt").write_text(
        "\n".join(sorted(train)) + "\n", encoding="utf-8"
    )
    (output_dir / "validation.txt").write_text(
        "\n".join(sorted(validation)) + "\n", encoding="utf-8"
    )

    # Build per-category breakdown for the report
    model_to_category = {
        model: cat for cat, models in categories.items() for model in models
    }
    cat_train: dict[str, int] = defaultdict(int)
    cat_val: dict[str, int] = defaultdict(int)
    for m in train:
        cat_train[model_to_category[m]] += 1
    for m in validation:
        cat_val[model_to_category[m]] += 1

    all_cats = sorted(set(list(cat_train.keys()) + list(cat_val.keys())))
    total_all = len(train) + len(validation)

    lines = [
        "Dataset Split Report",
        "====================",
        f"Dataset directory : {dataset_dir.resolve()}",
        f"Total models      : {total_all}",
        f"Training set      : {len(train)} models  ({len(train) / total_all * 100:.1f}%)",
        f"Validation set    : {len(validation)} models  ({len(validation) / total_all * 100:.1f}%)",
        "",
        f"{'Category':<30} {'Total':>7} {'Train':>7} {'Val':>7} {'Train%':>8}",
        "-" * 65,
    ]
    for cat in all_cats:
        t = cat_train.get(cat, 0)
        v = cat_val.get(cat, 0)
        total = t + v
        pct = t / total * 100 if total else 0
        lines.append(f"{cat:<30} {total:>7} {t:>7} {v:>7} {pct:>7.1f}%")

    lines += [
        "-" * 65,
        f"{'TOTAL':<30} {total_all:>7} {len(train):>7} {len(validation):>7}",
    ]

    report = "\n".join(lines) + "\n"
    (output_dir / "split_report.txt").write_text(report, encoding="utf-8")
    print(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stratified 2:1 train/validation split of the BESSER-Dataset."
    )
    parser.add_argument(
        "--dataset-dir",
        default=str(Path(__file__).parent.parent / "BESSER-Dataset" / "Dataset"),
        help="Path to the Dataset folder containing model_N subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).parent / "splits"),
        help="Directory where output files are written (default: ./splits).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=2 / 3,
        help="Fraction of each category assigned to training (default: 2/3).",
    )
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    print(f"Scanning dataset: {dataset_dir}")
    categories = discover_models(dataset_dir)
    total = sum(len(v) for v in categories.values())
    print(f"Found {total} models across {len(categories)} categories.\n")

    train, validation = stratified_split(
        categories, train_ratio=args.train_ratio, seed=args.seed
    )

    output_dir = Path(args.output_dir)
    write_splits(train, validation, categories, output_dir, dataset_dir)
    print(f"Split files written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()