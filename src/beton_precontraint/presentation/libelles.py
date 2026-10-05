"""Textes affichés : ce sont des fonctions pures du domaine, sans widget.

Les mettre à part permet de les tester sur un cas de charge sans fenêtre, et de
laisser `fenetre.py` réduit à la mise en page.
"""

from math import isfinite

from ..domaine import (
    CasDeCharge,
    SectionRectangulaire,
    effort_annulant_traction,
    excentrement_annulant_traction,
)
from ..theme import COULEUR_COMPRESSION, COULEUR_TRACTION

SEUIL_NUL = 0.005       # MPa : en dessous, une contrainte vaut zéro à l'affichage


def qualite(sigma: float) -> str:
    """Qualité mécanique d'une contrainte, compression positive."""
    if abs(sigma) < SEUIL_NUL:
        return "nulle"
    return "compression" if sigma > 0 else "traction"


def libelle_fibre(nom: str, sigma: float) -> str:
    """« Fibre supérieure : +6.67 MPa (compression) »."""
    return f"Fibre {nom} : <b>{sigma:+.2f} MPa</b> ({qualite(sigma)})"


def libelle_etat(section: SectionRectangulaire, cas: CasDeCharge) -> tuple[str, str]:
    """Diagnostic de la section, et couleur associée.

    Bleu si toute la section est comprimée, rouge dès qu'une fibre est en
    traction : la couleur suit donc la convention des diagrammes.
    """
    sigma_sup, sigma_inf = cas.extremes_totaux(section)
    couleur = (COULEUR_COMPRESSION if min(sigma_sup, sigma_inf) >= 0
               else COULEUR_TRACTION)
    return cas.etat_section(section), couleur


def libelle_seuil(grandeur: str, section: SectionRectangulaire,
                  cas: CasDeCharge) -> str:
    """Seuil de fibre inférieure nulle, dans la grandeur que l'on ne règle pas.

    `grandeur` vaut "P" quand P vient d'être changé : on lit alors l'excentrement
    qui annulerait la contrainte. Sinon on lit la force de précontrainte
    correspondante. Les deux expriment la même relation P = 6·M/(h + 6·e).
    """
    if grandeur != "P":
        seuil = effort_annulant_traction(cas.moment, section, cas.excentrement)
        return f"Fibre inférieure nulle pour P = <b>{seuil:.2f} MN</b>"

    seuil = excentrement_annulant_traction(cas.moment, section, cas.effort)
    if not isfinite(seuil):
        return "Fibre inférieure nulle : impossible, P = 0"
    if seuil < 0:
        return ("Fibre inférieure jamais nulle pour e ≥ 0 "
                f"(il faudrait e = {seuil:+.3f} m)")
    if seuil > section.h / 2:
        return (f"Fibre inférieure nulle pour e = <b>{seuil:.3f} m</b>, "
                f"hors plage (e ≤ h/2 = {section.h / 2:.3f} m)")
    return f"Fibre inférieure nulle pour e = <b>{seuil:.3f} m</b>"
