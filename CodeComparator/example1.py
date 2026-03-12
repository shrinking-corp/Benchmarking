from __future__ import annotations

from typing import List, Optional


class Petrinet:
    """Represents a Petri net containing places, transitions, and arcs."""

    def __init__(self, name: str) -> None:
        """
        Initialize a Petrinet instance.

        Args:
            name: The name of the Petri net.
        """
        self.name: str = name
        self.places: List[Place] = []
        self.transitions: List[Transition] = []
        self.arcs: List[PetrinetArc] = []

    def add_place(self, place: Place) -> None:
        """
        Add a place to the Petri net.

        Args:
            place: The place to add.
        """
        if place not in self.places:
            self.places.append(place)
            place.petrinet = self

    def add_transition(self, transition: Transition) -> None:
        """
        Add a transition to the Petri net.

        Args:
            transition: The transition to add.
        """
        if transition not in self.transitions:
            self.transitions.append(transition)
            transition.petrinet = self

    def add_arc(self, arc: PetrinetArc) -> None:
        """
        Add an arc to the Petri net.

        Args:
            arc: The arc to add.
        """
        if arc not in self.arcs:
            self.arcs.append(arc)
            arc.petrinet = self


class PetrinetArc:
    """Represents a generic arc entity in the Petri net model."""

    def __init__(self, weight: int) -> None:
        """
        Initialize a PetrinetArc instance.

        Args:
            weight: The weight of the arc.
        """
        self.weight: int = weight
        self.petrinet: Optional[Petrinet] = None


class Token:
    """Represents a token that belongs to a place."""

    def __init__(self) -> None:
        """Initialize a Token instance."""
        self.place: Optional[Place] = None


class Arc:
    """Base class for arcs connecting places and transitions."""

    def __init__(self) -> None:
        """Initialize an Arc instance."""
        pass


class PTArc(Arc):
    """Represents an arc from a place to a transition."""

    def __init__(
        self,
        place: Optional[Place] = None,
        transition: Optional[Transition] = None,
    ) -> None:
        """
        Initialize a PTArc instance.

        Args:
            place: The source place.
            transition: The target transition.
        """
        super().__init__()
        self.place: Optional[Place] = place
        self.transition: Optional[Transition] = transition


class TPArc(Arc):
    """Represents an arc from a transition to a place."""

    def __init__(
        self,
        transition: Optional[Transition] = None,
        place: Optional[Place] = None,
    ) -> None:
        """
        Initialize a TPArc instance.

        Args:
            transition: The source transition.
            place: The target place.
        """
        super().__init__()
        self.transition: Optional[Transition] = transition
        self.place: Optional[Place] = place


class Place:
    """Represents a place in a Petri net."""

    def __init__(self, name: str) -> None:
        """
        Initialize a Place instance.

        Args:
            name: The name of the place.
        """
        self.name: str = name
        self.petrinet: Optional[Petrinet] = None
        self.tokens: List[Token] = []
        self.outgoing_pt_arcs: List[PTArc] = []
        self.incoming_tp_arcs: List[TPArc] = []

    def getTokenNumber(self) -> int:
        """
        Return the number of tokens in this place.

        Returns:
            The number of tokens.
        """
        return len(self.tokens)

    def isAPart(self) -> bool:
        """
        Check whether this place is part of a Petri net.

        Returns:
            True if the place belongs to a Petri net, otherwise False.
        """
        return self.petrinet is not None

    def add_token(self, token: Token) -> None:
        """
        Add a token to this place.

        Args:
            token: The token to add.
        """
        if token not in self.tokens:
            self.tokens.append(token)
            token.place = self

    def add_outgoing_pt_arc(self, arc: PTArc) -> None:
        """
        Add an outgoing place-to-transition arc.

        Args:
            arc: The arc to add.
        """
        if arc not in self.outgoing_pt_arcs:
            self.outgoing_pt_arcs.append(arc)
            arc.place = self

    def add_incoming_tp_arc(self, arc: TPArc) -> None:
        """
        Add an incoming transition-to-place arc.

        Args:
            arc: The arc to add.
        """
        if arc not in self.incoming_tp_arcs:
            self.incoming_tp_arcs.append(arc)
            arc.place = self


class Transition:
    """Represents a transition in a Petri net."""

    def __init__(self, name: str) -> None:
        """
        Initialize a Transition instance.

        Args:
            name: The name of the transition.
        """
        self.name: str = name
        self.petrinet: Optional[Petrinet] = None
        self.incoming_pt_arcs: List[PTArc] = []
        self.outgoing_tp_arcs: List[TPArc] = []

    def isEnabled(self) -> bool:
        """
        Check whether the transition is enabled.

        A transition is considered enabled if all its incoming places
        have at least as many tokens as required by the corresponding arc.
        Since PTArc does not define a weight in the diagram, each incoming
        arc is treated as requiring at least one token in its source place.

        Returns:
            True if the transition is enabled, otherwise False.
        """
        for arc in self.incoming_pt_arcs:
            if arc.place is None or arc.place.getTokenNumber() < 1:
                return False
        return True

    def add_incoming_pt_arc(self, arc: PTArc) -> None:
        """
        Add an incoming place-to-transition arc.

        Args:
            arc: The arc to add.
        """
        if arc not in self.incoming_pt_arcs:
            self.incoming_pt_arcs.append(arc)
            arc.transition = self

    def add_outgoing_tp_arc(self, arc: TPArc) -> None:
        """
        Add an outgoing transition-to-place arc.

        Args:
            arc: The arc to add.
        """
        if arc not in self.outgoing_tp_arcs:
            self.outgoing_tp_arcs.append(arc)
            arc.transition = self


# Aliases matching the BUML class names more closely if needed.
PetrinetArcBase = Arc