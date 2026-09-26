import customtkinter as ctk
from datetime import datetime


def imprimer_fiche(titre, donnees, parent=None):
    """Affiche le ticket de la fiche, sans envoyer à l'imprimante."""
    lignes = [titre, "=" * len(titre), ""]
    for libelle, valeur in donnees.items():
        lignes.append(f"{libelle} : {valeur if valeur not in (None, "") else '-'}")
    lignes.append("")
    lignes.append("Ticket généré le " + datetime.now().strftime("%d/%m/%Y %H:%M"))

    fenetre = ctk.CTkToplevel(parent)
    fenetre.title(titre)
    fenetre.geometry("480x420")
    zone = ctk.CTkTextbox(fenetre, width=460, height=330)
    zone.pack(padx=15, pady=15)
    zone.insert("1.0", "\n".join(lignes))
    zone.configure(state="disabled")
    ctk.CTkButton(fenetre, text="Fermer", command=fenetre.destroy).pack(pady=(0, 15))
    return "\n".join(lignes)
