"""Génère l'image d'aperçu du dépôt (docs/apercu.png)."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")

from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg

from beton_precontraint.domaine import CasDeCharge, SectionRectangulaire
from beton_precontraint.rendu import figure_complete

RACINE = Path(__file__).resolve().parent
sortie = RACINE / "apercu.png"

figure = figure_complete(SectionRectangulaire(0.50, 1.20),
                         CasDeCharge(0.80, 1.50, 0.20))
FigureCanvasAgg(figure)
figure.savefig(sortie, dpi=110, bbox_inches="tight", facecolor="white")
print(sortie, os.path.getsize(sortie), "octets")
