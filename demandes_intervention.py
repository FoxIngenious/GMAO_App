from datetime import date

import customtkinter as ctk
from tkinter import messagebox, ttk

from impression import imprimer_fiche
from models import (
    PRIORITES,
    STATUTS_DI,
    ajouter_demande,
    lister_demandes,
    lister_materiels,
    modifier_demande,
    supprimer_demande,
)


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
            self, columns=("id", "numero", "equipement", "demandeur", "priorite", "statut", "date_creation"),
            show="headings", height=16,
        )
        for colonne, libelle in {
            "id": "ID", "numero": "N° DI", "equipement": "Équipement", "demandeur": "Demandeur",
            "priorite": "Priorité", "statut": "Statut", "date_creation": "Date",
        }.items():
            self.tableau.heading(colonne, text=libelle)
            self.tableau.column(colonne, width=160, anchor="w")
        self.tableau.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.tableau.bind("<Double-1>", lambda _event: self.modifier())
        self.rafraichir()

    def rafraichir(self):
        self.tableau.delete(*self.tableau.get_children())
        for demande in lister_demandes():
            self.tableau.insert(
                "", "end", iid=str(demande["id"]),
                values=(
                    demande["id"], demande["numero"], demande["equipement"], demande["demandeur"],
                    demande["priorite"], demande["statut"], demande["date_creation"],
                ),
            )

    def demande_selectionnee(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez une demande.", parent=self)
            return None
        identifiant = int(selection[0])
        return next(item for item in lister_demandes() if item["id"] == identifiant)

    def ajouter(self):
        FormulaireDemande(self, self.rafraichir)

    def modifier(self):
        demande = self.demande_selectionnee()
        if demande:
            FormulaireDemande(self, self.rafraichir, demande)

    def supprimer(self):
        demande = self.demande_selectionnee()
        if demande and messagebox.askyesno("Confirmer", "Supprimer cette demande ?", parent=self):
            supprimer_demande(demande["id"])
            self.rafraichir()

    def imprimer(self):
        demande = self.demande_selectionnee()
        if demande:
            imprimer_fiche("Demande d'intervention", {
                "N° DI": demande["numero"], "Équipement": demande["equipement"],
                "Demandeur": demande["demandeur"], "Date": demande["date_creation"],
                "Priorité": demande["priorite"], "Statut": demande["statut"],
                "Problème": demande["description"],
            })


class FormulaireDemande(ctk.CTkToplevel):
    def __init__(self, parent, on_success, demande=None):
        super().__init__(parent)
        self.demande = demande
        self.on_success = on_success
        self.title("Modifier la demande" if demande else "Ajouter une demande")
        self.geometry("500x620")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        conteneur = ctk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(fill="both", expand=True, padx=25, pady=20)
        conteneur.columnconfigure(0, weight=1)
        conteneur.columnconfigure(1, weight=1)

        ctk.CTkLabel(conteneur, text="N° de la DI").grid(row=0, column=0, sticky="w", pady=(8, 0))
        self.numero = ctk.CTkEntry(conteneur)
        self.numero.insert(0, demande["numero"] if demande else "Généré automatiquement")
        self.numero.configure(state="disabled")
        self.numero.grid(row=1, column=0, sticky="ew", pady=(2, 0), padx=(0, 8))

        ctk.CTkLabel(conteneur, text="Priorité").grid(row=0, column=1, sticky="w", pady=(8, 0))
        self.priorite = ctk.CTkComboBox(conteneur, values=list(PRIORITES))
        self.priorite.set(demande["priorite"] if demande else "Normale")
        self.priorite.grid(row=1, column=1, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(conteneur, text="Équipement").grid(row=2, column=0, sticky="w", pady=(8, 0))
        equipements = [materiel["nom"] for materiel in lister_materiels()]
        self.equipement = ctk.CTkComboBox(conteneur, values=equipements or ["Aucun matériel"])
        if demande:
            self.equipement.set(demande["equipement"])
        elif equipements:
            self.equipement.set(equipements[0])
        self.equipement.grid(row=3, column=0, sticky="ew", pady=(2, 0), padx=(0, 8))

        ctk.CTkLabel(conteneur, text="Demandeur").grid(row=2, column=1, sticky="w", pady=(8, 0))
        self.demandeur = ctk.CTkEntry(conteneur)
        if demande:
            self.demandeur.insert(0, demande["demandeur"])
        self.demandeur.grid(row=3, column=1, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(conteneur, text="Date de création (AAAA-MM-JJ)").grid(row=4, column=0, sticky="w", pady=(8, 0))
        self.date_creation = ctk.CTkEntry(conteneur)
        self.date_creation.insert(0, demande["date_creation"] if demande else date.today().isoformat())
        self.date_creation.grid(row=5, column=0, sticky="ew", pady=(2, 0), padx=(0, 8))

        ctk.CTkLabel(conteneur, text="Statut").grid(row=4, column=1, sticky="w", pady=(8, 0))
        self.statut = ctk.CTkComboBox(conteneur, values=list(STATUTS_DI))
        self.statut.set(demande["statut"] if demande else "Nouvelle")
        self.statut.grid(row=5, column=1, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(conteneur, text="Description du problème").grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.description = ctk.CTkTextbox(conteneur, height=150)
        if demande:
            self.description.insert("1.0", demande["description"])
        self.description.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(2, 14))

        boutons = ctk.CTkFrame(conteneur, fg_color="transparent")
        boutons.grid(row=8, column=0, columnspan=2)
        ctk.CTkButton(boutons, text="Valider", width=185, command=self.enregistrer).pack(side="left", padx=5)
        ctk.CTkButton(boutons, text="Annuler", width=185, command=self.destroy).pack(side="left", padx=5)

    def enregistrer(self):
        try:
            date.fromisoformat(self.date_creation.get().strip())
        except ValueError:
            messagebox.showwarning("Date invalide", "Écris la date au format AAAA-MM-JJ.", parent=self)
            return
        try:
            valeurs = (
                self.equipement.get(), self.description.get("1.0", "end-1c"),
                self.demandeur.get(), self.priorite.get(), self.statut.get(),
            )
            if self.demande:
                modifier_demande(self.demande["id"], *valeurs)
            else:
                ajouter_demande(*valeurs)
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        self.on_success()
        self.destroy()
