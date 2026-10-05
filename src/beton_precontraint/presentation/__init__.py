"""Interface PySide6 : la fenêtre, ses réglages et ses deux vues.

Cette couche ne fait aucun calcul : elle lit les réglages, demande le cas de
charge au domaine, et affiche le résultat. Elle dépend de PySide6, mais aussi
de matplotlib pour le canevas des diagrammes — d'où un seul module,
`vue_contraintes.py`, qui assume ce lien.
"""

from .constantes import TITRE_FENETRE
from .fenetre import FenetreContraintes
from .reglages import Reglage
from .vue_contraintes import VueContraintes
from .vue_section import VueSection

__all__ = [
    "TITRE_FENETRE",
    "FenetreContraintes",
    "Reglage",
    "VueContraintes",
    "VueSection",
]
