"""Configuration commune aux tests.

- `src` est ajouté à `sys.path` pour que `pytest` fonctionne dans un clone
  neuf, sans avoir à installer le paquet ;
- Qt et matplotlib sont mis en mode hors écran, sinon la création d'un widget
  échoue sur une machine sans écran (CI, session distante).
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE / "src"))
