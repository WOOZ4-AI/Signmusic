from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HandShape:
    """
    Configuración de una mano.

    Los valores concretos podrán ampliarse cuando
    incorporemos datos lingüísticos reales.
    """

    shape: Optional[str] = None
    fingers: Dict[str, Any] = field(
        default_factory=dict
    )
    thumb: Optional[str] = None


@dataclass
class Orientation:
    """
    Orientación de la mano.
    """

    palm: Optional[str] = None
    wrist: Optional[str] = None
    fingers: Optional[str] = None


@dataclass
class Location:
    """
    Ubicación del signo respecto al cuerpo.
    """

    body_region: Optional[str] = None
    side: Optional[str] = None
    height: Optional[str] = None


@dataclass
class Movement:
    """
    Movimiento utilizado durante el signo.
    """

    type: Optional[str] = None
    direction: Optional[str] = None
    path: Optional[str] = None
    repetition: int = 1
    speed: Optional[str] = None


@dataclass
class NonManualFeatures:
    """
    Componentes no manuales del signo.

    Pueden incluir expresión facial, cabeza,
    mirada y otros componentes lingüísticos.
    """

    facial_expression: Optional[str] = None
    eyebrow_position: Optional[str] = None
    eye_gaze: Optional[str] = None
    head_movement: Optional[str] = None
    mouth_pattern: Optional[str] = None


@dataclass
class SignSource:
    """
    Información sobre la procedencia de los datos.
    """

    name: Optional[str] = None
    url: Optional[str] = None
    license: Optional[str] = None
    attribution: Optional[str] = None


@dataclass
class SignModel:
    """
    Modelo completo de un signo/concepto.

    Este objeto representa la información lingüística
    necesaria para posteriormente producir una animación.

    No contiene directamente los keyframes de Blender.
    """

    concept: str

    language: str

    status: str = "unavailable"

    hand_shape: HandShape = field(
        default_factory=HandShape
    )

    orientation: Orientation = field(
        default_factory=Orientation
    )

    location: Location = field(
        default_factory=Location
    )

    movement: Movement = field(
        default_factory=Movement
    )

    non_manual: NonManualFeatures = field(
        default_factory=NonManualFeatures
    )

    dominant_hand: Optional[str] = None

    duration: Optional[float] = None

    variants: List[str] = field(
        default_factory=list
    )

    notes: Optional[str] = None

    source: Optional[SignSource] = None

    confidence: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def validate(self) -> List[str]:
        """
        Comprueba la consistencia básica del modelo.
        """

        errors = []

        if not self.concept.strip():
            errors.append(
                "El concepto no puede estar vacío."
            )

        if not self.language.strip():
            errors.append(
                "La lengua no puede estar vacía."
            )

        if self.status not in {
            "defined",
            "unavailable",
            "verified",
            "prototype",
        }:
            errors.append(
                f"Estado no válido: {self.status}"
            )

        if not 0.0 <= self.confidence <= 1.0:
            errors.append(
                "confidence debe estar entre 0.0 y 1.0."
            )

        if (
            self.duration is not None
            and self.duration < 0
        ):
            errors.append(
                "duration no puede ser negativa."
            )

        return errors

    # =========================================================
    # SERIALIZACIÓN
    # =========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        """

        return {
            "concept": self.concept,
            "language": self.language,
            "status": self.status,

            "hand_shape": {
                "shape": self.hand_shape.shape,
                "fingers": self.hand_shape.fingers,
                "thumb": self.hand_shape.thumb,
            },

            "orientation": {
                "palm": self.orientation.palm,
                "wrist": self.orientation.wrist,
                "fingers": self.orientation.fingers,
            },

            "location": {
                "body_region": self.location.body_region,
                "side": self.location.side,
                "height": self.location.height,
            },

            "movement": {
                "type": self.movement.type,
                "direction": self.movement.direction,
                "path": self.movement.path,
                "repetition": self.movement.repetition,
                "speed": self.movement.speed,
            },

            "non_manual": {
                "facial_expression": (
                    self.non_manual.facial_expression
                ),
                "eyebrow_position": (
                    self.non_manual.eyebrow_position
                ),
                "eye_gaze": (
                    self.non_manual.eye_gaze
                ),
                "head_movement": (
                    self.non_manual.head_movement
                ),
                "mouth_pattern": (
                    self.non_manual.mouth_pattern
                ),
            },

            "dominant_hand": self.dominant_hand,
            "duration": self.duration,
            "variants": self.variants,
            "notes": self.notes,

            "source": (
                None
                if self.source is None
                else {
                    "name": self.source.name,
                    "url": self.source.url,
                    "license": self.source.license,
                    "attribution": self.source.attribution,
                }
            ),

            "confidence": self.confidence,
            "metadata": self.metadata,
        }

    # =========================================================
    # CONSTRUCCIÓN DESDE DICCIONARIO
    # =========================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "SignModel":
        """
        Construye un SignModel desde un diccionario.
        """

        hand_data = data.get(
            "hand_shape",
            {},
        )

        orientation_data = data.get(
            "orientation",
            {},
        )

        location_data = data.get(
            "location",
            {},
        )

        movement_data = data.get(
            "movement",
            {},
        )

        non_manual_data = data.get(
            "non_manual",
            {},
        )

        source_data = data.get(
            "source"
        )

        source = None

        if source_data is not None:
            source = SignSource(
                name=source_data.get("name"),
                url=source_data.get("url"),
                license=source_data.get("license"),
                attribution=source_data.get(
                    "attribution"
                ),
            )

        return cls(
            concept=data["concept"],
            language=data["language"],
            status=data.get(
                "status",
                "unavailable",
            ),

            hand_shape=HandShape(
                shape=hand_data.get("shape"),
                fingers=hand_data.get(
                    "fingers",
                    {},
                ),
                thumb=hand_data.get("thumb"),
            ),

            orientation=Orientation(
                palm=orientation_data.get(
                    "palm"
                ),
                wrist=orientation_data.get(
                    "wrist"
                ),
                fingers=orientation_data.get(
                    "fingers"
                ),
            ),

            location=Location(
                body_region=location_data.get(
                    "body_region"
                ),
                side=location_data.get("side"),
                height=location_data.get(
                    "height"
                ),
            ),

            movement=Movement(
                type=movement_data.get("type"),
                direction=movement_data.get(
                    "direction"
                ),
                path=movement_data.get("path"),
                repetition=movement_data.get(
                    "repetition",
                    1,
                ),
                speed=movement_data.get(
                    "speed"
                ),
            ),

            non_manual=NonManualFeatures(
                facial_expression=(
                    non_manual_data.get(
                        "facial_expression"
                    )
                ),
                eyebrow_position=(
                    non_manual_data.get(
                        "eyebrow_position"
                    )
                ),
                eye_gaze=(
                    non_manual_data.get(
                        "eye_gaze"
                    )
                ),
                head_movement=(
                    non_manual_data.get(
                        "head_movement"
                    )
                ),
                mouth_pattern=(
                    non_manual_data.get(
                        "mouth_pattern"
                    )
                ),
            ),

            dominant_hand=data.get(
                "dominant_hand"
            ),

            duration=data.get(
                "duration"
            ),

            variants=data.get(
                "variants",
                [],
            ),

            notes=data.get(
                "notes"
            ),

            source=source,

            confidence=data.get(
                "confidence",
                0.0,
            ),

            metadata=data.get(
                "metadata",
                {},
            ),
        )


# =============================================================
# PRUEBA DIRECTA
# =============================================================

if __name__ == "__main__":

    sign = SignModel(
        concept="SAVE",
        language="ASL",
        status="prototype",
        dominant_hand="right",
        duration=0.8,
        confidence=0.5,
        notes=(
            "Modelo estructural de prueba. "
            "No representa todavía una descripción "
            "lingüística verificada."
        ),
    )

    print(
        "=== SIGNMUSIC SIGN MODEL ==="
    )

    print(
        "Concept:",
        sign.concept,
    )

    print(
        "Language:",
        sign.language,
    )

    print(
        "Validation:",
        sign.validate(),
    )

    print(
        "Dictionary:",
        sign.to_dict(),
    )