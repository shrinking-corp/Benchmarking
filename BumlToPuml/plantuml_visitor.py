from typing import List, Any, Iterable, Tuple

from besser.BUML.metamodel.structural import DomainModel, Class, Enumeration, AssociationClass, Generalization, \
    BinaryAssociation

from BumlToPuml.domain_model_visitor import DomainModelVisitor
from BumlToPuml.utils import _type_name


class PlantUMLVisitor(DomainModelVisitor):
    SUPPORTED_RELATIONS = {
        "-->",
        "<--",
        "--|>",
        "<|--",
        "..>",
        "<..",
        "--o",
        "o--",
        "--*",
        "*--",
        "--",
        "..",
    }

    def __init__(self):
        self.lines: List[str] = []

    @staticmethod
    def _visibility_symbol(value: Any) -> str:
        visibility = str(value) if value else "public"
        return "+" if visibility == "public" else "-" if visibility == "private" else "#" if visibility == "protected" else "~"

    @staticmethod
    def _association_symbol(end1: Any, end2: Any) -> str:
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

    @staticmethod
    def _multiplicity_label(end: Any) -> str:
        multiplicity = getattr(end, "multiplicity", None)
        if multiplicity is None:
            return '""'
        return f'"{getattr(multiplicity, "min", "")}..{getattr(multiplicity, "max", "")}"'

    def start_model(self, model: DomainModel) -> None:
        self.lines.append("@startuml")

    def visit_class(self, class_type: Class, attributes: Iterable[Any], methods: Iterable[Tuple[Any, Iterable[Any]]]) -> None:
        class_prefix = "abstract class" if class_type.is_abstract else "class"
        self.lines.append(f"{class_prefix} {class_type.name} {{")

        for attr in attributes:
            attr_type = _type_name(getattr(attr, "type", ""))
            self.lines.append(f"  {self._visibility_symbol(getattr(attr, 'visibility', None))} {attr.name} : {attr_type}")

        for method, parameters in methods:
            params = [f"{param.name} : {_type_name(getattr(param, 'type', ''))}" for param in parameters]
            return_type = _type_name(getattr(method, "type", "void")) if getattr(method, "type", None) else "void"
            self.lines.append(
                f"  {self._visibility_symbol(getattr(method, 'visibility', None))} {method.name}({', '.join(params)}) : {return_type}"
            )

        self.lines.append("}")

    def visit_enumeration(self, enum_type: Enumeration, literals: Iterable[Any]) -> None:
        self.lines.append(f"enum {enum_type.name} {{")
        for literal in literals:
            self.lines.append(f"  {literal.name}")
        self.lines.append("}")

    def visit_association_class_link(self, association_class: AssociationClass, end1: Any, end2: Any) -> None:
        self.lines.append(f"({_type_name(end1.type)}, {_type_name(end2.type)}) .. {association_class.name}")

    def visit_generalization(self, generalization: Generalization) -> None:
        self.lines.append(f"{generalization.general.name} <|-- {generalization.specific.name}")

    def visit_binary_association(self, association: BinaryAssociation, end1: Any, end2: Any) -> None:
        type1_name = _type_name(end1.type)
        type2_name = _type_name(end2.type)
        label1 = self._multiplicity_label(end1)
        label2 = self._multiplicity_label(end2)
        symbol = self._association_symbol(end1, end2)
        if symbol not in self.SUPPORTED_RELATIONS:
            symbol = "--"
        assoc_name = str(getattr(association, "name", ""))

        if assoc_name:
            self.lines.append(f"{type1_name} {label1} {symbol} {label2} {type2_name} : {assoc_name}")
        else:
            self.lines.append(f"{type1_name} {label1} {symbol} {label2} {type2_name}")

    def end_model(self, model: DomainModel) -> None:
        self.lines.append("@enduml")

    def to_puml(self) -> str:
        return "\n".join(self.lines)
