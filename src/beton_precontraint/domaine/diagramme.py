"""Valeur d'un diagramme de contraintes : les deux contraintes extrêmes.

La différence entre ces deux valeurs suffit à définir la forme du diagramme,
qui est linéaire sur la hauteur : c'est tout ce que le rendu a besoin de savoir.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Diagramme:
    """Contraintes aux deux fibres extrêmes : leur différence définit la forme."""

    titre: str
    sigma_sup: float
    sigma_inf: float

    @property
    def sigma_reference(self) -> float:
        """Plus grande contrainte en valeur absolue (MPa) : sert au tracé."""
        return max(abs(self.sigma_sup), abs(self.sigma_inf))
