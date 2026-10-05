"""Repères du rendu matplotlib.

Les longueurs sont exprimées en mètres de la **hauteur affichée** des diagrammes
(``HAUTEUR_AFFICHAGE``), les fractions de la figure en fraction de sa largeur ou
de sa hauteur.
"""

# Hauteur de poutre dessinée dans les diagrammes, quelle que soit la hauteur
# réelle de la section : les quatre diagrammes gardent donc exactement la même
# hauteur à l'écran, et h ne change plus que les valeurs de σ. Seules les
# proportions b x h de la section dessinée à part tiennent compte de h.
HAUTEUR_AFFICHAGE = 1.20

MARGE_HAUT = 0.38       # m, espace au-dessus de la poutre (étiquettes)
MARGE_BAS = 0.50        # m, espace sous la poutre (étiquettes)
FACTEUR_LARGEUR = 1.12  # demi-largeur du cadre = FACTEUR * plus grande
                        # contrainte du diagramme, soit ~89 % de la demi-largeur
LARGEUR_CARACTERE = 8.0  # px, largeur moyenne d'un caractère d'étiquette (fontsize 9)

NB_POINTS = 101        # σ est linéaire en y : 101 points suffisent pour un
                       # diagramme à l'aspect parfaitement lisse

# --- répartition de la bande des diagrammes dans la figure -------------------
POIDS_DIAGRAMME = 2.5  # poids : largeur d'un diagramme de contraintes
POIDS_SIGNE = 0.55     # poids : largeur des colonnes « + », « = »

GAUCHE = 0.04           # fractions de la largeur
DROITE = 0.995
BAS = 0.11              # fractions de la hauteur : bandeau des diagrammes
HAUT = 0.82             # fractions de la hauteur : place des étiquettes du haut

# --- figure d'export (section au-dessus, diagrammes en dessous) --------------
TAILLE_EXPORT = (13.6, 7.4)   # pouces
CADRE_EXPORT_SECTION = (0.04, 0.60, 0.92, 0.39)
BANDE_EXPORT_DIAGRAMMES = (0.13, 0.55)
