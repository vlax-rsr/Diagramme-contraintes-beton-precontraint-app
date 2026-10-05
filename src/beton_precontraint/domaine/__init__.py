"""Cœur de calcul : arithmétique seule, aucun import graphique.

Ce paquet est le seul à définir ce que sont les contraintes. Il ne dépend ni de
PySide6, ni de matplotlib, ni de numpy pour ses résultats : les tests peuvent
donc le vérifier sans environment graphique.
"""

from .charges import CasDeCharge
from .diagramme import Diagramme
from .relations import (
    effort_annulant_traction,
    excentrement_annulant_traction,
)
from .section import SectionRectangulaire

__all__ = [
    "CasDeCharge",
    "Diagramme",
    "SectionRectangulaire",
    "effort_annulant_traction",
    "excentrement_annulant_traction",
]
