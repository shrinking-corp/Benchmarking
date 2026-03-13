import os
from besser.BUML.metamodel.structural import DomainModel
from besser.BUML.notations.structuralPlantUML import plantuml_to_buml

model_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(model_dir, "test.plantuml")
modeltest: DomainModel = plantuml_to_buml(plantUML_model_path=model_path)

classes = modeltest.classes_sorted_by_inheritance()

for cls in classes:
    print(cls.name)


# chat gpt 5.4 thinking lets gooo
def domain_model_to_puml(domain_model) -> str:
    lines: list[str] = ["@startuml"]

    primitive_map = {
        "int": "int",
        "str": "str",
        "bool": "bool",
        "float": "float",
        "datetime": "datetime",
        "date": "date",
        "time": "time",
        "timedelta": "timedelta",
        "any": "any",
    }

    def type_name(t) -> str:
        # Adjust this if your metamodel uses singleton primitive objects
        name = getattr(t, "name", str(t))
        return primitive_map.get(name, name)

    def multiplicity_to_str(mult) -> str:
        if mult is None:
            return ""
        lower = getattr(mult, "lower", None)
        upper = getattr(mult, "upper", None)

        def fmt(v):
            if v in (None, "*"):
                return "*"
            return str(v)

        if lower is None and upper is None:
            return ""
        if lower == upper:
            return fmt(lower)
        return f"{fmt(lower)}..{fmt(upper)}"

    # --- Enums ---
    enums = sorted(domain_model.get_enumerations(), key=lambda e: e.name)
    for enum in enums:
        lines.append(f"enum {enum.name} {{")
        for lit in sorted(getattr(enum, "literals", []), key=lambda l: l.name):
            lines.append(f"  {lit.name}")
        lines.append("}")
        lines.append("")

    # --- Classes ---
    classes = sorted(domain_model.get_classes(), key=lambda c: c.name)
    for cls in classes:
        lines.append(f"class {cls.name} {{")

        for attr in sorted(getattr(cls, "attributes", []), key=lambda a: a.name):
            lines.append(f"  + {attr.name}: {type_name(attr.type)}")

        for method in sorted(getattr(cls, "methods", []), key=lambda m: m.name):
            params = []
            for p in sorted(getattr(method, "parameters", []), key=lambda p: p.name):
                piece = f"{p.name}: {type_name(p.type)}"
                if getattr(p, "default_value", None) is not None:
                    piece += (
                        f' = "{p.default_value}"'
                        if isinstance(p.default_value, str)
                        else f" = {p.default_value}"
                    )
                params.append(piece)

            ret_type = getattr(method, "type", None)
            suffix = f": {type_name(ret_type)}" if ret_type is not None else ""
            lines.append(f"  + {method.name}({', '.join(params)}){suffix}")

        lines.append("}")
        lines.append("")

    # --- Generalizations ---
    for gen in sorted(
        domain_model.generalizations, key=lambda g: (g.specific.name, g.general.name)
    ):
        lines.append(f"{gen.specific.name} --|> {gen.general.name}")
    if domain_model.generalizations:
        lines.append("")

    # --- Associations ---
    for assoc in sorted(domain_model.associations, key=lambda a: a.name):
        ends = list(getattr(assoc, "ends", []))
        if len(ends) != 2:
            # Skip non-binary associations in this simple serializer
            continue

        end1, end2 = ends[0], ends[1]

        mult1 = multiplicity_to_str(getattr(end1, "multiplicity", None))
        mult2 = multiplicity_to_str(getattr(end2, "multiplicity", None))

        left = end1.type.name
        right = end2.type.name

        left_mult = f' "{mult1}"' if mult1 else ""
        right_mult = f' "{mult2}"' if mult2 else ""

        # Use the association name as the PlantUML label.
        # You could also use an end name if that better matches your original source.
        lines.append(f"{left}{left_mult} --{right_mult} {right}: {assoc.name}")

    lines.append("@enduml")
    return "\n".join(lines)


lines = domain_model_to_puml(modeltest)
print(lines)
