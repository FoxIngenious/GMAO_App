import os
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4


def imprimer_fiche(titre: str, donnees: dict) -> None:
    """Envoie une fiche texte à l'imprimante Windows par défaut."""
    lignes = [titre, "=" * len(titre), ""]
    lignes.extend(f"{libelle} : {valeur}" for libelle, valeur in donnees.items())
    lignes.extend(["", f"Imprimé le : {datetime.now():%d/%m/%Y %H:%M}"])
    chemin = Path(tempfile.gettempdir()) / f"gmao_{uuid4().hex}.txt"
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    os.startfile(str(chemin), "print")
