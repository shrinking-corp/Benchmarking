from pathlib import Path
from collections import defaultdict
import ast

def extract_num_of_classes(model_dir: Path) -> int:
    metadata_file = model_dir / "metadata.txt"
    if not metadata_file.exists():
        return 0
    metadate_text = metadata_file.read_text(encoding='utf-8')
    metadata = ast.literal_eval(metadate_text)
    return int(metadata.get("classes", 0))

def foo(dataset_dir: Path):
    result = defaultdict(list)
    for model_dir in dataset_dir.iterdir():
        if model_dir.is_dir():
            num_of_classes = extract_num_of_classes(model_dir)
            result[num_of_classes].append(model_dir.name)
    return result

def print_result(dict):
    total_num = sum([len(val) for val in dict.values()])
    print(total_num)

    for key, values in sorted(dict.items()):
        print(f"{key: >3}: {len(values): <3}: {round(len(values) / total_num * 100, 2)}")

def main() -> None:
    model_dir = Path(__file__).parent.parent / "BESSER-Dataset" / "Dataset"
    data = foo(model_dir)
    print_result(data)

if __name__ == "__main__":
    main()