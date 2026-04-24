#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import statistics
from pathlib import Path

try:
    import tiktoken  # pip install tiktoken
except ImportError:
    tiktoken = None


def resolve_dataset_dir(user_value: str) -> Path:
    """Resolve dataset path from several likely locations."""
    raw = Path(user_value)
    candidates = [
        raw,
        Path.cwd() / raw,
        Path(__file__).resolve().parent / raw,
        Path(__file__).resolve().parent.parent / raw,
    ]
    for p in candidates:
        if p.exists() and p.is_dir():
            return p.resolve()
    raise FileNotFoundError(
        f"Dataset directory not found: '{user_value}'. "
        "Pass --dataset-dir explicitly."
    )


def count_words(text: str) -> int:
    # Words are non-whitespace sequences.
    return len(re.findall(r"\S+", text))


def get_encoder(model: str, encoding: str):
    """Return a tiktoken encoder if available, else None."""
    if tiktoken is None:
        return None

    if encoding:
        return tiktoken.get_encoding(encoding)

    # Try model-specific encoding first; fallback to cl100k_base.
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, encoder) -> int:
    """Count tokens using tiktoken encoder, fallback to word-like approximation."""
    if encoder is not None:
        return len(encoder.encode(text))
    # Fallback approximation if tiktoken is not installed.
    return count_words(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count word/character/token stats for all PUML files in dataset."
    )
    parser.add_argument(
        "--dataset-dir",
        default="BESSER-Dataset/Dataset",
        help="Path to dataset root containing model_* folders (default: BESSER-Dataset/Dataset)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model name for tokenization mapping (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--encoding",
        default="",
        help="Explicit tiktoken encoding name (e.g., cl100k_base). Overrides --model.",
    )
    parser.add_argument(
        "--print-per-file",
        action="store_true",
        help="Print per-file words/chars/tokens.",
    )
    args = parser.parse_args()

    dataset_dir = resolve_dataset_dir(args.dataset_dir)
    puml_files = sorted(dataset_dir.rglob("*.puml"))

    if not puml_files:
        print(f"No .puml files found under: {dataset_dir}")
        return

    encoder = get_encoder(args.model, args.encoding)
    using_fallback = encoder is None

    word_counts = []
    char_counts = []
    token_counts = []

    for puml_file in puml_files:
        text = puml_file.read_text(encoding="utf-8", errors="ignore")

        words = count_words(text)
        chars = len(text)
        tokens = count_tokens(text, encoder)

        word_counts.append(words)
        char_counts.append(chars)
        token_counts.append(tokens)

        if args.print_per_file:
            rel_path = puml_file.relative_to(dataset_dir)
            print(f"{rel_path}: words={words}, chars={chars}, tokens={tokens}")

    file_count = len(puml_files)

    avg_words = sum(word_counts) / file_count
    med_words = statistics.median(word_counts)

    avg_chars = sum(char_counts) / file_count
    med_chars = statistics.median(char_counts)

    avg_tokens = sum(token_counts) / file_count
    med_tokens = statistics.median(token_counts)

    print("PUML Dataset Statistics")
    print("-----------------------")
    print(f"Dataset directory: {dataset_dir}")
    print(f"PUML files found:  {file_count}")
    print()
    print(f"Average words:      {avg_words:.2f}")
    print(f"Median words:       {med_words:.2f}")
    print(f"Average characters: {avg_chars:.2f}")
    print(f"Median characters:  {med_chars:.2f}")
    print(f"Average tokens:     {avg_tokens:.2f}")
    print(f"Median tokens:      {med_tokens:.2f}")

    if using_fallback:
        print()
        print(
            "Warning: tiktoken is not installed. Token counts are approximated "
            "using word count. Install tiktoken for model-accurate token counts."
        )


if __name__ == "__main__":
    main()
