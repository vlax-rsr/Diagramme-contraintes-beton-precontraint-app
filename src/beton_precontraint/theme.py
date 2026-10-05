"""Palette commune aux deux techniques de dessin.

Le bleu signifie toujours la compression et le rouge la traction, aussi bien
sur les diagrammes matplotlib que sur les libellés de l'interface : une seule
définition, donc une seule convention à retenir.
"""

COULEUR_COMPRESSION = "#1f77b4"   # σ > 0
COULEUR_TRACTION = "#d62728"      # σ < 0

# section cotée (QtCharts)
COULEUR_SECTION = "#37474f"
COULEUR_COTE = "#546e7a"
COULEUR_ATTACHE = "#b0bec5"
COULEUR_TEXTE_COTE = "#37474f"

__all__ = [
    "COULEUR_ATTACHE",
    "COULEUR_COMPRESSION",
    "COULEUR_COTE",
    "COULEUR_SECTION",
    "COULEUR_TEXTE_COTE",
    "COULEUR_TRACTION",
]
