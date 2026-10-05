"""Section cotée, en matplotlib.

Ce tracé ne sert que la figure d'export : dans la fenêtre, la section est
dessinée par QtCharts (`presentation.vue_section`). Il est autonome : il occupe
un cadre qui lui est propre, sans rapport avec l'échelle des diagrammes, et
cadré sur une échelle unique pour que 1 m horizontal vaille 1 m vertical — la
section garde donc ses proportions quelle que soit la taille du cadre, et rien
n'est rogné.
"""

from matplotlib.patches import Rectangle

from ..domaine import SectionRectangulaire

# Cotes en pixels, converties en mètres par l'itération de mise à l'échelle
PX_LONGUEUR_COTE = 26
PIXELS_COTE = 3.4       # debord du cadre à gauche et à droite
PIXELS_HAUTEUR = 3.5    # idem en haut et en bas


def tracer_section(section: SectionRectangulaire, ax) -> None:
    """Dessine la section cotée — largeur b dessous, hauteur h à gauche."""
    h, b = section.h, section.b
    cadre = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "gray", "alpha": 0.9}

    # Cadre réel en pixels. L'échelle est le plus grand nombre de mètres par
    # pixel qui fait tenir la section et ses cotes dans les deux sens : le
    # décalage des cotes, compté en pixels, en dépend, d'où quelques itérations.
    pos, fig = ax.get_position(), ax.figure
    largeur_px = max(pos.width * fig.bbox.width, 1.0)
    hauteur_px = max(pos.height * fig.bbox.height, 1.0)
    par_px = 0.06 * max(b, h) / PX_LONGUEUR_COTE
    for _ in range(5):
        decalage = PX_LONGUEUR_COTE * par_px
        par_px = max((b + PIXELS_COTE * decalage) / largeur_px,
                     (h + PIXELS_HAUTEUR * decalage) / hauteur_px)
    decalage = PX_LONGUEUR_COTE * par_px
    largeur_m, hauteur_m = largeur_px * par_px, hauteur_px * par_px

    ax.add_patch(Rectangle((-b / 2, -h / 2), b, h, fc="#e8e8e8", ec="k", lw=1.5))

    # axe de gravité, prolongé jusqu'aux deux cotes
    ax.plot([0, 0], [-h / 2 - 1.9 * decalage, h / 2 + 0.5 * decalage],
            color="gray", ls="-.", lw=1)

    # cote de hauteur, à gauche de la section, étiquette entre la cote et la section
    x = -b / 2 - 0.8 * decalage
    for yy in (-h / 2, h / 2):
        ax.plot([-b / 2, x - 0.15 * decalage], [yy, yy], color="k", lw=0.8)
    ax.annotate("", xy=(x, h / 2), xytext=(x, -h / 2),
                arrowprops={"arrowstyle": "<->", "lw": 1, "mutation_scale": 10})
    ax.text(x + 0.25 * decalage, 0, f"h = {h:.2f} m", rotation=90, ha="left",
            va="center", fontsize=9, bbox=cadre)

    # cote de largeur, sous la section
    y = -h / 2 - 1.3 * decalage
    for xx in (-b / 2, b / 2):
        ax.plot([xx, xx], [-h / 2, y + 0.25 * decalage], color="k", lw=0.8)
    ax.annotate("", xy=(-b / 2, y), xytext=(b / 2, y),
                arrowprops={"arrowstyle": "<->", "lw": 1, "mutation_scale": 10})
    ax.text(0, y - 0.55 * decalage, f"b = {b:.2f} m", ha="center", va="top",
            fontsize=9, bbox=cadre)

    # cadre calé sur le dessin, déformation impossible par construction :
    # les deux dimensions sortent de la même échelle, donc 1 m = 1 m
    ax.set_xlim(-b / 2 - 2.6 * decalage,
                -b / 2 - 2.6 * decalage + largeur_m)
    ax.set_ylim(-h / 2 - 2.4 * decalage,
                -h / 2 - 2.4 * decalage + hauteur_m)
    ax.set_axis_off()
