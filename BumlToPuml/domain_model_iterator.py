from typing import Iterator, Any, Optional, Tuple

from besser.BUML.metamodel.structural import DomainModel, Class, Enumeration, Generalization, BinaryAssociation, \
    AssociationClass

from BumlToPuml.utils import _type_name


class DomainModelIterator:
    def __init__(self, model: DomainModel):
        self.model = model

    def iter_types(self) -> Iterator[Any]:
        yield from sorted(list(self.model.types), key=lambda item: _type_name(item))

    def iter_attributes(self, class_type: Class) -> Iterator[Any]:
        yield from sorted(list(class_type.attributes), key=lambda item: _type_name(item))

    def iter_methods(self, class_type: Class) -> Iterator[Any]:
        yield from sorted(list(class_type.methods), key=lambda item: _type_name(item))

    def iter_parameters(self, method: Any) -> Iterator[Any]:
        yield from sorted(list(getattr(method, "parameters", [])), key=lambda item: _type_name(item))

    def iter_literals(self, enum_type: Enumeration) -> Iterator[Any]:
        yield from sorted(list(enum_type.literals), key=lambda item: _type_name(item))

    def iter_generalizations(self) -> Iterator[Generalization]:
        yield from sorted(
            list(self.model.generalizations),
            key=lambda item: f"{_type_name(item.general)}::{_type_name(item.specific)}",
        )

    def iter_binary_associations(self) -> Iterator[BinaryAssociation]:
        associations = [assoc for assoc in self.model.associations if isinstance(assoc, BinaryAssociation)]
        yield from sorted(associations, key=lambda item: _type_name(item))

    def ordered_ends(self, association: Any) -> Optional[Tuple[Any, Any]]:
        ends = list(getattr(association, "ends", []))
        if len(ends) != 2:
            return None

        def end_key(end: Any) -> Tuple[str, str, str, str, bool, bool, bool]:
            multiplicity = getattr(end, "multiplicity", None)
            return (
                _type_name(getattr(end, "type", "")),
                str(getattr(end, "name", "")),
                str(getattr(multiplicity, "min", "")),
                str(getattr(multiplicity, "max", "")),
                bool(getattr(end, "is_navigable", False)),
                bool(getattr(end, "is_composite", False)),
                bool(getattr(end, "is_aggregation", False)),
            )

        ordered = sorted(ends, key=end_key)
        return ordered[0], ordered[1]

    def iter_association_class_links(self) -> Iterator[Tuple[AssociationClass, Any, Any]]:
        for model_type in self.iter_types():
            if not isinstance(model_type, AssociationClass):
                continue
            association = getattr(model_type, "association", None)
            if association is None:
                continue
            ordered = self.ordered_ends(association)
            if ordered is None:
                continue
            yield model_type, ordered[0], ordered[1]
