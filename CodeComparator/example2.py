from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class petrinet_Arc:
    """Represents an arc in a Petri net."""

    weight: int = 1


@dataclass
class Arc:
    """Base class for Petri net arcs."""


@dataclass
class petrinet_Token:
    """Represents a token contained in a place."""

    place: Optional[petrinet_Place] = None


@dataclass
class petrinet_PTArc(Arc):
    """Represents an arc from a place to a transition."""

    src: Optional[petrinet_Place] = None
    trg: Optional[petrinet_Transition] = None


@dataclass
class petrinet_TPArc(Arc):
    """Represents an arc from a transition to a place."""

    src: Optional[petrinet_Transition] = None
    trg: Optional[petrinet_Place] = None


@dataclass
class petrinet_Place:
    """Represents a place in a Petri net."""

    name: str
    petrinet: Optional[petrinet_Petrinet] = None
    tokens: List[petrinet_Token] = field(default_factory=list)
    out: List[petrinet_PTArc] = field(default_factory=list)
    in_: List[petrinet_TPArc] = field(default_factory=list)

    def __init__(
        self,
        name: str,
        petrinet: Optional[petrinet_Petrinet] = None,
        tokens: Optional[List[petrinet_Token]] = None,
        out: Optional[List[petrinet_PTArc]] = None,
        in_: Optional[List[petrinet_TPArc]] = None,
    ) -> None:
        """Initialize a place."""
        self.name = name
        self.petrinet = petrinet
        self.tokens = tokens if tokens is not None else []
        self.out = out if out is not None else []
        self.in_ = in_ if in_ is not None else []

    def getTokenNumber(self) -> int:
        """Return the number of tokens currently in the place."""
        return len(self.tokens)

    def isAPart(self) -> bool:
        """Return whether this place belongs to a Petri net."""
        return self.petrinet is not None

    def add_token(self, token: petrinet_Token) -> None:
        """Add a token to this place."""
        token.place = self
        self.tokens.append(token)

    def remove_token(self) -> Optional[petrinet_Token]:
        """Remove and return a token from this place if available."""
        if not self.tokens:
            return None
        token = self.tokens.pop()
        token.place = None
        return token


@dataclass
class petrinet_Transition:
    """Represents a transition in a Petri net."""

    name: str
    petrinet: Optional[petrinet_Petrinet] = None
    in_: List[petrinet_PTArc] = field(default_factory=list)
    out: List[petrinet_TPArc] = field(default_factory=list)

    def __init__(
        self,
        name: str,
        petrinet: Optional[petrinet_Petrinet] = None,
        in_: Optional[List[petrinet_PTArc]] = None,
        out: Optional[List[petrinet_TPArc]] = None,
    ) -> None:
        """Initialize a transition."""
        self.name = name
        self.petrinet = petrinet
        self.in_ = in_ if in_ is not None else []
        self.out = out if out is not None else []

    def isEnabled(self) -> bool:
        """Return whether the transition is enabled."""
        for arc in self.in_:
            if arc.src is None:
                return False
            if arc.src.getTokenNumber() < 1:
                return False
        return True

    def fire(self) -> bool:
        """Fire the transition if enabled, consuming and producing tokens."""
        if not self.isEnabled():
            return False

        for arc in self.in_:
            if arc.src is not None:
                arc.src.remove_token()

        for arc in self.out:
            if arc.trg is not None:
                arc.trg.add_token(petrinet_Token())

        return True


@dataclass
class petrinet_Petrinet:
    """Represents a Petri net."""

    name: str
    places: List[petrinet_Place] = field(default_factory=list)
    transitions: List[petrinet_Transition] = field(default_factory=list)
    arcs: List[petrinet_Arc] = field(default_factory=list)

    def __init__(
        self,
        name: str,
        places: Optional[List[petrinet_Place]] = None,
        transitions: Optional[List[petrinet_Transition]] = None,
        arcs: Optional[List[petrinet_Arc]] = None,
    ) -> None:
        """Initialize a Petri net."""
        self.name = name
        self.places = places if places is not None else []
        self.transitions = transitions if transitions is not None else []
        self.arcs = arcs if arcs is not None else []

        for place in self.places:
            place.petrinet = self
        for transition in self.transitions:
            transition.petrinet = self

    def add_place(self, place: petrinet_Place) -> None:
        """Add a place to the Petri net."""
        place.petrinet = self
        self.places.append(place)

    def add_transition(self, transition: petrinet_Transition) -> None:
        """Add a transition to the Petri net."""
        transition.petrinet = self
        self.transitions.append(transition)

    def add_arc(self, arc: petrinet_Arc) -> None:
        """Add an arc to the Petri net."""
        self.arcs.append(arc)