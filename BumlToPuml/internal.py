import argparse
import importlib.util
import os
import sys
import uuid
from typing import Any

# Allow running from this repo without installing BESSER globally.
sys.path.append(os.path.join(os.path.dirname(__file__), "../BESSER"))

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural import AssociationClass, BinaryAssociation, Class, DomainModel, Enumeration


def _type_name(type_obj: Any) -> str:
    return type_obj.name if hasattr(type_obj, "name") else str(type_obj)


def _visibility_symbol(value: Any) -> str:
    visibility = str(value) if value else "public"
    return "+" if visibility == "public" else "-" if visibility == "private" else "#" if visibility == "protected" else "~"


def _association_symbol(end1: Any, end2: Any) -> str:
    # Keep output strictly inside the supported relation set.
    if getattr(end2, "is_composite", False):
        return "*--"
    if getattr(end1, "is_composite", False):
        return "--*"

    if getattr(end2, "is_aggregation", False):
        return "o--"
    if getattr(end1, "is_aggregation", False):
        return "--o"

    if getattr(end1, "is_navigable", False) and not getattr(end2, "is_navigable", False):
        return "<--"
    if getattr(end2, "is_navigable", False) and not getattr(end1, "is_navigable", False):
        return "-->"
    return "--"


def load_domain_model(file_path: str) -> DomainModel:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file not found: {file_path}")

    module_name = f"buml_model_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load Python module from path: {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)

    for value in vars(module).values():
        if isinstance(value, DomainModel):
            return value

    for value in vars(module).values():
        if isinstance(value, Project) and value.models:
            return value.models[0]

    raise ValueError("No DomainModel found in the provided file.")


def generate_puml(domain_model: DomainModel) -> str:
    puml_lines = ["@startuml"]

    types = sorted(list(domain_model.types), key=lambda x: x.name)
    associations = sorted(list(domain_model.associations), key=lambda x: x.name)
    generalizations = sorted(
        list(domain_model.generalizations),
        key=lambda x: x.general.name + x.specific.name,
    )

    for item in types:
        if isinstance(item, Class):
            class_prefix = "abstract class" if item.is_abstract else "class"
            puml_lines.append(f"{class_prefix} {item.name} {{")

            attributes = sorted(list(item.attributes), key=lambda x: x.name)
            for attr in attributes:
                puml_lines.append(
                    f"  {_visibility_symbol(getattr(attr, 'visibility', None))} {attr.name} : {_type_name(getattr(attr, 'type', ''))}"
                )

            methods = sorted(list(item.methods), key=lambda x: x.name)
            for method in methods:
                params = []
                for param in sorted(list(getattr(method, "parameters", [])), key=lambda p: getattr(p, "name", "")):
                    params.append(f"{param.name} : {_type_name(getattr(param, 'type', ''))}")
                return_type = _type_name(getattr(method, "type", "void")) if getattr(method, "type", None) else "void"
                puml_lines.append(
                    f"  {_visibility_symbol(getattr(method, 'visibility', None))} {method.name}({', '.join(params)}) : {return_type}"
                )

            puml_lines.append("}")

            if isinstance(item, AssociationClass) and item.association and len(item.association.ends) == 2:
                ends = list(item.association.ends)
                puml_lines.append(f"({_type_name(ends[0].type)}, {_type_name(ends[1].type)}) .. {item.name}")

        elif isinstance(item, Enumeration):
            puml_lines.append(f"enum {item.name} {{")
            literals = sorted(list(item.literals), key=lambda x: x.name)
            for literal in literals:
                puml_lines.append(f"  {literal.name}")
            puml_lines.append("}")

    for gen in generalizations:
        puml_lines.append(f"{gen.general.name} <|-- {gen.specific.name}")

    for assoc in associations:
        if not isinstance(assoc, BinaryAssociation):
            continue

        ends = list(assoc.ends)
        if len(ends) != 2:
            continue

        end1 = ends[0]
        end2 = ends[1]
        type1_name = _type_name(end1.type)
        type2_name = _type_name(end2.type)

        mult1 = getattr(end1, "multiplicity", None)
        mult2 = getattr(end2, "multiplicity", None)
        label1 = f'"{mult1.min}..{mult1.max}"' if mult1 else '""'
        label2 = f'"{mult2.min}..{mult2.max}"' if mult2 else '""'

        rel_symbol = _association_symbol(end1, end2)

        puml_lines.append(f"{type1_name} {label1} {rel_symbol} {label2} {type2_name} : {assoc.name}")

    puml_lines.append("@enduml")
    return "\n".join(puml_lines)


class BUMLToPUMLParser:
    def parse_file(self, file_path: str) -> str:
        domain_model = load_domain_model(file_path)
        return generate_puml(domain_model)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a BUML Python model into PlantUML.")
    parser.add_argument("model_file", help="Path to the BUML Python file")
    parser.add_argument("--output", "-o", help="Optional path to write .puml output")
    args = parser.parse_args()

    try:
        puml_content = BUMLToPUMLParser().parse_file(args.model_file)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    output_path = args.output if args.output else f"{os.path.splitext(args.model_file)[0]}.puml"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(puml_content)

    print(f"Wrote PUML to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

