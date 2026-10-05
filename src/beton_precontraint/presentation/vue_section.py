"""Section cotée, dessinée par le module graphique intégré de PySide6.

La section est tracée dans un ``QChartView`` par des polylignes
(``QLineSeries``) exprimées en mètres : les cotes suivent donc la section quand
elle change de dimensions, et ce dessin ne dépend pas de matplotlib — il suit le
thème de l'interface et coûte bien moins cher à redessiner.

La zone de tracé occupe tout le cadre disponible, et ce sont les plages d'axes
qui sont calculées pour que le dessin soit centré et sans déformation : la
même échelle est appliquée horizontalement et verticalement, et les deux plages
sont élargies de la même quantité, ce qui centre la section.
"""

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPalette, QPen
from PySide6.QtWidgets import (
    QGraphicsTextItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..domaine import SectionRectangulaire
from ..theme import COULEUR_ATTACHE, COULEUR_COTE, COULEUR_SECTION, COULEUR_TEXTE_COTE

MARGE_TEXTE = 10.0      # px laissés pour les cotes, de part et d'autre
TAILLE_MINIMALE = (250, 170)
DEBUT = 0.06            # m : demi-décalage minimal des cotes
FIN = 0.20              # m : demi-décalage maximal des cotes
TAUX_COTE = 0.18        # fraction de h retenue pour le décalage des cotes


class VueSection(QWidget):
    """Section rectangulaire cotée, dessinée par QtCharts et centrée."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(*TAILLE_MINIMALE)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.section = SectionRectangulaire(0.50, 1.20)
        self.geometrie = None
        self.series = []
        self.etiquettes = {}
        self.cotes = (0.0, 0.0)
        self.emprise = (0.0, 1.0, 0.0, 1.0)

        self.graphique = QChart()
        self.graphique.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.graphique.setBackgroundVisible(False)
        self.graphique.setTitle("")
        self.graphique.legend().setVisible(False)
        # sans marge de layout, la zone de tracé peut occuper tout le cadre
        self.graphique.layout().setContentsMargins(0, 0, 0, 0)
        self.axe_x = self._creer_axe(Qt.AlignmentFlag.AlignBottom)
        self.axe_y = self._creer_axe(Qt.AlignmentFlag.AlignLeft)

        self.vue = QChartView(self.graphique)
        self.vue.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.vue.setStyleSheet("background: transparent;")
        disposition = QVBoxLayout(self)
        disposition.setContentsMargins(0, 0, 0, 0)
        disposition.addWidget(self.vue)

        self.definir_section(self.section)

    def _creer_axe(self, alignement: Qt.AlignmentFlag) -> QValueAxis:
        axe = QValueAxis()
        axe.setVisible(False)
        axe.setLabelFormat("")
        self.graphique.addAxis(axe, alignement)
        return axe

    def _nouvelle_serie(self, points, couleur: str, largeur: float = 1.6,
                        pointilles: bool = False) -> QLineSeries:
        style = Qt.PenStyle.DotLine if pointilles else Qt.PenStyle.SolidLine
        serie = QLineSeries()
        for x, y in points:
            serie.append(QPointF(x, y))
        serie.setPen(QPen(QColor(couleur), largeur, style))
        self.graphique.addSeries(serie)
        serie.attachAxis(self.axe_x)
        serie.attachAxis(self.axe_y)
        self.series.append(serie)
        return serie

    def _etiquette(self, cle: str) -> QGraphicsTextItem:
        """Cote affichée, sur fond de la couleur du cadre pour masquer la ligne."""
        if cle not in self.etiquettes:
            item = QGraphicsTextItem()
            item.setFont(QFont(self.font().family(), 9))
            item.setDefaultTextColor(QColor(COULEUR_TEXTE_COTE))
            item.document().setDocumentMargin(0.0)
            self.vue.scene().addItem(item)
            self.etiquettes[cle] = item
        return self.etiquettes[cle]

    def _ecrire(self, cle: str, texte: str) -> None:
        fond = self.palette().color(QPalette.ColorRole.Window).name()
        self._etiquette(cle).setHtml(
            f'<p style="margin:0"><span style="background-color:{fond}">'
            f'{texte}</span></p>')

    def definir_section(self, section: SectionRectangulaire) -> None:
        """Redessine la section et ses cotes.

        La géométrie n'est reconstruite que si b ou h change : à chaque
        changement de P, de M ou de e, il suffit de replacer les deux cotes.
        """
        b, h = section.b, section.h
        if self.geometrie == (b, h):
            self._placer_textes()
            return
        self.geometrie = (b, h)
        self.section = section

        for serie in self.series:
            self.graphique.removeSeries(serie)
            serie.deleteLater()
        self.series.clear()

        demi_b, demi_h = b / 2, h / 2
        # décalage des cotes et de l'axe de gravité : proportionnel à h, mais
        # borné, pour rester lisible sur une section plate comme très haute
        d = min(max(TAUX_COTE * h, DEBUT), FIN)
        e = 0.25 * d          # traits d'attache
        a = 0.22 * d          # demi-flèche des cotes
        x_cote = -demi_b - 0.50 * d
        y_cote = -demi_h - 0.50 * d
        self.cotes = (x_cote, y_cote)

        self._nouvelle_serie(
            [(-demi_b, -demi_h), (demi_b, -demi_h), (demi_b, demi_h),
             (-demi_b, demi_h), (-demi_b, -demi_h)],
            COULEUR_SECTION, 2.0)
        self._nouvelle_serie([(0.0, -demi_h - d), (0.0, demi_h + d)],
                             COULEUR_COTE, 1.0, True)

        for signe in (-1.0, 1.0):
            # cote de h, à gauche : flèches vers le haut et le bas
            y = signe * demi_h
            self._nouvelle_serie(
                [(x_cote - a, y - signe * 2 * a), (x_cote, y),
                 (x_cote + a, y - signe * 2 * a)], COULEUR_COTE, 1.2)
            self._nouvelle_serie([(-demi_b - 0.10 * d, y), (x_cote - e, y)],
                                 COULEUR_ATTACHE, 0.9)
            # cote de b, en dessous : flèches vers la gauche et la droite
            x = signe * demi_b
            self._nouvelle_serie(
                [(x - signe * 2 * a, y_cote - a), (x, y_cote),
                 (x - signe * 2 * a, y_cote + a)], COULEUR_COTE, 1.2)
            self._nouvelle_serie([(x, -demi_h - 0.10 * d), (x, y_cote - e)],
                                 COULEUR_ATTACHE, 0.9)
        self._nouvelle_serie([(x_cote, -demi_h), (x_cote, demi_h)],
                             COULEUR_COTE, 1.0)
        self._nouvelle_serie([(-demi_b, y_cote), (demi_b, y_cote)],
                             COULEUR_COTE, 1.0)

        # emprise : cotes à gauche et en bas, axe de gravité au-dessus et
        # en dessous de la section
        self.emprise = (x_cote - e, demi_b, -demi_h - d, demi_h + d)
        self._ecrire("h", f"h = {h:.2f} m")
        self._ecrire("b", f"b = {b:.2f} m")
        self._ajuster()

    def _marges(self) -> tuple[float, float]:
        """Marge à laisser autour du dessin, en px, selon les cotes affichées.

        La cote de h est posée sur sa ligne, à gauche de la section : la marge
        doit donc accueillir la moitié de sa largeur.
        """
        cadre = self._etiquette("h").boundingRect()
        return (max(MARGE_TEXTE, cadre.width() / 2 + 8.0), MARGE_TEXTE)

    def _calculer_plages(self) -> None:
        """Remplit le cadre et règle les deux axes sur une échelle unique.

        La zone de tracé est imposée au graphique, ce qui évite les marges
        automatiques de QtCharts : le dessin profite de toute la place. Les
        deux plages sont centrées sur la section et larges de zone / ppm, donc
        1 m vaut 1 m horizontalement comme verticalement, et le dessin reste au
        milieu du cadre.
        """
        largeur, hauteur = self.graphique.size().width(), self.graphique.size().height()
        if largeur <= 0 or hauteur <= 0:
            return
        zone = QRectF(0.0, 0.0, float(largeur), float(hauteur))
        self.graphique.setPlotArea(zone)
        x_min, x_max, y_min, y_max = self.emprise
        marge_x, marge_y = self._marges()
        # échelle commune aux deux sens : la plus grande qui fait tenir la
        # section et ses cotes dans le cadre
        ppm = min((zone.width() - 2 * marge_x) / max(x_max - x_min, 1e-9),
                  (zone.height() - 2 * marge_y) / max(y_max - y_min, 1e-9))
        ppm = max(ppm, 1e-9)
        # chaque plage est centrée sur la section et large de zone / ppm : un
        # mètre occupe donc ppm pixels dans les deux sens, et le dessin reste
        # au milieu du cadre
        centre_x, centre_y = (x_min + x_max) / 2, (y_min + y_max) / 2
        demi_x = zone.width() / 2 / ppm
        demi_y = zone.height() / 2 / ppm
        self.axe_x.setRange(centre_x - demi_x, centre_x + demi_x)
        self.axe_y.setRange(centre_y - demi_y, centre_y + demi_y)

    def _ajuster(self) -> None:
        """Recale les plages et les cotes sur la taille courante du cadre."""
        self._calculer_plages()
        self._placer_textes()

    def _vers_scene(self, x: float, y: float):
        zone = self.graphique.plotArea()
        if zone.width() <= 0 or zone.height() <= 0:
            return None
        px = zone.left() + (x - self.axe_x.min()) / (
            self.axe_x.max() - self.axe_x.min()) * zone.width()
        py = zone.bottom() - (y - self.axe_y.min()) / (
            self.axe_y.max() - self.axe_y.min()) * zone.height()
        return px, py

    def _placer_textes(self) -> None:
        """Place chaque cote au milieu de sa ligne de cote."""
        x_cote, y_cote = self.cotes
        position = self._vers_scene(x_cote, 0.0)
        if position is not None:
            self._centrer(self._etiquette("h"), *position)
        position = self._vers_scene(0.0, y_cote)
        if position is not None:
            self._centrer(self._etiquette("b"), *position)

    @staticmethod
    def _centrer(item: QGraphicsTextItem, px: float, py: float) -> None:
        cadre = item.boundingRect()
        item.setPos(px - cadre.width() / 2 - cadre.left(),
                    py - cadre.height() / 2 - cadre.top())

    def resizeEvent(self, evenement):
        super().resizeEvent(evenement)
        self._ajuster()
        # QtCharts recalcule sa zone après l'événement : on recale une seconde
        # fois, sur la zone définitive
        QTimer.singleShot(0, self._ajuster)

    def showEvent(self, evenement):
        super().showEvent(evenement)
        self._ajuster()
        QTimer.singleShot(0, self._ajuster)
