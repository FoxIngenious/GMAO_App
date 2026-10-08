import customtkinter as ctk
from tkinter import messagebox, ttk

from impression import imprimer_fiche
from api_client import (
    ajouter_technicien,
    lister_techniciens,
    modifier_technicien,
    supprimer_technicien,
)


class GestionTechniciens(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Techniciens", font=("Arial", 36)).pack(pady=(20, 10))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=(0, 12))
        ctk.CTkButton(actions, text="+ Ajouter", command=self.ajouter).grid(row=0, column=0, padx=5)
        ctk.CTkButton(actions, text="Modifier", command=self.modifier).grid(row=0, column=1, padx=5)
        ctk.CTkButton(actions, text="Supprimer", fg_color="#b33939", command=self.supprimer).grid(row=0, column=2, padx=5)
        ctk.CTkButton(actions, text="Imprimer", command=self.imprimer).grid(row=0, column=3, padx=5)

        self.tableau = ttk.Treeview(
            self, columns=("id", "nom", "specialite", "telephone"), show="headings", height=16
        )
        for colonne, libelle in {
            "id": "ID", "nom": "Nom", "specialite": "Spécialité", "telephone": "Téléphone",
        }.items():
            self.tableau.heading(colonne, text=libelle)
            self.tableau.column(colonne, width=200, anchor="center")
        self.tableau.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.tableau.bind("<Double-1>", lambda _event: self.modifier())
        self.rafraichir()

    def rafraichir(self):
        self.tableau.delete(*self.tableau.get_children())
        for technicien in lister_techniciens():
            self.tableau.insert(
                "", "end", iid=str(technicien["id"]),
                values=(
                    technicien["id"], technicien["nom"], technicien["specialite"],
                    technicien["telephone"],
                ),
            )

    def technicien_selectionne(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez un technicien.", parent=self)
            return None
        identifiant = int(selection[0])
        return next(item for item in lister_techniciens() if item["id"] == identifiant)

    def ajouter(self):
        FormulaireTechnicien(self, self.rafraichir)

    def modifier(self):
        technicien = self.technicien_selectionne()
        if technicien:
            FormulaireTechnicien(self, self.rafraichir, technicien)

    def supprimer(self):
        technicien = self.technicien_selectionne()
        if technicien and messagebox.askyesno("Confirmer", "Supprimer ce technicien ?", parent=self):
            supprimer_technicien(technicien["id"])
            self.rafraichir()

    def imprimer(self):
        technicien = self.technicien_selectionne()
        if technicien:
            imprimer_fiche("Fiche technicien", {
                "ID": technicien["id"], "Nom": technicien["nom"],
                "Spécialité": technicien["specialite"], "Téléphone": technicien["telephone"],
            })


class FormulaireTechnicien(ctk.CTkToplevel):
    def __init__(self, parent, on_success, technicien=None):
        super().__init__(parent)
        self.technicien = technicien
        self.on_success = on_success
        self.title("Modifier le technicien" if technicien else "Ajouter un technicien")
        self.geometry("440x400")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        conteneur = ctk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(fill="both", expand=True, padx=30, pady=20)
        self.nom = self._champ(conteneur, "Nom", technicien["nom"] if technicien else "")
        self.specialite = self._champ(conteneur, "Spécialité", technicien["specialite"] if technicien else "")
        self.telephone = self._champ(conteneur, "Téléphone", technicien["telephone"] if technicien else "")

        boutons = ctk.CTkFrame(conteneur, fg_color="transparent")
        boutons.pack(pady=16)
        ctk.CTkButton(boutons, text="Valider", width=175, command=self.enregistrer).pack(side="left", padx=5)
        ctk.CTkButton(boutons, text="Annuler", width=175, command=self.destroy).pack(side="left", padx=5)

    def _champ(self, parent, libelle, valeur):
        ctk.CTkLabel(parent, text=libelle).pack(anchor="w")
        entree = ctk.CTkEntry(parent, width=360)
        entree.insert(0, valeur or "")
        entree.pack(pady=(2, 12))
        return entree

    def enregistrer(self):
        try:
            valeurs = (self.nom.get(), self.specialite.get(), self.telephone.get())
            if self.technicien:
                modifier_technicien(self.technicien["id"], *valeurs)
            else:
                ajouter_technicien(*valeurs)
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        self.on_success()
        self.destroy()
