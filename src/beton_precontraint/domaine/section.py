"""Section rectangulaire b x h : grandeurs géométriques et contraintes dues à
la section seule.

Unités SI : b, h en m ; M en MN·m ; P en MN  ->  σ en MPa.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SectionRectangulaire:
    """Section rectangulaire b x h (m)."""

    b: float
    h: float

    def __post_init__(self) -> None:
        if self.b <= 0 or self.h <= 0:
            raise ValueError(f"b et h strictement positifs (b={self.b}, h={self.h})")

    @property
    def surface(self) -> float:
        """S = b·h (m²)."""
        return self.b * self.h

    @property
    def inertie(self) -> float:
        """I = b·h³/12 (m⁴)."""
        return self.b * self.h ** 3 / 12

    @property
    def excentricite_max(self) -> float:
        """Limite du noyau : e = h/6."""
        return self.h / 6

    def sigma_flexion(self, moment: float, y):
        """σ_M(y) = M·y/I (MPa si M en MN·m), compression positive."""
        return moment * np.asarray(y, dtype=float) / self.inertie

    def sigma_axiale(self, effort: float) -> float:
        """σ_P = P/(b·h) (MPa si P en MN), compression positive."""
        return effort / self.surface

    def extremes_flexion(self, moment: float) -> tuple[float, float]:
        """(σ fibre supérieure, σ fibre inférieure) dues à la flexion seule."""
        return (float(self.sigma_flexion(moment, self.h / 2)),
                float(self.sigma_flexion(moment, -self.h / 2)))
