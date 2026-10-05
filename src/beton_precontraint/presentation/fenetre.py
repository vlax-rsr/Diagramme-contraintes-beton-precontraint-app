"""Fenêtre principale : mise en page et orchestration des mises à jour.

La fenêtre ne contient aucun calcul. Elle assemble les widgets, lit les cinq
réglages, demande au domaine le cas de charge correspondant, puis passe le
résultat aux deux vues. Toute modification d'un réglage déclenche le même
chemin, ce qui garantit que les deux dessins et les libellés restent cohérents.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..domaine import CasDeCharge, SectionRectangulaire
from .constantes import (
    EFFORT,
    EXCENTREMENT,
    HAUTEUR,
    LARGEUR,
    LARGEUR_PANNEAU_SAISIE,
    MOMENT,
    NOM_FICHIER_EXPORT,
    PAS_E,
    PLAGE_B,
    PLAGE_H,
    PLAGE_M,
    PLAGE_P,
    TAILLE_MINIMALE,
    TITRE_FENETRE,
)
from .libelles import libelle_etat, libelle_fibre, libelle_seuil
from .reglages import Reglage
from .vue_contraintes import VueContraintes
from .vue_section import VueSection

MARGES_CADRE = 8         # px entre la fenêtre et son contenu
MARGES_GROUPE = 4        # px à l'intérieur du cadre de la section


class FenetreContraintes(QMainWindow):
    """Saisie des grandeurs, diagrammes et section, résultats chiffrés."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TITRE_FENETRE)
        self.setMinimumSize(*TAILLE_MINIMALE)

        # section et moment extérieur : saisie directe, sans curseur
        self.reglage_b = Reglage("b", "Largeur b", "m", PLAGE_B, LARGEUR, 2,
                                 avec_curseur=False)
        self.reglage_h = Reglage("h", "Hauteur h", "m", PLAGE_H, HAUTEUR, 2,
                                 avec_curseur=False)
        self.reglage_m = Reglage("M", "Moment M", "MN·m", PLAGE_M, MOMENT, 2,
                                 avec_curseur=False)

        # précontrainte et excentrement : curseur et saisie
        self.reglage_p = Reglage("P", "Précontrainte", "MN", PLAGE_P, EFFORT, 2)
        self.reglage_e = Reglage("e", "Excentrement", "m",
                                 (0.0, HAUTEUR / 2, PAS_E), EXCENTREMENT, 3)

        self.derniere_grandeur = "e"      # seuil exprimé dans l'autre grandeur
        self.libelle_sup = QLabel()
        self.libelle_inf = QLabel()
        self.libelle_reference = QLabel()
        self.libelle_etat = QLabel()
        self.bouton_export = QPushButton("Enregistrer l'image…")

        # La section a un cadre à elle, sous les boutons, et non une colonne
        # parmi les diagrammes : son échelle est indépendante de la leur, et son
        # dessin est produit par QtCharts, pas par matplotlib.
        self.vue_contraintes = VueContraintes()
        self.vue_section = VueSection()

        self.assembler()
        for reglage in self.reglages:
            reglage.modifie.connect(self.mettre_a_jour)
        self.bouton_export.clicked.connect(self.exporter)

        self.mettre_a_jour("e")

    @property
    def reglages(self) -> tuple[Reglage, ...]:
        return (self.reglage_b, self.reglage_h, self.reglage_m,
                self.reglage_p, self.reglage_e)

    # --------------------------------------------------------- mise en page
    def assembler(self) -> None:
        centrale = QWidget()
        disposition_globale = QHBoxLayout(centrale)
        disposition_globale.setContentsMargins(*(MARGES_CADRE,) * 4)
        disposition_globale.addWidget(self.panneau_saisie())
        disposition_globale.addWidget(self.vue_contraintes, 1)
        self.setCentralWidget(centrale)

    def panneau_saisie(self) -> QWidget:
        panneau = QWidget()
        panneau.setFixedWidth(LARGEUR_PANNEAU_SAISIE)
        disposition = QVBoxLayout(panneau)
        disposition.setContentsMargins(0, 0, 0, 0)

        geometrie = QGroupBox("Section et moment extérieur")
        formulaire = QFormLayout(geometrie)
        formulaire.addRow(self.reglage_b)
        formulaire.addRow(self.reglage_h)
        formulaire.addRow(self.reglage_m)
        disposition.addWidget(geometrie)

        reglages = QGroupBox("Précontrainte")
        verticale = QVBoxLayout(reglages)
        verticale.addWidget(self.reglage_p)
        verticale.addWidget(self.reglage_e)
        disposition.addWidget(reglages)

        resultats = QGroupBox("Résultats")
        verticale = QVBoxLayout(resultats)
        for libelle in (self.libelle_sup, self.libelle_inf,
                        self.libelle_reference, self.libelle_etat):
            verticale.addWidget(libelle)
        disposition.addWidget(resultats)

        affichage = QGroupBox("Affichage")
        verticale = QVBoxLayout(affichage)
        verticale.addWidget(self.bouton_export)
        disposition.addWidget(affichage)

        section = QGroupBox("Section")
        verticale = QVBoxLayout(section)
        verticale.setContentsMargins(*(MARGES_GROUPE,) * 4)
        # la section prend toute la hauteur restante : le dessin en profite
        verticale.addWidget(self.vue_section)
        disposition.addWidget(section, 1)

        return panneau

    # ------------------------------------------------------------- actions
    def exporter(self) -> None:
        defaut = Path.home() / NOM_FICHIER_EXPORT
        nom, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la figure", str(defaut),
            "Images PNG (*.png);;Images JPEG (*.jpg);;Tous les fichiers (*)")
        if nom:
            # section et diagrammes réunis dans une même image
            figure = self.vue_contraintes.figure_export(self.section,
                                                        self.cas_de_charge)
            figure.savefig(nom, dpi=150, bbox_inches="tight")

    # ---------------------------------------------------------- affichage
    @property
    def section(self) -> SectionRectangulaire:
        return SectionRectangulaire(self.reglage_b.valeur, self.reglage_h.valeur)

    @property
    def cas_de_charge(self) -> CasDeCharge:
        return CasDeCharge(moment=self.reglage_m.valeur,
                           effort=self.reglage_p.valeur,
                           excentrement=self.reglage_e.valeur)

    def mettre_a_jour(self, grandeur: str = "") -> None:
        """Recalcule et redessine tout (temps réel).

        `grandeur` est le nom court du réglage qui vient de changer : il sert à
        afficher le seuil de fibre inférieure nulle dans la grandeur que l'on
        n'est pas en train de régler.
        """
        if grandeur:
            self.derniere_grandeur = grandeur
        # l'excentrement reste dans la section : 0 ≤ e ≤ h/2
        self.reglage_e.definir_plage(0.0, self.reglage_h.valeur / 2)

        section, cas = self.section, self.cas_de_charge
        self.vue_contraintes.mettre_a_jour(cas.diagrammes(section))
        self.vue_section.definir_section(section)

        self.afficher_resultats(section, cas)

    def afficher_resultats(self, section: SectionRectangulaire,
                           cas: CasDeCharge) -> None:
        sigma_sup, sigma_inf = cas.extremes_totaux(section)
        self.libelle_sup.setText(libelle_fibre("supérieure", sigma_sup))
        self.libelle_inf.setText(libelle_fibre("inférieure", sigma_inf))
        self.libelle_reference.setText(
            libelle_seuil(self.derniere_grandeur, section, cas))
        texte, couleur = libelle_etat(section, cas)
        self.libelle_etat.setText(texte)
        self.libelle_etat.setStyleSheet(
            f"font-weight: bold; color: {couleur}")
