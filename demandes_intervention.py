import customtkinter as ctk
from tkinter import messagebox, ttk

from models import ajouter_demande, lister_demandes, modifier_demande, supprimer_demande
from impression import imprimer_fiche


class GestionDemandesIntervention(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Demandes d'intervention", font=("Arial", 36)).pack(pady=(20, 10))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=(0, 12))
        ctk.CTkButton(actions, text="+ Ajouter", command=self.ajouter).grid(row=0, column=0, padx=5)
        ctk.CTkButton(actions, text="Modifier", command=self.modifier).grid(row=0, column=1, padx=5)
        ctk.CTkButton(actions, text="Supprimer", fg_color="#b33939", command=self.supprimer).grid(row=0, column=2, padx=5)
        ctk.CTkButton(actions, text="Imprimer", command=self.imprimer).grid(row=0, column=3, padx=5)

        self.tableau = ttk.Treeview(
            self,
            columns=("id", "description", "technicien", "materiel", "statut"),
            show="headings",
            height=16,
        )
        for colonne, libelle, largeur in (
            ("id", "ID", 60),
            ("description", "Description", 330),
            ("technicien", "Technicien", 170),
            ("materiel", "Matériel", 170),
            ("statut", "Statut", 130),
        ):
            self.tableau.heading(colonne, text=libelle)
            self.tableau.column(colonne, width=largeur, anchor="w")
        self.tableau.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.tableau.bind("<Double-1>", lambda _event: self.modifier())
        self.rafraichir()

    def rafraichir(self):
        self.tableau.delete(*self.tableau.get_children())
        for demande in lister_demandes():
            self.tableau.insert(
                "", "end", iid=str(demande["id"]),
                values=(demande["id"], demande["description"], demande["technicien"], demande["materiel"], demande["statut"]),
            )

    def demande_selectionnee(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez une demande.", parent=self)
            return None
        identifiant = int(selection[0])
        valeurs = self.tableau.item(selection[0], "values")
        return identifiant, valeurs

    def ajouter(self):
        FormulaireDemande(self, self.rafraichir)

    def modifier(self):
        demande = self.demande_selectionnee()
        if demande is None:
            return
        identifiant, valeurs = demande
        FormulaireDemande(self, self.rafraichir, identifiant, *valeurs[1:])

    def supprimer(self):
        demande = self.demande_selectionnee()
        if demande is None:
            return
        if messagebox.askyesno("Confirmer", "Supprimer cette demande ?", parent=self):
            supprimer_demande(demande[0])
            self.rafraichir()

    def imprimer(self):
        demande = self.demande_selectionnee()
        if demande is None:
            return
        _identifiant, valeurs = demande
        try:
            imprimer_fiche("Demande d'intervention", {
                "ID": valeurs[0], "Description": valeurs[1], "Technicien": valeurs[2],
                "Matériel": valeurs[3], "Statut": valeurs[4],
            })
        except OSError as erreur:
            messagebox.showerror("Impression impossible", str(erreur), parent=self)


class FormulaireDemande(ctk.CTkToplevel):
    def __init__(self, parent, on_success, identifiant=None, description="", technicien="", materiel="", statut="À traiter"):
        super().__init__(parent)
        self.identifiant = identifiant
        self.on_success = on_success
        self.title("Modifier la demande" if identifiant else "Ajouter une demande")
        self.geometry("500x430")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        conteneur = ctk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(fill="both", expand=True, padx=35, pady=25)

        ctk.CTkLabel(conteneur, text="Description").pack(anchor="w")
        self.description = ctk.CTkTextbox(conteneur, width=420, height=120)
        self.description.insert("1.0", description)
        self.description.pack(pady=(2, 12))
        self.technicien = self._entree(conteneur, "Technicien", technicien)
        self.materiel = self._entree(conteneur, "Matériel", materiel)
        ctk.CTkLabel(conteneur, text="Statut").pack(anchor="w")
        self.statut = ctk.CTkComboBox(conteneur, values=["À traiter", "En cours", "Terminé", "Annulé"])
        self.statut.set(statut)
        self.statut.pack(pady=(2, 18))
        ctk.CTkButton(conteneur, text="Enregistrer", command=self.enregistrer).pack()

    @staticmethod
    def _entree(parent, libelle, valeur):
        ctk.CTkLabel(parent, text=libelle).pack(anchor="w")
        entree = ctk.CTkEntry(parent, width=420)
        entree.insert(0, valeur)
        entree.pack(pady=(2, 12))
        return entree

    def enregistrer(self):
        try:
            valeurs = (
                self.description.get("1.0", "end-1c"), self.technicien.get(),
                self.materiel.get(), self.statut.get(),
            )
            if self.identifiant is None:
                ajouter_demande(*valeurs)
            else:
                modifier_demande(self.identifiant, *valeurs)
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        self.on_success()
        self.destroy()
