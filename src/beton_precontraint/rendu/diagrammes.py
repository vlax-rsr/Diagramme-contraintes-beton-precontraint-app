"""Diagrammes de contraintes : le tracé matplotlib, sans dépendance à PySide6.

Deux principes de rendu, tous deux dictés par l'usage en cours de manipulation :

- la **hauteur dessinée est constante**. La poutre occupe toujours
  ``HAUTEUR_AFFICHAGE`` mètres d'écran, quelle que soit la hauteur réelle h :
  changer h ne déforme donc pas les diagrammes, il ne change que les valeurs de
  σ. Les fibres restent les deux extrémités du dessin, à y = ±hauteur/2 ;
- **aucune échelle de contrainte n'est partagée**. Chaque diagramme ajuste sa
  propre demi-largeur sur sa plus grande contrainte et remplit sa colonne : un
  diagramme à contraintes faibles est agrandi, un diagramme à contraintes
  fortes est réduit, et aucun n'est écrasé. Les largeurs variables d'un
  diagramme à l'autre ne sont donc pas comparables visuellement ; seul le
  rapport entre σ et y, au sein d'un même diagramme, a un sens.

`VueDiagrammes` encapsule une `Figure` déjà créée et n'y recrée que le contenu
des axes à chaque mise à jour, ce qui permet un affichage temps réel piloté par
les curseurs de l'interface.
"""

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from ..domaine import Diagramme
from ..theme import COULEUR_COMPRESSION, COULEUR_TRACTION
from .constantes import (
    BAS,
    DROITE,
    FACTEUR_LARGEUR,
    GAUCHE,
    HAUT,
    HAUTEUR_AFFICHAGE,
    LARGEUR_CARACTERE,
    MARGE_BAS,
    MARGE_HAUT,
    NB_POINTS,
    POIDS_DIAGRAMME,
    POIDS_SIGNE,
)

SEUIL_NUL = 0.005       # MPa : en dessous, une contrainte vaut zéro à l'affichage


def _ylim() -> tuple[float, float]:
    """Limites verticales : la hauteur affichée et ses marges d'étiquettes.

    Indépendantes de la section, donc identiques d'un diagramme à l'autre et
    d'un cas de charge à l'autre.
    """
    return (-HAUTEUR_AFFICHAGE / 2 - MARGE_BAS,
            HAUTEUR_AFFICHAGE / 2 + MARGE_HAUT)


def vider_axe(ax) -> None:
    """Retire le contenu d'un axe sans le coût d'un `clear()` complet.

    `Axes.clear()` reconstruit aussi les graduations et les bordures, ce qui
    domine le temps de rendu dès qu'on redessine à chaque mouvement de curseur.
    Ici on ne détache que les artistes dessinés, le titre restant en place.
    """
    for artiste in (*ax.patches, *ax.collections, *ax.lines, *ax.texts):
        artiste.remove()


def _largeur_etiquette(ax, texte: str, lim: float) -> float:
    """Largeur d'une étiquette, convertie dans les unités de l'axe.

    Les axes des diagrammes n'ont pas de graduations (`set_axis_off`), rien ne
    rogne donc une étiquette qui dépasse : elle viendrait recouvrir le diagramme
    voisin. On estime sa largeur en pixels pour pouvoir la maintenir à l'intérieur.
    """
    pos, fig = ax.get_position(), ax.figure
    largeur_px = max(pos.width * fig.get_figwidth() * fig.dpi, 1.0)
    return len(texte) * LARGEUR_CARACTERE * (2 * lim / largeur_px)


def tracer_contrainte(diagramme: Diagramme, ax, ylim: tuple[float, float]) -> None:
    """Trace un diagramme de contraintes variant linéairement sur la hauteur.

    sigma_sup, sigma_inf (MPa) sont les contraintes en fibre supérieure et
    inférieure :
        - flexion pure : sigma_sup = -sigma_inf (triangles)
        - effort normal : sigma_sup = sigma_inf (rectangle)
        - cas combiné  : quelconques (trapèze)

    La poutre est dessinée sur `HAUTEUR_AFFICHAGE` mètres, donc toujours de la
    même taille, et la demi-largeur du cadre vaut `FACTEUR_LARGEUR` fois la plus
    grande des deux contraintes. Les étiquettes sont alignées sur la pointe du
    diagramme et s'étendent vers l'intérieur : elles ne dépassent donc jamais de
    l'axe.
    """
    sigma_sup, sigma_inf = diagramme.sigma_sup, diagramme.sigma_inf
    demi = HAUTEUR_AFFICHAGE / 2

    y = np.linspace(-demi, demi, NB_POINTS)
    sigma = sigma_inf + (sigma_sup - sigma_inf) * (y + demi) / HAUTEUR_AFFICHAGE

    lim = FACTEUR_LARGEUR * diagramme.sigma_reference
    if lim <= 0.0:
        # aucune contrainte : il n'y a rien à ajuster. La demi-largeur vaut 1
        # pour que la transformation reste définie ; le dessin se réduit à
        # l'axe de référence, et aucune amplitude n'est imposée aux autres
        lim = 1.0

    ax.fill_betweenx(y, 0, sigma, where=sigma >= 0, interpolate=True,
                     color=COULEUR_COMPRESSION, alpha=0.35)
    ax.fill_betweenx(y, 0, sigma, where=sigma <= 0, interpolate=True,
                     color=COULEUR_TRACTION, alpha=0.35)
    ax.plot(sigma, y, color="k", lw=1.8)                # droite des contraintes
    ax.plot([0, 0], [-demi, demi], color="k", lw=3.5)   # axe de référence
    for yy, s in ((demi, sigma_sup), (-demi, sigma_inf)):   # traits de fibre
        ax.plot([0, s], [yy, yy], color="k", lw=1.5)

    # annotations des valeurs extrêmes : au-dessus / au-dessous de la poutre,
    # aussi près que possible de la pointe mais jamais au-delà de l'axe
    for yy, s, dy in ((demi, sigma_sup, 0.08), (-demi, sigma_inf, -0.08)):
        if abs(s) < SEUIL_NUL:   # valeur nulle à l'affichage : évite « -0.00 MPa »
            s = 0.0
        texte = f"{s:+.2f} MPa"
        largeur = _largeur_etiquette(ax, texte, lim)
        if abs(s) < SEUIL_NUL or largeur > 1.9 * lim:   # pas de place : on centre
            x, ha = 0.0, "center"
        elif s > 0:   # texte calé sur la pointe, croissant vers l'intérieur
            x, ha = min(max(s, -lim + largeur), lim), "right"
        else:
            x, ha = max(min(s, lim - largeur), -lim), "left"
        ax.annotate(texte, xy=(s, yy), xytext=(x, yy + dy),
                    ha=ha, va="bottom" if dy > 0 else "top", fontsize=9,
                    bbox={"boxstyle": "round,pad=0.25", "fc": "white",
                          "ec": "gray", "alpha": 0.95})

    ax.set_xlim(-lim, lim)
    ax.set_ylim(*ylim)
    ax.set_axis_off()
    ax.set_title(diagramme.titre, fontsize=9.5)


class VueDiagrammes:
    """Superposition M + P + M₂ = σ totale sur une `Figure` déjà créée.

    Les quatre diagrammes occupent la bande `bas` → `haut` de la figure, en
    fractions de sa hauteur : la section n'y figure plus, elle est dessinée à part
    (`beton_precontraint.rendu.section`). Les axes sont construits une seule fois
    et seul leur contenu est redessiné à chaque appel à `mettre_a_jour`, ce qui
    rend l'affichage temps réel ; ils ne sont reconstruits que si la taille de la
    fenêtre change. La figure ne porte aucun titre global : chaque diagramme
    s'identifie par le sien.
    """

    def __init__(self, figure: Figure, bas: float = BAS, haut: float = HAUT):
        self.figure = figure
        self.bas, self.haut = bas, haut
        self.axes_diag: list = []
        self.axes_symbole: list = []
        self._taille = (0.0, 0.0)
        self._construire_axes()

    # ------------------------------------------------------------------ axes
    def _colonnes(self) -> list[tuple[str, float]]:
        """Colonnes de la bande : quatre diagrammes séparés par les signes."""
        colonnes: list[tuple[str, float]] = []
        for index in range(4):
            if index:
                colonnes.append(("signe", POIDS_SIGNE))
            colonnes.append(("diagramme", POIDS_DIAGRAMME))
        return colonnes

    def _construire_axes(self) -> None:
        for ax in (*self.axes_diag, *self.axes_symbole):
            ax.remove()
        self.axes_diag, self.axes_symbole = [], []
        self._taille = (self.figure.bbox.width, self.figure.bbox.height)

        colonnes = self._colonnes()
        pas = (DROITE - GAUCHE) / sum(largeur for _, largeur in colonnes)
        x = GAUCHE

        for nature, largeur in colonnes:
            ax = self.figure.add_axes([x, self.bas, largeur * pas,
                                       self.haut - self.bas])
            x += largeur * pas
            if nature == "signe":
                ax.set_xlim(0, 1)
                ax.set_axis_off()
                self.axes_symbole.append(ax)
            else:
                self.axes_diag.append(ax)

        for ax, symbole in zip(self.axes_symbole, ["+", "+", "="], strict=True):
            ax.text(0.5, 0, symbole, ha="center", va="center", fontsize=30,
                    fontweight="bold")

    # ----------------------------------------------------------------- rendu
    def mettre_a_jour(self, diagrammes: tuple[Diagramme, ...]) -> None:
        """Redessine les quatre colonnes.

        La géométrie ne dépend que de la taille de la figure : ni la section, ni
        l'amplitude des contraintes n'y changent quoi que ce soit.
        """
        if (self.figure.bbox.width, self.figure.bbox.height) != self._taille:
            self._construire_axes()

        ylim = _ylim()

        for ax, diagramme in zip(self.axes_diag, diagrammes, strict=True):
            vider_axe(ax)
            tracer_contrainte(diagramme, ax, ylim)

        for ax in self.axes_symbole:   # les signes sont centrés sur y = 0
            ax.set_ylim(*ylim)

        self._legende()

    def effacer(self) -> None:
        """Retire tout ce qui est dessiné : la figure reste vide jusqu'au
        prochain mouvement de curseur."""
        for ax in self.axes_diag:
            vider_axe(ax)
            ax.set_title("")
        self.figure.legends = []

    def _legende(self) -> None:
        self.figure.legends = []
        self.figure.legend(
            handles=[Patch(fc=COULEUR_COMPRESSION, alpha=0.35,
                           label="Compression (σ > 0)"),
                     Patch(fc=COULEUR_TRACTION, alpha=0.35,
                           label="Traction (σ < 0)")],
            loc="lower center", ncol=2, frameon=False, fontsize=9)
