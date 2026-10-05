"""Figure d'export : la section cotée au-dessus, les quatre diagrammes en
dessous, réunis dans une seule image.

Le canevas matplotlib de la fenêtre ne contient que les diagrammes ; c'est ici
que les deux dessins se rencontrent, pour l'enregistrement d'image.
"""

from matplotlib.figure import Figure

from ..domaine import CasDeCharge, SectionRectangulaire
from .constantes import (
    BANDE_EXPORT_DIAGRAMMES,
    CADRE_EXPORT_SECTION,
    TAILLE_EXPORT,
)
from .diagrammes import VueDiagrammes
from .section import tracer_section


def figure_complete(section: SectionRectangulaire, cas: CasDeCharge) -> Figure:
    """Figure autonome : section cotée au-dessus, superposition des diagrammes
    en dessous.

    La section occupe le haut de la figure, à sa propre échelle.
    """
    figure = Figure(figsize=TAILLE_EXPORT, facecolor="white")
    tracer_section(section, figure.add_axes(CADRE_EXPORT_SECTION))
    VueDiagrammes(figure, *BANDE_EXPORT_DIAGRAMMES).mettre_a_jour(
        cas.diagrammes(section))
    return figure
