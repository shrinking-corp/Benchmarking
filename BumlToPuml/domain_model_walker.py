from typing import List, Tuple, Any, Iterable

from besser.BUML.metamodel.structural import DomainModel, Class, Enumeration

from BumlToPuml.domain_model_visitor import DomainModelVisitor
from BumlToPuml.domain_model_iterator import DomainModelIterator


class DomainModelWalker:
    def __init__(self, model: DomainModel, iterator: DomainModelIterator, visitor: DomainModelVisitor):
        self.model = model
        self.iterator = iterator
        self.visitor = visitor

    def walk(self) -> None:
        self.visitor.start_model(self.model)

        for model_type in self.iterator.iter_types():
            if isinstance(model_type, Class):
                methods_with_params: List[Tuple[Any, Iterable[Any]]] = []
                for method in self.iterator.iter_methods(model_type):
                    methods_with_params.append((method, self.iterator.iter_parameters(method)))
                self.visitor.visit_class(model_type, self.iterator.iter_attributes(model_type), methods_with_params)
            elif isinstance(model_type, Enumeration):
                self.visitor.visit_enumeration(model_type, self.iterator.iter_literals(model_type))

        for association_class, end1, end2 in self.iterator.iter_association_class_links():
            self.visitor.visit_association_class_link(association_class, end1, end2)

        for generalization in self.iterator.iter_generalizations():
            self.visitor.visit_generalization(generalization)

        for association in self.iterator.iter_binary_associations():
            ordered = self.iterator.ordered_ends(association)
            if ordered is None:
                continue
            self.visitor.visit_binary_association(association, ordered[0], ordered[1])

        self.visitor.end_model(self.model)
