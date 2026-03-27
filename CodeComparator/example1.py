from __future__ import annotations


class smalluml_Class(Type):
    """Class smalluml::Class."""

    def __init__(self) -> None:
        pass


class Type:
    """Class Type."""

    def __init__(self) -> None:
        pass


class smalluml_Operation(NamedElement):
    """Class smalluml::Operation."""

    def __init__(self) -> None:
        pass


class NamedElement:
    """Class NamedElement."""

    def __init__(self) -> None:
        pass


class smalluml_Type(NamedElement):
    """Class smalluml::Type."""

    def __init__(self) -> None:
        pass


class smalluml_NamedElement:
    """Class smalluml::NamedElement."""

    def __init__(self, name: str) -> None:
        self.name = name


class smalluml_TypeString(Type):
    """Class smalluml::TypeString."""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_TypeReal(Type):
    """Class smalluml::TypeReal."""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_Property(NamedElement):
    """Class smalluml::Property."""

    def __init__(self, upperBound: int, lowerBound: int) -> None:
        self.upperBound = upperBound
        self.lowerBound = lowerBound


class smalluml_TypeBoolean(Type):
    """Class smalluml::TypeBoolean."""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_Root:
    """Class smalluml::Root."""

    def __init__(self) -> None:
        pass


class smalluml_TypeInteger(Type):
    """Class smalluml::TypeInteger."""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_TypeUnlimitedNatural(Type):
    """Class smalluml::TypeUnlimitedNatural."""

    def __init__(self, value: str) -> None:
        self.value = value