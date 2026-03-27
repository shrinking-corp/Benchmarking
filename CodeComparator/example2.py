from __future__ import annotations


class smalluml_NamedElement:
    """smalluml::NamedElement"""

    def __init__(self, name: str) -> None:
        self.name = name


class Type:
    """Type"""

    def __init__(self) -> None:
        pass


class NamedElement:
    """NamedElement"""

    def __init__(self) -> None:
        pass


class smalluml_Class(Type):
    """smalluml::Class"""

    def __init__(self) -> None:
        pass


class smalluml_Operation(NamedElement):
    """smalluml::Operation"""

    def __init__(self) -> None:
        pass


class smalluml_Type(NamedElement):
    """smalluml::Type"""

    def __init__(self) -> None:
        pass


class smalluml_TypeString(Type):
    """smalluml::TypeString"""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_TypeReal(Type):
    """smalluml::TypeReal"""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_Property(NamedElement):
    """smalluml::Property"""

    def __init__(self, upperBound: int, lowerBound: int) -> None:
        self.upperBound = upperBound
        self.lowerBound = lowerBound


class smalluml_TypeBoolean(Type):
    """smalluml::TypeBoolean"""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_Root:
    """smalluml::Root"""

    def __init__(self) -> None:
        pass


class smalluml_TypeInteger(Type):
    """smalluml::TypeInteger"""

    def __init__(self, value: str) -> None:
        self.value = value


class smalluml_TypeUnlimitedNatural(Type):
    """smalluml::TypeUnlimitedNatural"""

    def __init__(self, value: str) -> None:
        self.value = value