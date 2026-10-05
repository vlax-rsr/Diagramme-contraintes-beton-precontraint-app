"""Cas de charge d'une section de poutre précontrainte, et superposition des
contraintes.

Convention de signe : COMPRESSION POSITIVE (σ > 0 = compression).
    - M > 0 : moment fléchissant extérieur, flèche vers le bas, donc traction
      en fibre inférieure ;
    - P > 0 : force de précontrainte comprimant la section ;
    - e > 0 : excentrement du câblage, 0 ≤ e ≤ h/2.

La force de précontrainte est appliquée en effort axial, puis son
excentrement e ajoute une flexion M₂ = -P·e :

    σ(y) = σ_M(y) + σ_P + σ_M₂(y) = (M - P·e)·y/I + P/(b·h)

où y est mesuré vers le haut depuis le centre de gravité.
"""

from dataclasses import dataclass

from .diagramme import Diagramme
from .section import SectionRectangulaire


@dataclass(frozen=True)
class CasDeCharge:
    """Cas d'une section de poutre précontrainte.

    moment : moment fléchissant extérieur M (MN·m), positif (flèche vers le bas) ;
    effort : force de précontrainte P (MN), > 0 = compression de la section ;
    excentrement : décalage e du point d'application de P sous le centre de
        gravité (m), 0 ≤ e ≤ h/2.
    """

    moment: float = 0.80
    effort: float = 4.00
    excentrement: float = 0.02

    @property
    def moment_excentricite(self) -> float:
        """M₂ = -P·e (MN·m), toujours négatif pour P > 0 et e > 0.

        C'est le moment flexionnant dû à l'excentrement de la force de
        précontrainte appliquée en effort axial : P comprime uniformément la
        section, et son déplacement de e sous le centre de gravité s'y ajoute
        comme une flexion de moment M₂, de signe opposé à M.
        """
        return -self.effort * self.excentrement

    @property
    def moment_total(self) -> float:
        """M + M₂ : le moment qui régit la forme de la contrainte totale."""
        return self.moment + self.moment_excentricite

    def sigma_axiale(self, section: SectionRectangulaire) -> float:
        return section.sigma_axiale(self.effort)

    def extremes_exterieur(self, section: SectionRectangulaire) -> tuple[float, float]:
        return section.extremes_flexion(self.moment)

    def extremes_excentricite(self, section: SectionRectangulaire) -> tuple[float, float]:
        return section.extremes_flexion(self.moment_excentricite)

    def extremes_totaux(self, section: SectionRectangulaire) -> tuple[float, float]:
        """Contraintes totales (σ(M) + σ(P) + σ(M₂)) aux deux fibres extrêmes."""
        ext = self.extremes_exterieur(section)
        pre = self.extremes_excentricite(section)
        axiale = self.sigma_axiale(section)
        return (ext[0] + pre[0] + axiale, ext[1] + pre[1] + axiale)

    def diagrammes(self, section: SectionRectangulaire) -> tuple[Diagramme, ...]:
        """Les quatre diagrammes de la superposition, dans l'ordre d'affichage."""
        axiale = self.sigma_axiale(section)
        return (
            Diagramme(f"Flexion extérieure\n$M$ = {self.moment:+.2f} MN·m",
                      *self.extremes_exterieur(section)),
            Diagramme(f"Effort normal\n$P$ = {self.effort:+.2f} MN",
                      axiale, axiale),
            Diagramme(f"Flexion $M_2$ (excentrement)\n$M_2 = -P\\,e$ = "
                      f"{self.moment_excentricite:+.3f} MN·m",
                      *self.extremes_excentricite(section)),
            Diagramme("Contraintes totales\n"
                      "$\\sigma = \\sigma(M) + \\sigma(P) + \\sigma(M_2)$",
                      *self.extremes_totaux(section)),
        )

    def etat_section(self, section: SectionRectangulaire) -> str:
        """Diagnostic : signale toute fibre en traction, ou la compression totale."""
        sigma_sup, sigma_inf = self.extremes_totaux(section)
        tractions = [(nom, s) for nom, s in (("supérieure", sigma_sup),
                                             ("inférieure", sigma_inf)) if s < 0]
        if not tractions:
            return "Précontrainte totale"
        return " ; ".join(f"Traction en fibre {nom} : {abs(s):.2f} MPa"
                          for nom, s in tractions)
