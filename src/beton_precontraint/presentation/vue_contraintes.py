"""Canevas des quatre diagrammes : matplotlib dans un widget Qt.

Ce widget est le seul point de contact entre les deux bibliothèques. Il possède
sa figure et son canevas, et ne publie que deux opérations : mettre à jour les
diagrammes, produire la figure d'export.
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..domaine import CasDeCharge, Diagramme, SectionRectangulaire
from ..rendu import VueDiagrammes, figure_complete
from .constantes import TAILLE_CANEVAS_MINIMALE, TAILLE_FIGURE


class VueContraintes(QWidget):
    """Les quatre diagrammes de la superposition, redessinés à la demande."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=TAILLE_FIGURE, facecolor="white")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumSize(*TAILLE_CANEVAS_MINIMALE)
        self.diagrammes = VueDiagrammes(self.figure)

        disposition = QVBoxLayout(self)
        disposition.setContentsMargins(0, 0, 0, 0)
        disposition.addWidget(self.canvas)

    @property
    def axes(self) -> list:
        """Axes des quatre colonnes, dans l'ordre d'affichage."""
        return self.diagrammes.axes_diag

    def mettre_a_jour(self, diagrammes: tuple[Diagramme, ...]) -> None:
        self.diagrammes.mettre_a_jour(diagrammes)
        self.canvas.draw_idle()

    def effacer(self) -> None:
        self.diagrammes.effacer()
        self.canvas.draw_idle()

    def figure_export(self, section: SectionRectangulaire,
                      cas: CasDeCharge) -> Figure:
        """Figure autonome réunissant la section cotée et les quatre diagrammes."""
        return figure_complete(section, cas)
