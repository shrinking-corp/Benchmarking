# Code Comparator using CodeBLEU

A Python utility to compare two Python files and calculate their similarity using the CodeBLEU metric.

## Overview

CodeBLEU is a metric designed to evaluate generated code by combining four complementary scores:
- **N-gram match (BLEU)**: Lexical similarity based on n-gram overlap
- **Weighted N-gram match**: Weighted version of n-gram match
- **AST (syntax) match**: Abstract Syntax Tree similarity (structural similarity)
- **Data-flow match**: Logic similarity based on data-flow information

The final CodeBLEU score is a weighted combination of these four scores, correlating better with human evaluation than BLEU alone.

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
python main.py <file_path_1> <file_path_2>
```

**Example:**
```bash
python main.py file1.py file2.py
```

This will output:
```
CodeBLEU Similarity Score: 0.5530

Detailed Metrics:
  CodeBLEU Score: 0.5530
  N-gram Match Score: 0.0234
  Weighted N-gram Match Score: 0.0267
  Syntax Match Score (AST): 1.0000
  Data-flow Match Score: 0.7500
```

### Programmatic Usage

```python
from main import compare_python_files

# Get only the CodeBLEU score
similarity_score = compare_python_files('file1.py', 'file2.py')
print(f"Similarity: {similarity_score:.4f}")

# Get detailed metrics
metrics = compare_python_files('file1.py', 'file2.py', return_full_metrics=True)
print(f"CodeBLEU: {metrics['codebleu']:.4f}")
print(f"Syntax Match: {metrics['syntax_match_score']:.4f}")
print(f"Data-flow Match: {metrics['dataflow_match_score']:.4f}")
```

## Function Documentation

### `compare_python_files(file_path_1, file_path_2, return_full_metrics=False)`

Compare two Python files using CodeBLEU metric.

**Parameters:**
- `file_path_1` (str or Path): Path to the first Python file
- `file_path_2` (str or Path): Path to the second Python file
- `return_full_metrics` (bool): If True, returns all metrics; if False, returns only CodeBLEU score

**Returns:**
- If `return_full_metrics` is False: `float` - CodeBLEU similarity score (0.0 to 1.0)
- If `return_full_metrics` is True: `dict` with keys:
  - `codebleu`: final CodeBLEU score
  - `ngram_match_score`: n-gram match score
  - `weighted_ngram_match_score`: weighted n-gram match score
  - `syntax_match_score`: AST similarity
  - `dataflow_match_score`: logic similarity

**Raises:**
- `FileNotFoundError`: If either file does not exist
- `IOError`: If there's an error reading the files

## Example

```python
# Create test files
with open('file1.py', 'w') as f:
    f.write('''def sum(a, b):
    return a + b
''')

with open('file2.py', 'w') as f:
    f.write('''def add(x, y):
    return x + y
''')

# Compare them
score = compare_python_files('file1.py', 'file2.py')
print(f"Similarity: {score:.4f}")  # Output: Similarity: 0.5120
```

## What CodeBLEU Measures

| Metric | What It Measures | Range |
|--------|-----------------|-------|
| N-gram Match | Lexical overlap (word sequences) | 0.0 - 1.0 |
| Weighted N-gram Match | Importance-weighted lexical overlap | 0.0 - 1.0 |
| Syntax Match (AST) | Structural/syntactic similarity | 0.0 - 1.0 |
| Data-flow Match | Logic/semantic similarity | 0.0 - 1.0 |
| **CodeBLEU** | **Weighted combination of above** | **0.0 - 1.0** |

## Interpretation

- **CodeBLEU = 1.0**: Files are identical
- **CodeBLEU > 0.7**: Very similar (same logic, minor changes)
- **CodeBLEU 0.4-0.7**: Moderately similar (similar structure, different variable names)
- **CodeBLEU < 0.4**: Quite different
- **CodeBLEU = 0.0**: Completely different

## Dependencies

- `codebleu`: Core CodeBLEU metric implementation
- `tree-sitter-python`: Python language parser for AST extraction

## Project Structure

```
CodeComparator/
├── main.py              # Main implementation
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── venv/               # Virtual environment (created after setup)
└── README.md           # This file
```

## Troubleshooting

### "Tree-sitter language for python not available"
Make sure `tree-sitter-python` is installed:
```bash
pip install tree-sitter-python==0.23.0
```

### Version Compatibility
This project uses:
- `codebleu` from GitHub (latest version)
- `tree-sitter-python==0.23.0` (for compatibility)

If you encounter version conflicts, try:
```bash
pip uninstall -y codebleu tree-sitter tree-sitter-python
pip install -r requirements.txt
```

## License

This utility uses the CodeBLEU metric. See the [CodeBLEU GitHub repository](https://github.com/k4black/codebleu) for license information.

## References

- CodeBLEU GitHub: https://github.com/k4black/codebleu
- CodeBLEU Paper: "CodeBLEU: a Method for Automatic Evaluation of Code Synthesis"

