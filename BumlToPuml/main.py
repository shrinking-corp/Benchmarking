# buml_to_puml.py

import argparse
import importlib.util
import os
import sys
from typing import List

# Add BESSER to path assuming it is a sibling directory
sys.path.append(os.path.join(os.path.dirname(__file__), "../BESSER"))

from besser.BUML.metamodel.structural import DomainModel, Class, Enumeration, BinaryAssociation, Generalization, Property, DataType, PrimitiveDataType, AssociationClass
from besser.BUML.metamodel.project import Project


def load_model(file_path: str) -> DomainModel:
    spec = importlib.util.spec_from_file_location("model_module", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["model_module"] = module
    spec.loader.exec_module(module)
    
    for var_name, var_value in vars(module).items():
        if isinstance(var_value, DomainModel):
            return var_value
            
    # If not found, look for Project and take the first model
    for var_name, var_value in vars(module).items():
        if isinstance(var_value, Project):
            if var_value.models:
                return var_value.models[0]
                
    raise ValueError("No DomainModel found in the provided file.")

def generate_puml(model: DomainModel) -> str:
    puml_lines = ["@startuml"]
    
    # Sort elements for deterministic output
    types = sorted([t for t in model.types], key=lambda x: x.name)
    associations = sorted([a for a in model.associations], key=lambda x: x.name)
    generalizations = sorted([g for g in model.generalizations], key=lambda x: x.general.name + x.specific.name)
    
    # Classes and Enums
    for t in types:
        if isinstance(t, Class):
            if t.is_abstract:
                puml_lines.append(f"abstract class {t.name} {{")
            else:
                puml_lines.append(f"class {t.name} {{")
                
            # Attributes
            attributes = sorted(list(t.attributes), key=lambda x: x.name)
            for attr in attributes:
                visibility = "+" if attr.visibility == "public" else "-" if attr.visibility == "private" else "#" if attr.visibility == "protected" else "~"
                type_name = attr.type.name if hasattr(attr.type, 'name') else str(attr.type)
                puml_lines.append(f"  {visibility} {attr.name} : {type_name}")
            
            # Methods
            methods = sorted(list(t.methods), key=lambda x: x.name)
            for method in methods:
                 visibility = "+" if method.visibility == "public" else "-" if method.visibility == "private" else "#" if method.visibility == "protected" else "~"
                 params = ", ".join([f"{p.name} : {p.type.name if hasattr(p.type, 'name') else str(p.type)}" for p in method.parameters])
                 return_type = method.type.name if method.type and hasattr(method.type, 'name') else str(method.type) if method.type else "void"
                 puml_lines.append(f"  {visibility} {method.name}({params}) : {return_type}")
            
            puml_lines.append("}")
            
            # Association Class Link
            if isinstance(t, AssociationClass):
                if t.association and len(t.association.ends) == 2:
                    ends = list(t.association.ends)
                    type1_name = ends[0].type.name if hasattr(ends[0].type, "name") else str(ends[0].type)
                    type2_name = ends[1].type.name if hasattr(ends[1].type, "name") else str(ends[1].type)
                    puml_lines.append(f"({type1_name}, {type2_name}) .. {t.name}")
            
        elif isinstance(t, Enumeration):
            puml_lines.append(f"enum {t.name} {{")
            literals = sorted(list(t.literals), key=lambda x: x.name)
            for lit in literals:
                puml_lines.append(f"  {lit.name}")
            puml_lines.append("}")

    # Generalizations
    for gen in generalizations:
        puml_lines.append(f"{gen.general.name} <|-- {gen.specific.name}")

    # Associations
    for assoc in associations:
        if isinstance(assoc, BinaryAssociation):
            ends = list(assoc.ends)
            if len(ends) == 2:
                end1 = ends[0]
                end2 = ends[1]
                
                type1_name = end1.type.name if hasattr(end1.type, "name") else str(end1.type)
                type2_name = end2.type.name if hasattr(end2.type, "name") else str(end2.type)
                
                label1 = f'"{end1.multiplicity.min}..{end1.multiplicity.max}"'
                label2 = f'"{end2.multiplicity.min}..{end2.multiplicity.max}"'
                
                # Default relationship
                rel_symbol = "--"
                
                # Check for composition
                if end2.is_composite:
                   # Type1 is Whole. Type2 is Part (as end2 points to Type2).
                   # Diamond on Left (Type1).
                   style = "*"
                   line = "--"
                   head = ""
                   if end2.is_navigable:
                       head = ">"
                   rel_symbol = f"{style}{line}{head}"
                   
                elif end1.is_composite:
                   # Type2 is Whole. Type1 is Part.
                   # Diamond on Right (Type2).
                   style = "*"
                   line = "--"
                   head = ""
                   if end1.is_navigable:
                       head = "<"
                   rel_symbol = f"{head}{line}{style}"
                   
                else:
                    # No composition
                     if end1.is_navigable and end2.is_navigable:
                         rel_symbol = "--" # Bi-directional
                     elif end1.is_navigable:
                         rel_symbol = "<--" # Type2 -> Type1
                     elif end2.is_navigable:
                         rel_symbol = "-->" # Type1 -> Type2
                     else:
                         rel_symbol = "--" 
                
                puml_lines.append(f'{type1_name} {label1} {rel_symbol} {label2} {type2_name} : {assoc.name}')
    
    puml_lines.append("@enduml")
    return "\n".join(puml_lines)

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

