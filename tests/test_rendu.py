"""Tests du rendu : géométrie des diagrammes et figure d'export.

Les deux principes de rendu sont vérifiés ici :

- la hauteur dessinée est **constante**, indépendante de la hauteur réelle h ;
- aucune échelle de contrainte n'est **partagée** entre les diagrammes.
"""

import matplotlib
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from beton_precontraint.domaine import CasDeCharge, Diagramme, SectionRectangulaire
from beton_precontraint.rendu import VueDiagrammes, figure_complete
from beton_precontraint.rendu.constantes import (
    FACTEUR_LARGEUR,
    HAUTEUR_AFFICHAGE,
    MARGE_BAS,
    MARGE_HAUT,
)

matplotlib.use("Agg")

# h très différent de la hauteur affichée : la géométrie ne doit pas bouger
HAUTEURS = (0.20, 1.20, 3.00)
CAS = [(0.80, 1.50, 0.20), (5.00, 15.00, 0.60), (0.01, 0.05, 0.005),
       (0.80, 0.20, 0.60), (0.80, 0.00, 0.00), (0.00, 0.00, 0.00)]


def hauteur_pixels(ax, ligne) -> float:
    """Hauteur à l'écran d'une ligne, en pixels."""
    ys = ligne.get_ydata()
    bas = ax.transData.transform((0.0, ys.min()))[1]
    haut = ax.transData.transform((0.0, ys.max()))[1]
    return haut - bas


@pytest.fixture
def figure():
    figure = Figure(figsize=(11.0, 4.4), facecolor="white")
    FigureCanvasAgg(figure)
    return figure


@pytest.fixture
def vue(figure):
    return VueDiagrammes(figure)


class TestHauteurConstante:
    """La poutre dessinée garde la même taille, quel que soit h."""

    @pytest.mark.parametrize("h", HAUTEURS)
    def test_plages_verticales_independant_de_la_section(self, vue, h):
        for moment, effort, excentrement in CAS:
            section = SectionRectangulaire(0.50, h)
            cas = CasDeCharge(moment, effort, min(excentrement, h / 2))
            vue.mettre_a_jour(cas.diagrammes(section))
            attendu = (-HAUTEUR_AFFICHAGE / 2 - MARGE_BAS,
                       HAUTEUR_AFFICHAGE / 2 + MARGE_HAUT)
            for ax in vue.axes_diag + vue.axes_symbole:
                assert ax.get_ylim() == pytest.approx(attendu)

    @pytest.mark.parametrize("h", HAUTEURS)
    def test_axe_de_reference_couvre_la_hauteur_affichee(self, vue, h):
        """Le trait vertical de la poutre va bien de -h/2 à +h/2 affiché."""
        section = SectionRectangulaire(0.50, h)
        vue.mettre_a_jour(CasDeCharge(0.80, 1.50, 0.0).diagrammes(section))
        demi = HAUTEUR_AFFICHAGE / 2
        trait = max(vue.axes_diag[0].lines, key=lambda ligne: ligne.get_linewidth())
        ydata = trait.get_ydata()
        assert ydata.min() == pytest.approx(-demi)
        assert ydata.max() == pytest.approx(demi)

    def test_hauteur_dessinee_identique_pour_toute_hauteur(self, vue, figure):
        """Le plus grand trait vertical fait toujours la même taille en pixels."""
        tailles = []
        for h in HAUTEURS:
            section = SectionRectangulaire(0.50, h)
            vue.mettre_a_jour(CasDeCharge(0.80, 1.50, 0.0).diagrammes(section))
            figure.canvas.draw()
            ax = vue.axes_diag[0]
            trait = max(ax.lines, key=lambda ligne: ligne.get_linewidth())
            tailles.append(round(hauteur_pixels(ax, trait), 6))
        assert len(set(tailles)) == 1


class TestPasDEchelleCommune:
    @pytest.mark.parametrize("moment,effort,excentrement", CAS)
    def test_largeurs_independantes(self, vue, moment, effort, excentrement):
        section = SectionRectangulaire(0.50, 1.20)
        cas = CasDeCharge(moment, effort, min(excentrement, 0.60))
        diagrammes = cas.diagrammes(section)
        vue.mettre_a_jour(diagrammes)

        non_nuls = [(d, ax) for d, ax in zip(diagrammes, vue.axes_diag, strict=True)
                    if d.sigma_reference > 0]
        for diagramme, ax in non_nuls:
            demi = ax.get_xlim()[1]
            assert diagramme.sigma_reference / demi == pytest.approx(1 / FACTEUR_LARGEUR)

    def test_largeurs_suivant_les_contraintes_de_chaque_diagramme(self, vue):
        """Cas où les quatre amplitudes diffèrent : quatre largeurs distinctes."""
        section = SectionRectangulaire(0.50, 1.20)
        diagrammes = CasDeCharge(5.00, 15.00, 0.60).diagrammes(section)
        vue.mettre_a_jour(diagrammes)
        largeurs = [round(ax.get_xlim()[1], 6) for ax in vue.axes_diag]
        assert len(set(largeurs)) == 4

    @pytest.mark.parametrize("moment,effort,excentrement", CAS)
    def test_chaque_diagramme_remplit_sa_colonne(self, vue, figure,
                                                 moment, effort, excentrement):
        section = SectionRectangulaire(0.50, 1.20)
        cas = CasDeCharge(moment, effort, min(excentrement, 0.60))
        diagrammes = cas.diagrammes(section)
        vue.mettre_a_jour(diagrammes)
        figure.canvas.draw()

        for ax, diagramme in zip(vue.axes_diag, diagrammes, strict=True):
            if diagramme.sigma_reference <= 0:
                continue
            zone = ax.get_window_extent()
            centre = ax.transData.transform((0.0, 0.0))[0]
            x = [ax.transData.transform(v)[0]
                 for collection in ax.collections
                 for chemin in collection.get_paths()
                 for v in chemin.vertices]
            if not x:
                continue
            demi = zone.width / 2
            # la pointe la plus éloignée touche 89 % de la demi-largeur
            assert max((max(x) - centre) / demi, (centre - min(x)) / demi) == (
                pytest.approx(1 / FACTEUR_LARGEUR, abs=0.01))

    def test_les_quatre_cases_ont_la_meme_hauteur(self, vue, figure):
        vue.mettre_a_jour(CasDeCharge().diagrammes(SectionRectangulaire(0.5, 1.2)))
        figure.canvas.draw()
        hauteurs = {round(ax.get_window_extent().height, 6) for ax in vue.axes_diag}
        assert len(hauteurs) == 1


class TestDiagrammeNul:
    def test_pas_de_transformation_singuliere(self, vue, figure):
        nul = Diagramme("nul", 0.0, 0.0)
        vue.mettre_a_jour((nul,) * 4)
        figure.canvas.draw()
        bas, haut = vue.axes_diag[0].get_xlim()
        assert bas < 0 < haut


class TestFigureComplete:
    def test_section_et_diagrammes_reunis(self):
        figure = figure_complete(SectionRectangulaire(0.50, 1.20),
                                 CasDeCharge(0.80, 1.50, 0.20))
        assert len(figure.axes) == 8       # 4 diagrammes, 3 signes, 1 section

    def test_export_ecrit_un_fichier(self, tmp_path):
        chemin = tmp_path / "diagramme.png"
        figure_complete(SectionRectangulaire(0.50, 1.20),
                        CasDeCharge(0.80, 1.50, 0.20)).savefig(chemin, dpi=72)
        assert chemin.exists() and chemin.stat().st_size > 0
