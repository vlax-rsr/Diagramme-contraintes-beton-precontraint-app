"""Relations utiles : à quelle valeur de P ou de e la fibre inférieure est-elle
exactement comprimée ?

La contrainte en fibre inférieure vaut

    σ_inf = -6·M/(b·h²) + P/(b·h) + 6·P·e/(b·h²)

Elle s'annule pour P = 6·M/(h + 6·e) : les deux fonctions ci-dessous sont les
deux lectures de cette même relation.
"""

from .section import SectionRectangulaire


def effort_annulant_traction(moment: float, section: SectionRectangulaire,
                              excentrement: float = 0.0) -> float:
    """Force de précontrainte ramenant la fibre inférieure à la compression nulle.

    soit 6·M/h pour un câblage centré.
    """
    return 6 * moment / (section.h + 6 * excentrement)


def excentrement_annulant_traction(moment: float,
                                   section: SectionRectangulaire,
                                   effort: float) -> float:
    """Excentrement ramenant la fibre inférieure à la compression nulle.

    σ_inf = 0 ⟺ P = 6·M/(h + 6·e) ⟺ e = M/P - h/6.

    Renvoie `inf` si P = 0, et une valeur négative si aucun excentrement
    admissible n'annule la contrainte : dans ce cas la fibre inférieure est
    déjà comprimée, et e = 0 suffirait.
    """
    if effort <= 0:
        return float("inf")
    return moment / effort - section.h / 6
