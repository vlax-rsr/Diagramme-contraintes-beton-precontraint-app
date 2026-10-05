"""Rendu matplotlib : diagrammes de contraintes, section cotée, figure d'export.

Ce paquet ne connaît que le domaine et matplotlib ; il ignore l'existence de
PySide6. L'interface peut donc réutiliser ses primitives, et l'export produire
ses images sans faire appel à un seul widget.
"""

from .constantes import HAUTEUR_AFFICHAGE
from .diagrammes import VueDiagrammes, tracer_contrainte, vider_axe
from .figure import figure_complete
from .section import tracer_section

__all__ = [
    "HAUTEUR_AFFICHAGE",
    "VueDiagrammes",
    "figure_complete",
    "tracer_contrainte",
    "tracer_section",
    "vider_axe",
]
