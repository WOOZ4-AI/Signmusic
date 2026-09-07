from typing import Dict, Optional


class SignDefinition:
    """
    Define la representación lingüística de un signo.

    IMPORTANTE:
    Estos datos son una representación interna experimental.
    No deben interpretarse como una descripción oficial de DGS.
    """

    def __init__(
        self,
        concept: str,
        hand_shape: str,
        movement: str,
        location: str,
        description: str = "",
    ):
        self.concept = concept
        self.hand_shape = hand_shape
        self.movement = movement
        self.location = location
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "concept": self.concept,
            "hand_shape": self.hand_shape,
            "movement": self.movement,
            "location": self.location,
            "description": self.description,
        }


# ============================================================
# EXPERIMENTAL DGS LEXICON
# ============================================================
#
# Estos son solamente datos de prueba para desarrollar
# la arquitectura del sistema.
#
# NO representan todavía signos DGS lingüísticamente validados.
# ============================================================

DGS_LEXICON: Dict[str, SignDefinition] = {

    "SAVE": SignDefinition(
        concept="SAVE",
        hand_shape="bent_fingers",
        movement="pull_up",
        location="chest",
        description="Experimental rescue/protection movement",
    ),

    "ME": SignDefinition(
        concept="ME",
        hand_shape="pointing",
        movement="point_to_self",
        location="chest",
        description="Experimental self-reference movement",
    ),

    "YOU": SignDefinition(
        concept="YOU",
        hand_shape="pointing",
        movement="point_forward",
        location="center",
        description="Experimental reference-to-other movement",
    ),

    "HELP": SignDefinition(
        concept="HELP",
        hand_shape="open_hand",
        movement="support_up",
        location="chest",
        description="Experimental support movement",
    ),

    "LOVE": SignDefinition(
        concept="LOVE",
        hand_shape="curved_hands",
        movement="hug_self",
        location="chest",
        description="Experimental affection movement",
    ),

    "LIFE": SignDefinition(
        concept="LIFE",
        hand_shape="bent_fingers",
        movement="upward_spiral",
        location="body",
        description="Experimental life movement",
    ),
}


def get_sign(concept: str) -> Optional[SignDefinition]:
    """
    Obtiene la definición de un concepto.

    La búsqueda es independiente de mayúsculas/minúsculas.
    """

    if not concept:
        return None

    return DGS_LEXICON.get(concept.upper())


def has_sign(concept: str) -> bool:
    """Comprueba si existe una definición para el concepto."""

    return get_sign(concept) is not None