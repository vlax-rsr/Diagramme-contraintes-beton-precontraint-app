"""Widget de réglage : un libellé, un champ de saisie, et — facultativement —
un curseur, tous les trois synchronisés.

`grandeur` est le nom court utilisé par la fenêtre pour savoir ce qui vient
d'être réglé, et donc dans quelle grandeur afficher le seuil de traction nulle.
"""

from contextlib import contextmanager

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QWidget,
)

LARGEUR_LIBELLE = 104       # px : aligne les champs entre les groupes
STEPS_PAGE = 0.1            # pas du curseur qui avance sans glissement fin


@contextmanager
def signaux_bloques(*objets):
    """Les signaux de `objets` restent branchés mais ne sont pas déclenchés.

    Les objets absents (pas de curseur) sont simplement ignorés.
    """
    bloqueurs = [QSignalBlocker(objet) for objet in objets if objet is not None]
    try:
        yield
    finally:
        bloqueurs.clear()


class Reglage(QWidget):
    """Libellé, champ de saisie et — facultativement — curseur synchronisés.

    Plage : (minimum, maximum, pas). `pas` doit avoir autant de décimales que
    celles du champ, sans quoi le curseur et le champ ne peuvent coïncider.
    Sans `avec_curseur`, le widget se réduit à un simple champ de saisie.
    """

    modifie = Signal(str)

    def __init__(self, grandeur: str, libelle: str, unite: str,
                 plage: tuple[float, float, float], valeur: float,
                 decimales: int, avec_curseur: bool = True, parent=None):
        super().__init__(parent)
        self.grandeur = grandeur
        self.minimum, self.maximum, self.pas = plage
        self.avec_curseur = avec_curseur

        self.curseur = QSlider(Qt.Horizontal) if avec_curseur else None
        if self.curseur is not None:
            self._bornes_curseur()
            self.curseur.setPageStep(max(1, round(STEPS_PAGE / self.pas)))
            self.curseur.valueChanged.connect(self._curseur_change)

        self.champ = QDoubleSpinBox()
        self.champ.setDecimals(decimales)
        self.champ.setRange(self.minimum, self.maximum)
        self.champ.setSingleStep(self.pas)
        self.champ.setSuffix(f"  {unite}")
        self.champ.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.champ.setKeyboardTracking(False)
        self.champ.valueChanged.connect(self._champ_change)

        texte = QLabel(libelle)
        texte.setMinimumWidth(LARGEUR_LIBELLE)

        disposition = QHBoxLayout(self)
        disposition.setContentsMargins(0, 0, 0, 0)
        disposition.addWidget(texte)
        if self.curseur is not None:
            disposition.addWidget(self.curseur, 1)
        disposition.addWidget(self.champ)

        self.definir(valeur)

    @property
    def valeur(self) -> float:
        return self.champ.value()

    def _bornes_curseur(self) -> None:
        if self.curseur is not None:
            self.curseur.setRange(0, round((self.maximum - self.minimum) / self.pas))

    def _index(self, valeur: float) -> int:
        """Position du curseur correspondant à une valeur du champ."""
        return round((valeur - self.minimum) / self.pas)

    def definir(self, valeur: float) -> None:
        """Positionne le champ et le curseur sans déclencher `modifie`."""
        valeur = min(max(valeur, self.minimum), self.maximum)
        with signaux_bloques(self.curseur, self.champ):
            self.champ.setValue(valeur)
            if self.curseur is not None:
                self.curseur.setValue(self._index(valeur))

    def definir_plage(self, minimum: float, maximum: float) -> None:
        """Change les bornes, en arrondissant le maximum sur un pas entier.

        La valeur en cours est conservée si elle reste admissible, bornée
        sinon. Appelé quand h change, puisque la plage de e vaut 0 → h/2.
        """
        maximum = minimum + round((maximum - minimum) / self.pas) * self.pas
        if (minimum, maximum) == (self.minimum, self.maximum):
            return
        valeur = min(max(self.champ.value(), minimum), maximum)
        self.minimum, self.maximum = minimum, maximum
        with signaux_bloques(self.curseur, self.champ):
            self.champ.setRange(minimum, maximum)
            self.champ.setValue(valeur)
            self._bornes_curseur()
            self.curseur.setValue(self._index(valeur))
        self.modifie.emit(self.grandeur)

    def _curseur_change(self, index: int) -> None:
        with signaux_bloques(self.champ):
            self.champ.setValue(self.minimum + index * self.pas)
        self.modifie.emit(self.grandeur)

    def _champ_change(self, _valeur: float) -> None:
        if self.curseur is not None:
            with signaux_bloques(self.curseur):
                self.curseur.setValue(self._index(self.champ.value()))
        self.modifie.emit(self.grandeur)
