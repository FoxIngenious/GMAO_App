import customtkinter as ctk
from tkinter import messagebox, ttk

from models import ajouter_bon_travail, lister_bons_travail, modifier_bon_travail, supprimer_bon_travail
from impression import imprimer_fiche


class GestionBonsTravail(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Bons de travail", font=("Arial", 36)).pack(pady=(20, 10))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=(0, 12))
        ctk.CTkButton(actions, text="+ Ajouter", command=self.ajouter).grid(row=0, column=0, padx=5)
        ctk.CTkButton(actions, text="Modifier", command=self.modifier).grid(row=0, column=1, padx=5)
        ctk.CTkButton(actions, text="Supprimer", fg_color="#b33939", command=self.supprimer).grid(row=0, column=2, padx=5)
        ctk.CTkButton(actions, text="Imprimer", command=self.imprimer).grid(row=0, column=3, padx=5)

        self.tableau = ttk.Treeview(self, columns=("id", "numero_bon", "statut"), show="headings", height=16)
        for colonne, libelle, largeur in (
            ("id", "ID", 80), ("numero_bon", "Numéro du bon", 360), ("statut", "Statut", 180)
        ):
            self.tableau.heading(colonne, text=libelle)
            self.tableau.column(colonne, width=largeur, anchor="w")
        self.tableau.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.tableau.bind("<Double-1>", lambda _event: self.modifier())
        self.rafraichir()

    def rafraichir(self):
        self.tableau.delete(*self.tableau.get_children())
        for bon in lister_bons_travail():
            self.tableau.insert("", "end", iid=str(bon["id"]), values=(bon["id"], bon["numero_bon"], bon["statut"]))

    def bon_selectionne(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez un bon de travail.", parent=self)
            return None
        return int(selection[0]), self.tableau.item(selection[0], "values")

    def ajouter(self):
        FormulaireBonTravail(self, self.rafraichir)

    def modifier(self):
        bon = self.bon_selectionne()
        if bon is not None:
            identifiant, valeurs = bon
            FormulaireBonTravail(self, self.rafraichir, identifiant, valeurs[1], valeurs[2])

    def supprimer(self):
        bon = self.bon_selectionne()
        if bon and messagebox.askyesno("Confirmer", "Supprimer ce bon de travail ?", parent=self):
            supprimer_bon_travail(bon[0])
            self.rafraichir()

    def imprimer(self):
        bon = self.bon_selectionne()
        if bon is None:
            return
        _identifiant, valeurs = bon
        try:
            imprimer_fiche("Bon de travail", {
                "ID": valeurs[0], "Numéro du bon": valeurs[1], "Statut": valeurs[2],
            })
        except OSError as erreur:
            messagebox.showerror("Impression impossible", str(erreur), parent=self)


class FormulaireBonTravail(ctk.CTkToplevel):
    def __init__(self, parent, on_success, identifiant=None, numero_bon="", statut="À traiter"):
        super().__init__(parent)
        self.identifiant, self.on_success = identifiant, on_success
        self.title("Modifier le bon" if identifiant else "Ajouter un bon de travail")
        self.geometry("440x245")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        conteneur = ctk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(fill="both", expand=True, padx=30, pady=25)
        ctk.CTkLabel(conteneur, text="Numéro du bon").pack(anchor="w")
        self.numero_bon = ctk.CTkEntry(conteneur, width=370)
        self.numero_bon.insert(0, numero_bon)
        self.numero_bon.pack(pady=(2, 15))
        ctk.CTkLabel(conteneur, text="Statut").pack(anchor="w")
        self.statut = ctk.CTkComboBox(conteneur, values=["À traiter", "En cours", "Terminé", "Annulé"])
        self.statut.set(statut)
        self.statut.pack(pady=(2, 18))
        ctk.CTkButton(conteneur, text="Enregistrer", command=self.enregistrer).pack()

    def enregistrer(self):
        try:
            valeurs = (self.numero_bon.get(), self.statut.get())
            if self.identifiant is None:
                ajouter_bon_travail(*valeurs)
            else:
                modifier_bon_travail(self.identifiant, *valeurs)
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        self.on_success()
        self.destroy()
