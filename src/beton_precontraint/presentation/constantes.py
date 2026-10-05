"""Valeurs par défaut, plages de réglage et dimensions de la fenêtre.

Ces nombres appartiennent à l'interface, pas au calcul : les déplacer ici évite
de les laisser se confondre avec des constantes physiques.
"""

TITRE_FENETRE = "Diagramme des contraintes — béton précontraint"

TAILLE_FENETRE = (1320, 740)
TAILLE_MINIMALE = (1080, 620)
TAILLE_CANEVAS_MINIMALE = (720, 420)
TAILLE_FIGURE = (11.0, 4.4)      # pouces : ratio du canevas dans la fenêtre
LARGEUR_PANNEAU_SAISIE = 310     # px, colonne de gauche

# valeurs initiales : la section du cours, et une précontrainte dans le noyau
LARGEUR = 0.50          # m
HAUTEUR = 1.20          # m
MOMENT = 0.80           # MN·m, positif : flèche vers le bas
EFFORT = 1.50           # MN
EXCENTREMENT = 0.20     # m, soit h/6 : la limite du noyau

PLAGE_B = (0.10, 2.00, 0.01)           # m
PLAGE_H = (0.20, 3.00, 0.01)           # m
PLAGE_M = (0.01, 5.00, 0.01)           # MN·m : M reste strictement positif
PLAGE_P = (0.00, 15.00, 0.01)          # MN
PAS_E = 0.005                           # m, une subdivision de h/2

NOM_FICHIER_EXPORT = "diagramme_contraintes.png"
