import customtkinter as tk
from tkinter import messagebox

from models import ajouter_materiel, modifier_materiel


class AjouterMateriel(tk.CTkToplevel):
    def __init__(self, parent, on_success=None, materiel=None):
        super().__init__(parent)
        self.materiel = materiel
        self.title("Modifier le matériel" if materiel else "Ajouter un matériel")
        self.geometry("500x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.on_success = on_success

        input_contenaire = tk.CTkFrame(self, fg_color="transparent")
        input_contenaire.pack(expand=True)
        champs = (
            ("Nom du matériel", "Nom du matériel", "nom"),
            ("Catégorie", "Catégorie", "categorie"),
            ("Emplacement", "Emplacement (ex. labo Ginfo)", "emplacement"),
            ("État", "État du matériel", "etat"),
        )
        for ligne, (libelle, exemple, attribut) in enumerate(champs):
            tk.CTkLabel(input_contenaire, text=libelle, font=("Arial", 16)).grid(
                row=ligne * 2, column=0, columnspan=2, sticky="w", pady=(8, 0)
            )
            entree = tk.CTkEntry(
                input_contenaire, width=380, height=30, placeholder_text=exemple, font=("Arial", 16)
            )
            entree.grid(row=ligne * 2 + 1, column=0, columnspan=2, pady=(0, 4))
            if materiel:
                entree.insert(0, materiel[attribut])
            setattr(self, attribut, entree)

        tk.CTkButton(input_contenaire, text="Enregistrer", width=185, command=self.enregistrer).grid(
            row=8, column=0, pady=20
        )
        tk.CTkButton(input_contenaire, text="Annuler", width=185, command=self.destroy).grid(
            row=8, column=1, pady=20
        )

    def enregistrer(self):
        try:
            valeurs = (self.nom.get(), self.categorie.get(), self.emplacement.get(), self.etat.get())
            if self.materiel:
                modifier_materiel(self.materiel["id"], *valeurs)
            else:
                ajouter_materiel(*valeurs)
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        except Exception as erreur:
            messagebox.showerror(
                "Erreur", f"Impossible d'enregistrer le matériel : {erreur}", parent=self
            )
            return

        if self.on_success:
            self.on_success()
        self.destroy()
