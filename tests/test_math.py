"""Every mathematical claim drawn on screen is checked here with exact arithmetic."""

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from beyond import mathdata as md  # noqa: E402


def test_all_built_in_checks_pass():
    checks = md.verify_all(verbose=False)
    failed = [k for k, ok in checks.items() if not ok]
    assert not failed, failed


def test_reduction_sequence_matches_brief():
    assert md.reduction_sequence() == [
        ((1, 2, 1), (2, 4, 1), (1, 2, 0)),
        ((1, 2, 1), (0, 0, -1), (0, 0, -1)),
        ((1, 2, 1), (0, 0, 1), (0, 0, -1)),
        ((1, 2, 1), (0, 0, 1), (0, 0, 0)),
        ((1, 2, 0), (0, 0, 1), (0, 0, 0)),
    ]


def test_column_relation_survives_every_row_operation():
    # The Scene 4 "invariant filaments" claim: col2 = 2*col1 in every stage.
    for m in md.reduction_sequence():
        c1, c2, _ = zip(*m)
        assert c2 == tuple(2 * x for x in c1)


def test_null_loop_closes_for_every_t():
    # Scene 5: (-2t)v1 + t v2 + 0 v3 = 0 for all t.
    for t in (Fraction(-3), Fraction(-1, 2), Fraction(0), Fraction(1), Fraction(7, 3)):
        s = tuple(-2 * t * a + t * b + 0 * c for a, b, c in zip(md.V1, md.V2, md.V3))
        assert s == (0, 0, 0)


def test_distance_from_v3_to_line_of_v1():
    # Scene 3 shows the minimum distance from v3 to span{v1}: sqrt(1/2), at k = 1/2.
    dot = sum(a * b for a, b in zip(md.V1, md.V3))           # 3
    n1 = sum(a * a for a, b in zip(md.V1, md.V1))            # 6
    k = Fraction(dot, n1)                                     # 1/2
    r = [b - k * a for a, b in zip(md.V1, md.V3)]
    assert k == Fraction(1, 2)
    assert sum(x * x for x in r) == Fraction(1, 2)


def test_random_combinations_lie_on_plane():
    # Scene 1/6 point cloud: every a v1 + b v2 + c v3 satisfies x - y + z = 0.
    import random
    rng = random.Random(7)
    for _ in range(500):
        a, b, c = (Fraction(rng.randint(-100, 100), 100) for _ in range(3))
        p = [a * x + b * y + c * z for x, y, z in zip(md.V1, md.V2, md.V3)]
        assert p[0] - p[1] + p[2] == 0
