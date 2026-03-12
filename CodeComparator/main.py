"""
Code Comparator using CodeBLEU

This module provides functionality to compare two Python files and calculate
their similarity using CodeBLEU metric.
"""

from pathlib import Path
from typing import Union, Dict, Any
from codebleu import calc_codebleu


def compare_python_files(file_path_1: Union[str, Path], 
                        file_path_2: Union[str, Path],
                        return_full_metrics: bool = False) -> Union[float, Dict[str, Any]]:
    """
    Compare two Python files using CodeBLEU metric.
    
    This function reads two Python files, extracts their code, and compares them
    using CodeBLEU, which combines:
    - n-gram match (BLEU)
    - weighted n-gram match
    - AST (syntax) match
    - data-flow match
    
    Args:
        file_path_1: Path to the first Python file
        file_path_2: Path to the second Python file
        return_full_metrics: If True, returns all metrics; if False, returns only CodeBLEU score
    
    Returns:
        If return_full_metrics is False:
            float: CodeBLEU similarity score (0.0 to 1.0)
        If return_full_metrics is True:
            Dict with keys:
                - codebleu: final CodeBLEU score
                - ngram_match_score: n-gram match score
                - weighted_ngram_match_score: weighted n-gram match score
                - syntax_match_score: AST similarity
                - dataflow_match_score: logic similarity
    
    Raises:
        FileNotFoundError: If either file does not exist
        IOError: If there's an error reading the files
    """
    
    # Convert to Path objects for easier handling
    path_1 = Path(file_path_1)
    path_2 = Path(file_path_2)
    
    # Validate that files exist
    if not path_1.exists():
        raise FileNotFoundError(f"File not found: {file_path_1}")
    if not path_2.exists():
        raise FileNotFoundError(f"File not found: {file_path_2}")
    
    # Read the code from both files
    try:
        with open(path_1, 'r', encoding='utf-8') as f:
            code_1 = f.read()
    except IOError as e:
        raise IOError(f"Error reading file {file_path_1}: {e}")
    
    try:
        with open(path_2, 'r', encoding='utf-8') as f:
            code_2 = f.read()
    except IOError as e:
        raise IOError(f"Error reading file {file_path_2}: {e}")
    
    # Calculate CodeBLEU score using CodeBLEU library
    # Treating code_1 as reference and code_2 as prediction
    result = calc_codebleu(
        references=[code_1],
        predictions=[code_2],
        lang="python"
    )
    
    if return_full_metrics:
        return result
    else:
        return result['codebleu']


def main():
    """
    Main function to demonstrate the code comparator.
    """
    import sys
    
    # # Check command line arguments
    # if len(sys.argv) < 3:
    #     print("Usage: python main.py <file_path_1> <file_path_2>")
    #     print("\nExample: python main.py file1.py file2.py")
    #     sys.exit(1)
    #
    # file_path_1 = sys.argv[1]
    # file_path_2 = sys.argv[2]
    file_path_1 = "example1.py"
    file_path_2 = "example2.py"
    
    try:
        # Get the similarity score
        similarity_score = compare_python_files(file_path_1, file_path_2)
        print(f"CodeBLEU Similarity Score: {similarity_score:.4f}")
        
        # Optionally, get full metrics
        full_metrics = compare_python_files(file_path_1, file_path_2, return_full_metrics=True)
        print("\nDetailed Metrics:")
        print(f"  CodeBLEU Score: {full_metrics['codebleu']:.4f}")
        print(f"  N-gram Match Score: {full_metrics['ngram_match_score']:.4f}")
        print(f"  Weighted N-gram Match Score: {full_metrics['weighted_ngram_match_score']:.4f}")
        print(f"  Syntax Match Score (AST): {full_metrics['syntax_match_score']:.4f}")
        print(f"  Data-flow Match Score: {full_metrics['dataflow_match_score']:.4f}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()



