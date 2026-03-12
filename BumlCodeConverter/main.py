"""
BUML to Python Code Generator using OpenAI API

Reads a BUML file and generates Python code from the class diagram using ChatGPT.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_python_code_from_buml(
    buml_file_path: str,
    target_directory: str = "target",
    api_key: str = None
) -> str:
    """
    Convert BUML file to Python code using OpenAI API.
    
    Args:
        buml_file_path (str): Path to the BUML Python file
        target_directory (str): Output directory for generated code
        api_key (str): OpenAI API key (optional, loads from .env if not provided)
    
    Returns:
        str: Path to the generated code file
    """
    # Validate input
    if not os.path.exists(buml_file_path):
        raise FileNotFoundError(f"BUML file not found: {buml_file_path}")
    
    # Get API key
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. "
            "Please set OPENAI_API_KEY in .env file or pass it as argument."
        )
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Read BUML file content
    print(f"Reading BUML file: {buml_file_path}")
    with open(buml_file_path, 'r', encoding='utf-8') as f:
        buml_content = f.read()
    
    # Create prompt with BUML content
    prompt = f"""You are a Python code generator. Based on the following BUML class diagram, generate clean, well-structured Python code that implements all the classes with their attributes and methods.

BUML CLASS DIAGRAM:
{buml_content}

REQUIREMENTS:
1. Generate Python classes for each class in the diagram
2. Include all attributes with proper type hints
3. Include all methods with proper signatures
4. Add a __init__ method to initialize attributes
5. Add appropriate docstrings
6. Use Python best practices and PEP 8 style
7. Only output the Python code, no explanations

Generate the complete Python code:"""
    
    # Call OpenAI API
    print("Sending request to OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        # max_tokens=4000
    )
    
    generated_code = response.choices[0].message.content
    
    # Clean up markdown formatting if present
    if generated_code.startswith("```"):
        # Remove markdown code block markers
        lines = generated_code.split('\n')
        # Remove first line if it's ```python or ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove last line if it's ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        generated_code = '\n'.join(lines)
    
    # Create target directory
    Path(target_directory).mkdir(parents=True, exist_ok=True)
    
    # Save generated code
    buml_filename = os.path.splitext(os.path.basename(buml_file_path))[0]
    output_filename = f"{buml_filename}_generated.py"
    output_path = os.path.join(target_directory, output_filename)
    
    print(f"Saving generated code to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(generated_code)
    
    print(f"✓ Code generation completed successfully!")
    return output_path


if __name__ == "__main__":

    
    buml_file = "sample.py"
    target_dir = "target"
    
    try:
        output_file = generate_python_code_from_buml(buml_file, target_dir)
        print(f"\nGenerated code saved to: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)





