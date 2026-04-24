import argparse
import os
import re
import sys
import types
import uuid

from BumlToPuml.domain_model_walker import DomainModelWalker
from BumlToPuml.domain_model_iterator import DomainModelIterator
from BumlToPuml.plantuml_visitor import PlantUMLVisitor

# Add BESSER to path assuming it is a sibling directory
sys.path.append(os.path.join(os.path.dirname(__file__), "../BESSER"))

from besser.BUML.metamodel.structural import DomainModel
from besser.BUML.metamodel.project import Project


_COMPAT_CONSTRUCTOR_NAMES = ("DomainModel", "Generalization", "Multiplicity")


def _apply_compatibility_rewrites(source: str) -> str:
    """Rewrite known legacy patterns from the dataset to current metamodel APIs."""
    prelude = "import besser.BUML.metamodel.structural as __BUML_structural\n"
    for name in _COMPAT_CONSTRUCTOR_NAMES:
        source = re.sub(
            rf"(?<![\w.]){name}\s*\(",
            f"__BUML_structural.{name}(",
            source,
        )

    return f"{prelude}{source}"


def load_model(file_path: str) -> DomainModel:
    module_name = f"model_module_{uuid.uuid4().hex}"
    module = types.ModuleType(module_name)
    module.__file__ = file_path
    sys.modules[module_name] = module

    source = open(file_path, "r", encoding="utf-8").read()
    source = _apply_compatibility_rewrites(source)

    try:
        exec(compile(source, file_path, "exec"), module.__dict__)
    finally:
        sys.modules.pop(module_name, None)
    
    for var_name, var_value in vars(module).items():
        if isinstance(var_value, DomainModel):
            return var_value
            
    # If not found, look for Project and take the first model
    for var_name, var_value in vars(module).items():
        if isinstance(var_value, Project):
            for candidate_model in var_value.models:
                if isinstance(candidate_model, DomainModel):
                    return candidate_model
                
    raise ValueError("No DomainModel found in the provided file.")


def generate_puml(model: DomainModel) -> str:
    iterator = DomainModelIterator(model)
    visitor = PlantUMLVisitor()
    walker = DomainModelWalker(model, iterator, visitor)
    walker.walk()
    return visitor.to_puml()

def main():
    parser = argparse.ArgumentParser(description="Convert BUML model to PlantUML")
    parser.add_argument("buml_file", help="Path to the BUML file (python script)")
    parser.add_argument("--output", help="Path to the output PUML file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.buml_file):
        print(f"Error: File not found: {args.buml_file}")
        sys.exit(1)
    
    try:
        model = load_model(args.buml_file)
        puml_content = generate_puml(model)
        
        output_file = args.output
        if not output_file:
            base_name = os.path.splitext(args.buml_file)[0]
            output_file = base_name + ".puml"
            
        with open(output_file, "w") as f:
            f.write(puml_content)
            
        print(f"Successfully generated {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

