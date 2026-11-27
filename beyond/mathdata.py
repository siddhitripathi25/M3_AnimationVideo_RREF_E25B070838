"""Single source of truth for the mathematics in the film.

Everything here uses exact integer / Fraction arithmetic.  No floating point
ever decides whether a row operation or a dependence relation is correct.

Vectors are columns:

    v1 = (1, 2, 1),  v2 = (2, 4, 2),  v3 = (1, 1, 0)

    A = [ 1 2 1 ]
        [ 2 4 1 ]
        [ 1 2 0 ]
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Iterable, Sequence

Matrix = tuple[tuple[int | Fraction, ...], ...]
Vector = tuple[int | Fraction, ...]

# ---------------------------------------------------------------------------
# The immutable data of the film.  These are never modified by any animation.
# ---------------------------------------------------------------------------

V1: Vector = (1, 2, 1)
V2: Vector = (2, 4, 2)
V3: Vector = (1, 1, 0)

A0: Matrix = (
    (1, 2, 1),
    (2, 4, 1),
    (1, 2, 0),
)

# The plane containing all three vectors: y = x + z  <=>  (1,-1,1) . p = 0
PLANE_NORMAL: Vector = (1, -1, 1)

# The homogeneous solution: x = t(-2, 1, 0),  -2 v1 + v2 = 0
NULL_DIRECTION: Vector = (-2, 1, 0)

FINAL_RREF: Matrix = (
    (1, 2, 0),
    (0, 0, 1),
    (0, 0, 0),
)

PIVOT_COLUMNS: tuple[int, ...] = (0, 2)  # zero-based -> columns 1 and 3
FREE_COLUMNS: tuple[int, ...] = (1,)     # zero-based -> column 2


# ---------------------------------------------------------------------------
# Tiny exact linear-algebra helpers (used by the verification script and by
# the tests; the animation imports the same constants, not a second copy).
# ---------------------------------------------------------------------------


def matvec(m: Matrix, x: Vector) -> Vector:
    return tuple(sum((Fraction(m[i][j]) * Fraction(x[j]) for j in range(len(x))), Fraction(0)) for i in range(len(m)))


def matmul(m: Matrix, n: Matrix) -> Matrix:
    rows, cols, inner = len(m), len(n[0]), len(n)
    return tuple(
        tuple(sum((Fraction(m[i][k]) * Fraction(n[k][j]) for k in range(inner)), Fraction(0)) for j in range(cols))
        for i in range(rows)
    )


def matrix_from_columns(cols: Sequence[Vector]) -> Matrix:
    return tuple(tuple(c[j] for c in cols) for j in range(len(cols[0])))


def rref(m: Matrix) -> tuple[Matrix, tuple[int, ...]]:
    """Return exact reduced row echelon form and the pivot column indices."""
    a = [[Fraction(x) for x in row] for row in m]
    rows, cols = len(a), len(a[0])
    pivots: list[int] = []
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        pivot = next((i for i in range(r, rows) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][c]
        a[r] = [x / scale for x in a[r]]
        for i in range(rows):
            if i != r and a[i][c] != 0:
                factor = a[i][c]
                a[i] = [x - factor * y for x, y in zip(a[i], a[r])]
        pivots.append(c)
        r += 1
    return tuple(tuple(x for x in row) for row in a), tuple(pivots)


def rank(m: Matrix) -> int:
    return len(rref(m)[1])


def nullspace(m: Matrix) -> tuple[tuple[Fraction, ...], ...]:
    """Exact basis for ker(M), one vector per free variable."""
    red, pivots = rref(m)
    rows, cols = len(red), len(red[0])
    free = [c for c in range(cols) if c not in pivots]
    basis: list[tuple[Fraction, ...]] = []
    for f in free:
        v = [Fraction(0)] * cols
        v[f] = Fraction(1)
        for row, p in enumerate(pivots):
            v[p] = -red[row][f]
        basis.append(tuple(v))
    return tuple(basis)


def span_contains(basis: Iterable[Vector], target: Vector) -> bool:
    """Exact membership test over the rationals via RREF of an augmented system."""
    b = list(basis)
    if not b:
        return all(x == 0 for x in target)
    n = len(b[0])
    augmented: Matrix = tuple(
        tuple(Fraction(b[i][j]) for i in range(len(b))) + (Fraction(target[j]),) for j in range(n)
    )
    red, pivots = rref(augmented)
    # Inconsistent iff a row has all zero coefficients but nonzero RHS.
    for i, row in enumerate(red):
        if all(x == 0 for x in row[: len(b)]) and row[-1] != 0:
            return False
    return True


# ---------------------------------------------------------------------------
# The four row-reduction stages, exactly as specified in the film brief.
# Stage 1 applies two row replacements (R2 and R3); stages 2-4 apply one each.
# ---------------------------------------------------------------------------


def _stage1(m: Matrix) -> Matrix:
    r1, r2, r3 = m
    return (r1, tuple(r2[i] - 2 * r1[i] for i in range(3)), tuple(r3[i] - r1[i] for i in range(3)))


def _stage2(m: Matrix) -> Matrix:
    return (m[0], tuple(-x for x in m[1]), m[2])


def _stage3(m: Matrix) -> Matrix:
    return (m[0], m[1], tuple(m[2][i] + m[1][i] for i in range(3)))


def _stage4(m: Matrix) -> Matrix:
    return (tuple(m[0][i] - m[1][i] for i in range(3)), m[1], m[2])


@dataclass(frozen=True)
class RowStage:
    number: int
    operations: tuple[str, ...]          # exact notation shown on screen
    ascii_operations: tuple[str, ...]    # plain text for logs / narration
    changed_rows: tuple[int, ...]        # zero-based row indices
    apply: Callable[[Matrix], Matrix]
    expected: Matrix                     # independently written expected result


ROW_STAGES: tuple[RowStage, ...] = (
    RowStage(
        1,
        ("R₂ ← R₂ − 2R₁", "R₃ ← R₃ − R₁"),
        ("R2 <- R2 - 2R1", "R3 <- R3 - R1"),
        (1, 2),
        _stage1,
        ((1, 2, 1), (0, 0, -1), (0, 0, -1)),
    ),
    RowStage(
        2,
        ("R₂ ← −R₂",),
        ("R2 <- -R2",),
        (1,),
        _stage2,
        ((1, 2, 1), (0, 0, 1), (0, 0, -1)),
    ),
    RowStage(
        3,
        ("R₃ ← R₃ + R₂",),
        ("R3 <- R3 + R2",),
        (2,),
        _stage3,
        ((1, 2, 1), (0, 0, 1), (0, 0, 0)),
    ),
    RowStage(
        4,
        ("R₁ ← R₁ − R₂",),
        ("R1 <- R1 - R2",),
        (0,),
        _stage4,
        ((1, 2, 0), (0, 0, 1), (0, 0, 0)),
    ),
)


def reduction_sequence() -> list[Matrix]:
    """[A, after stage 1, after stage 2, after stage 3, RREF]."""
    out = [A0]
    current = A0
    for stage in ROW_STAGES:
        current = stage.apply(current)
        out.append(current)
    return out


# ---------------------------------------------------------------------------
# Verification -- run as a script, or via tests/test_math.py
# ---------------------------------------------------------------------------


def verify_all(verbose: bool = True) -> dict[str, bool]:
    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)
        if verbose:
            print(f"  [{'PASS' if condition else 'FAIL'}] {name}")

    if verbose:
        print("Mathematical verification — BEYOND THE PIVOTS")

    check("matrix columns are exactly v1, v2, v3", matrix_from_columns((V1, V2, V3)) == A0)
    check("v2 = 2*v1", V2 == tuple(2 * x for x in V1))
    check("all vectors satisfy y = x + z", all(y == x + z for x, y, z in (V1, V2, V3)))
    check("plane normal is orthogonal to each vector", all(sum(n * c for n, c in zip(PLANE_NORMAL, v)) == 0 for v in (V1, V2, V3)))

    sequence = reduction_sequence()
    for stage, before, after in zip(ROW_STAGES, sequence, sequence[1:]):
        check(f"stage {stage.number} computed result matches displayed matrix", after == stage.expected)
        check(f"stage {stage.number} leaves unhighlighted rows unchanged", all(
            before[i] == after[i] for i in range(3) if i not in stage.changed_rows
        ))
        check(f"stage {stage.number} preserves ker(A)", set(nullspace(before)) == set(nullspace(after)))

    reduced, pivots = rref(A0)
    check("independent RREF routine agrees with final stage", reduced == FINAL_RREF == sequence[-1])
    check("pivot columns are 1 and 3 (zero-based 0, 2)", pivots == PIVOT_COLUMNS)
    check("free column is 2 (zero-based 1)", tuple(c for c in range(3) if c not in pivots) == FREE_COLUMNS)
    check("rank is 2", rank(A0) == 2)
    check("v1 and v3 are independent", rank(matrix_from_columns((V1, V3))) == 2)
    check("nullspace is spanned by (-2, 1, 0)", nullspace(A0) == ((Fraction(-2), Fraction(1), Fraction(0)),))
    check("A * (-2,1,0) = 0", matvec(A0, NULL_DIRECTION) == (0, 0, 0))
    check("-2*v1 + 1*v2 + 0*v3 = 0", tuple(-2 * V1[i] + V2[i] for i in range(3)) == (0, 0, 0))
    check("original column space is the plane y = x + z", rank(A0) == 2 and span_contains((V1, V3), V2))
    rref_cols = tuple(zip(*FINAL_RREF))
    for i, m in enumerate(sequence):
        cols = tuple(zip(*m))
        check(f"stage {i}: col2 = 2*col1 (relation preserved)", cols[1] == tuple(2 * x for x in cols[0]))
    check("row operations do NOT preserve column space", not span_contains((rref_cols[0], rref_cols[2]), V1))
    check("RREF column space is z = 0, not the original plane", all(col[2] == 0 for col in rref_cols) and V1[2] != 0)

    if verbose:
        failed = [n for n, ok in checks.items() if not ok]
        print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed.")
        if failed:
            print("FAILED: " + ", ".join(failed))
    return checks


if __name__ == "__main__":
    import sys

    sys.exit(0 if all(verify_all().values()) else 1)
