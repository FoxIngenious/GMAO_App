import customtkinter as tk
from tkinter import messagebox

from api_client import ajouter_materiel, modifier_materiel
from models import ETATS_MATERIEL


class AjouterMateriel(tk.CTkToplevel):
    def __init__(self, parent, on_success=None, materiel=None):
        super().__init__(parent)
        self.materiel = materiel
        self.on_success = on_success
        self.title("Modifier le matériel" if materiel else "Ajouter un matériel")
        self.geometry("500x580")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        conteneur = tk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(expand=True)
        champs = (
            ("Code du matériel", "code"),
            ("Nom du matériel", "nom"),
            ("Catégorie", "categorie"),
            ("Emplacement", "emplacement"),
            ("Service", "service"),
        )
        for ligne, (libelle, attribut) in enumerate(champs):
            tk.CTkLabel(conteneur, text=libelle, font=("Arial", 15)).grid(
                row=ligne * 2, column=0, columnspan=2, sticky="w", pady=(6, 0)
            )
            entree = tk.CTkEntry(conteneur, width=380, height=30, font=("Arial", 15))
            entree.grid(row=ligne * 2 + 1, column=0, columnspan=2, pady=(0, 2))
            if materiel:
                entree.insert(0, materiel[attribut] or "")
            setattr(self, attribut, entree)

        tk.CTkLabel(conteneur, text="État", font=("Arial", 15)).grid(
            row=10, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )
        self.etat = tk.CTkComboBox(conteneur, values=list(ETATS_MATERIEL), font=("Arial", 15))
        if materiel and materiel["etat"] not in ETATS_MATERIEL:
            self.etat.configure(values=[materiel["etat"], *ETATS_MATERIEL])
        self.etat.set(materiel["etat"] if materiel else ETATS_MATERIEL[0])
        self.etat.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        tk.CTkButton(conteneur, text="Valider", width=185, command=self.enregistrer).grid(
            row=12, column=0, pady=18
        )
        tk.CTkButton(conteneur, text="Annuler", width=185, command=self.destroy).grid(
            row=12, column=1, pady=18
        )

    def enregistrer(self):
        try:
            valeurs = (
                self.code.get(), self.nom.get(), self.categorie.get(),
                self.emplacement.get(), self.service.get(), self.etat.get(),
            )
            if self.materiel:
                modifier_materiel(self.materiel["id"], *valeurs)
            else:
                ajouter_materiel(*valeurs)
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        if self.on_success:
            self.on_success()
        self.destroy()
