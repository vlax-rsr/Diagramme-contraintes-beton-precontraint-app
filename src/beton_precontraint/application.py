"""Démarrage de l'application.

Ce module ne fait que trois choses : créer l'application Qt s'il n'existe pas,
ouvrir la fenêtre, et lancer la boucle d'événements. Il permet à la fenêtre
d'être construite et testée sans passer par ici.
"""

import sys

from PySide6.QtWidgets import QApplication

from .presentation.constantes import TAILLE_FENETRE
from .presentation.fenetre import FenetreContraintes


def creer_application(argv: list[str] | None = None) -> QApplication:
    """L'instance Qt, créée si nécessaire (un seul objet QApplication possible)."""
    application = QApplication.instance()
    if application is None:
        application = QApplication(argv if argv is not None else sys.argv)
        application.setApplicationName("beton-precontraint")
    return application


def main(argv: list[str] | None = None) -> int:
    application = creer_application(argv)
    fenetre = FenetreContraintes()
    fenetre.resize(*TAILLE_FENETRE)
    fenetre.show()
    return application.exec()
