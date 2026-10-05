"""Contraintes normales d'une poutre en béton précontraint.

Application PySide6 de bureau : on règle la section, le moment extérieur M, la
précontrainte P et son excentrement e, et l'on lit les quatre diagrammes de la
superposition M + P + M₂ = σ, ainsi que la section cotée.

Le code est réparti en trois couches, qui ne dépendent que dans un sens :

    domaine        cœur de calcul pur, sans aucun import graphique ;
    rendu          tracé matplotlib (diagrammes, section, figure d'export) ;
    presentation   widgets PySide6 et libellés, qui affichent le domaine.

`theme` regroupe la palette commune aux deux techniques de dessin.
"""

__version__ = "1.0.0"

__all__ = ["__version__"]
