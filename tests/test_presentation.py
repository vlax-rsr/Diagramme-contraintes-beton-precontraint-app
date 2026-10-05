"""Tests de l'interface : construction, réglages et cohérence des libellés.

Qt tourne hors écran (voir `conftest.py`) : ces tests vérifient la logique de la
fenêtre, pas son rendu à l'écran.
"""

import pytest
from PySide6.QtWidgets import QApplication

from beton_precontraint.domaine import CasDeCharge, SectionRectangulaire
from beton_precontraint.presentation import FenetreContraintes
from beton_precontraint.presentation.constantes import (
    EFFORT,
    EXCENTREMENT,
    HAUTEUR,
    LARGEUR,
    MOMENT,
    PLAGE_H,
)
from beton_precontraint.presentation.libelles import (
    libelle_etat,
    libelle_fibre,
    libelle_seuil,
    qualite,
)
from beton_precontraint.theme import COULEUR_COMPRESSION, COULEUR_TRACTION


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def fenetre(application):
    return FenetreContraintes()


class TestLibelles:
    """Fonctions pures : vérifiables sans fenêtre."""

    @pytest.mark.parametrize("sigma,attendu", [
        (0.0, "nulle"), (0.001, "nulle"), (3.0, "compression"), (-3.0, "traction")
    ])
    def test_qualite(self, sigma, attendu):
        assert qualite(sigma) == attendu

    def test_libelle_fibre(self):
        assert libelle_fibre("supérieure", 6.67) == (
            "Fibre supérieure : <b>+6.67 MPa</b> (compression)")

    def test_etat_bleu_si_tout_comprime(self):
        section = SectionRectangulaire(0.50, 1.20)
        texte, couleur = libelle_etat(section, CasDeCharge(0.80, 4.00, 0.0))
        assert texte == "Précontrainte totale"
        assert couleur == COULEUR_COMPRESSION

    def test_etat_rouge_si_fibre_en_traction(self):
        section = SectionRectangulaire(0.50, 1.20)
        texte, couleur = libelle_etat(section, CasDeCharge(0.80, 1.50, 0.20))
        assert "Traction en fibre inférieure" in texte
        assert couleur == COULEUR_TRACTION

    def test_seuil_exprime_dans_la_grandeur_non_reglee(self):
        section = SectionRectangulaire(0.50, 1.20)
        cas = CasDeCharge(0.80, 1.50, 0.20)
        # P vient d'être réglée : on lit l'excentrement correspondant
        assert "e = <b>0.333 m</b>" in libelle_seuil("P", section, cas)
        # e vient d'être réglé : on lit la force de précontrainte
        assert "P = <b>2.00 MN</b>" in libelle_seuil("e", section, cas)

    def test_seuil_hors_plange(self):
        section = SectionRectangulaire(0.50, 1.20)
        cas = CasDeCharge(0.80, 0.50, 0.20)
        assert "hors plage" in libelle_seuil("P", section, cas)

    def test_seuil_impossible_sans_precontrainte(self):
        section = SectionRectangulaire(0.50, 1.20)
        cas = CasDeCharge(0.80, 0.0, 0.20)
        assert "impossible" in libelle_seuil("P", section, cas)


class TestFenetre:
    def test_construction_avec_valeurs_initiales(self, fenetre):
        assert fenetre.section == SectionRectangulaire(LARGEUR, HAUTEUR)
        assert fenetre.cas_de_charge == CasDeCharge(MOMENT, EFFORT, EXCENTREMENT)
        assert len(fenetre.vue_contraintes.axes) == 4

    def test_libelles_remplis(self, fenetre):
        assert "+6.67" in fenetre.libelle_sup.text()
        assert "-1.67" in fenetre.libelle_inf.text()
        assert COULEUR_TRACTION in fenetre.libelle_etat.styleSheet()

    def test_changement_de_moment_redessine(self, fenetre):
        fenetre.reglage_m.definir(1.60)
        fenetre.mettre_a_jour("M")
        assert fenetre.section == SectionRectangulaire(LARGEUR, HAUTEUR)
        assert "+13.33" in fenetre.libelle_sup.text()

    def test_section_suit_la_largeur(self, fenetre):
        fenetre.reglage_b.definir(0.80)
        fenetre.mettre_a_jour("b")
        assert fenetre.section.b == pytest.approx(0.80)
        assert fenetre.vue_section.geometrie == (0.80, HAUTEUR)

    def test_hauteur_change_les_contraintes_mais_pas_la_geometrie(self, fenetre):
        """Changer h ne doit pas toucher aux colonnes des diagrammes."""
        avant = [ax.get_ylim() for ax in fenetre.vue_contraintes.axes]
        fenetre.reglage_h.definir(2.40)
        fenetre.mettre_a_jour("h")
        assert fenetre.section.h == pytest.approx(2.40)
        assert [ax.get_ylim() for ax in fenetre.vue_contraintes.axes] == avant

    def test_excentrement_borne_a_la_moitie_de_la_hauteur(self, fenetre):
        fenetre.reglage_h.definir(PLAGE_H[1])
        fenetre.mettre_a_jour("h")
        assert fenetre.reglage_e.maximum == pytest.approx(PLAGE_H[1] / 2, abs=0.005)
        fenetre.reglage_e.definir(PLAGE_H[1])       # au-delà de la plage
        assert fenetre.reglage_e.valeur <= fenetre.reglage_e.maximum

    def test_curseur_et_champ_restent_synchronises(self, fenetre):
        fenetre.reglage_p.curseur.setValue(500)     # 0 + 500 x 0.01 MN
        assert fenetre.reglage_p.valeur == pytest.approx(5.00)
        fenetre.reglage_p.champ.setValue(2.50)
        assert fenetre.reglage_p.curseur.value() == 250

    def test_seuil_suit_la_derniere_grandeur(self, fenetre):
        fenetre.reglage_p.definir(1.50)
        fenetre.mettre_a_jour("P")
        assert "e = <b>" in fenetre.libelle_reference.text()
        fenetre.reglage_e.definir(0.20)
        fenetre.mettre_a_jour("e")
        assert "P = <b>" in fenetre.libelle_reference.text()

    def test_effacer_le_canevas(self, fenetre):
        fenetre.vue_contraintes.effacer()
        assert all(ax.get_title() == "" for ax in fenetre.vue_contraintes.axes)
