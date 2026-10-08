import customtkinter as ctk
from tkinter import messagebox, ttk

from ajouter import AjouterMateriel
from impression import imprimer_fiche
from api_client import lister_materiels, supprimer_materiel


class ListesMateriels(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Matériels", font=("Arial", 40)).pack(pady=(20, 10))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=(0, 12))
        ctk.CTkButton(actions, text="+ Ajouter", command=self.ajouter).grid(row=0, column=0, padx=5)
        ctk.CTkButton(actions, text="Modifier", command=self.modifier).grid(row=0, column=1, padx=5)
        ctk.CTkButton(actions, text="Supprimer", fg_color="#b33939", command=self.supprimer).grid(row=0, column=2, padx=5)
        ctk.CTkButton(actions, text="Imprimer", command=self.imprimer).grid(row=0, column=3, padx=5)

        self.tableau = ttk.Treeview(
            self, columns=("id", "code", "nom", "categorie", "service", "emplacement", "etat"),
            show="headings", height=16,
        )
        for colonne, libelle in {
            "id": "ID", "code": "Code", "nom": "Nom", "categorie": "Catégorie",
            "service": "Service", "emplacement": "Emplacement", "etat": "État",
        }.items():
            self.tableau.heading(colonne, text=libelle)
            self.tableau.column(colonne, width=150, anchor="center")
        self.tableau.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.tableau.bind("<Double-1>", lambda _event: self.modifier())
        self.rafraichir()

    def rafraichir(self):
        self.tableau.delete(*self.tableau.get_children())
        for materiel in lister_materiels():
            self.tableau.insert(
                "", "end", iid=str(materiel["id"]),
                values=(
                    materiel["id"], materiel["code"], materiel["nom"], materiel["categorie"],
                    materiel["service"], materiel["emplacement"], materiel["etat"],
                ),
            )

    def materiel_selectionne(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez un matériel.", parent=self)
            return None
        identifiant = int(selection[0])
        return next(item for item in lister_materiels() if item["id"] == identifiant)

    def ajouter(self):
        AjouterMateriel(self.winfo_toplevel(), self.rafraichir)

    def modifier(self):
        materiel = self.materiel_selectionne()
        if materiel:
            AjouterMateriel(self.winfo_toplevel(), self.rafraichir, materiel)

    def supprimer(self):
        materiel = self.materiel_selectionne()
        if materiel and messagebox.askyesno("Confirmer", "Supprimer ce matériel ?", parent=self):
            supprimer_materiel(materiel["id"])
            self.rafraichir()

    def imprimer(self):
        materiel = self.materiel_selectionne()
        if materiel:
            imprimer_fiche("Fiche matériel", {
                "ID": materiel["id"], "Code": materiel["code"], "Nom": materiel["nom"],
                "Catégorie": materiel["categorie"], "Service": materiel["service"],
                "Emplacement": materiel["emplacement"], "État": materiel["etat"],
            })
