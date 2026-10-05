"""Tests du cœur de calcul : formules, conventions et relations."""

import pytest

from beton_precontraint.domaine import (
    CasDeCharge,
    Diagramme,
    SectionRectangulaire,
    effort_annulant_traction,
    excentrement_annulant_traction,
)

# b = 0.50 m, h = 1.20 m  ->  S = 0.60 m², I = 0.072 m⁴
SECTION = SectionRectangulaire(0.50, 1.20)


class TestSection:
    def test_grandeurs_geometriques(self):
        assert SECTION.surface == pytest.approx(0.60)
        assert SECTION.inertie == pytest.approx(0.072)
        assert SECTION.excentricite_max == pytest.approx(0.20)

    @pytest.mark.parametrize("b,h", [(0.0, 1.0), (1.0, 0.0), (-0.5, 1.0)])
    def test_dimensions_non_admises(self, b, h):
        with pytest.raises(ValueError):
            SectionRectangulaire(b, h)

    def test_sigma_flexion_signe(self):
        # M > 0 : compression en haut, traction en bas
        haut, bas = SECTION.extremes_flexion(0.80)
        assert haut > 0 > bas
        assert haut == pytest.approx(-bas)

    def test_sigma_axiale(self):
        assert SECTION.sigma_axiale(1.50) == pytest.approx(2.50)


class TestCasDeCharge:
    def test_moment_excentricite(self):
        cas = CasDeCharge(moment=0.80, effort=1.50, excentrement=0.20)
        assert cas.moment_excentricite == pytest.approx(-0.30)

    def test_somme_des_quatre_contraintes(self):
        cas = CasDeCharge(0.80, 1.50, 0.20)
        (sup_m, inf_m) = SECTION.extremes_flexion(cas.moment)
        axiale = cas.sigma_axiale(SECTION)
        (sup_m2, inf_m2) = SECTION.extremes_flexion(cas.moment_excentricite)
        sup, inf = cas.extremes_totaux(SECTION)
        assert sup == pytest.approx(sup_m + axiale + sup_m2)
        assert inf == pytest.approx(inf_m + axiale + inf_m2)

    def test_quatre_diagrammes_dans_l_ordre(self):
        cas = CasDeCharge(0.80, 1.50, 0.20)
        diagrammes = cas.diagrammes(SECTION)
        assert len(diagrammes) == 4
        assert all(isinstance(d, Diagramme) for d in diagrammes)
        # l'effort normal est uniforme, la flexion extérieure est symétrique
        axiale, exterieur = diagrammes[1], diagrammes[0]
        assert axiale.sigma_sup == pytest.approx(axiale.sigma_inf)
        assert exterieur.sigma_sup == pytest.approx(-exterieur.sigma_inf)

    def test_sigma_reference(self):
        assert Diagramme("t", -3.0, 1.0).sigma_reference == pytest.approx(3.0)

    def test_etat_traction_en_fibre_inferieure(self):
        cas = CasDeCharge(0.80, 0.0, 0.0)      # σ_inf = -6.67 MPa
        assert cas.etat_section(SECTION) == "Traction en fibre inférieure : 6.67 MPa"

    def test_etat_precontrainte_totale(self):
        cas = CasDeCharge(0.80, 4.00, 0.0)     # P = 6·M/h : σ_inf = 0
        assert cas.etat_section(SECTION) == "Précontrainte totale"

    def test_valeurs_du_cours(self):
        cas = CasDeCharge(0.80, 1.50, 0.20)
        assert cas.extremes_exterieur(SECTION) == pytest.approx((6.67, -6.67), abs=0.01)
        assert cas.sigma_axiale(SECTION) == pytest.approx(2.50)
        assert cas.extremes_excentricite(SECTION) == pytest.approx((-2.50, 2.50))
        assert cas.extremes_totaux(SECTION) == pytest.approx((6.67, -1.67), abs=0.01)


class TestRelations:
    @pytest.mark.parametrize("excentrement", [0.0, 0.20, 0.60])
    def test_seuil_pour_e_fixe(self, excentrement):
        """P = 6·M/(h + 6·e) annule exactement la contrainte en fibre inférieure."""
        moment = 0.80
        seuil = effort_annulant_traction(moment, SECTION, excentrement)
        cas = CasDeCharge(moment, seuil, excentrement)
        assert cas.extremes_totaux(SECTION)[1] == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize("effort", [1.0, 2.0, 4.0])
    def test_seuil_pour_p_fixe(self, effort):
        moment = 0.80
        seuil = excentrement_annulant_traction(moment, SECTION, effort)
        cas = CasDeCharge(moment, effort, seuil)
        assert cas.extremes_totaux(SECTION)[1] == pytest.approx(0.0, abs=1e-9)

    def test_les_deux_seuils_sont_inverses(self):
        moment, effort = 0.80, 2.0
        e = excentrement_annulant_traction(moment, SECTION, effort)
        p = effort_annulant_traction(moment, SECTION, e)
        assert p == pytest.approx(effort)

    def test_valeurs_du_cours(self):
        assert effort_annulant_traction(0.80, SECTION, 0.0) == pytest.approx(4.00)
        assert effort_annulant_traction(0.80, SECTION, 0.20) == pytest.approx(2.00)
        assert effort_annulant_traction(0.80, SECTION, 0.60) == pytest.approx(1.00)

    def test_excentrement_impossible_sans_effort(self):
        assert excentrement_annulant_traction(0.80, SECTION, 0.0) == float("inf")

    def test_excentrement_negatif_si_deja_comprime(self):
        # P > 6·M/h : la fibre inférieure est déjà comprimée pour e = 0, et
        # aucun e ≥ 0 ne peut ramener σ_inf à zéro
        assert excentrement_annulant_traction(0.80, SECTION, 5.00) < 0
