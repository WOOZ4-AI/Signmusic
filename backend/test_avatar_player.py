import sys

sys.path.insert(0, "backend")

from keyframe_generator import KeyframeGenerator
from avatar_animation import AvatarAnimation
from avatar_player import AvatarPlayer


k = KeyframeGenerator()
a = AvatarAnimation()
p = AvatarPlayer()

sequence = a.prepare_sequence(
    k.generate_animation_sequence(
        ["SAVE", "ME", "YOU", "HELP", "LOVE", "LIFE"],
        bpm=120
    )
)

times = [
    0.0,
    0.2,
    0.4,
    0.8,
    1.0,
    1.25,
    1.5,
    1.7,
    2.0,
    2.4,
    2.7,
    3.0,
    3.3,
    3.7,
]

for t in times:
    result = p.sample_sequence(sequence, t)

    print(
        f"{t:.2f}s -> "
        f"{result.get('concept')}"
    )