from abc import ABC, abstractmethod
from typing import Iterable, Any, Tuple

from besser.BUML.metamodel.structural import DomainModel, Class, Enumeration, AssociationClass, Generalization, \
    BinaryAssociation


class DomainModelVisitor(ABC):
    @abstractmethod
    def start_model(self, model: DomainModel) -> None:
        pass

    @abstractmethod
    def visit_class(self, class_type: Class, attributes: Iterable[Any], methods: Iterable[Tuple[Any, Iterable[Any]]]) -> None:
        pass

    @abstractmethod
    def visit_enumeration(self, enum_type: Enumeration, literals: Iterable[Any]) -> None:
        pass

    @abstractmethod
    def visit_association_class_link(self, association_class: AssociationClass, end1: Any, end2: Any) -> None:
        pass

    @abstractmethod
    def visit_generalization(self, generalization: Generalization) -> None:
        pass

    @abstractmethod
    def visit_binary_association(self, association: BinaryAssociation, end1: Any, end2: Any) -> None:
        pass

    @abstractmethod
    def end_model(self, model: DomainModel) -> None:
        pass
