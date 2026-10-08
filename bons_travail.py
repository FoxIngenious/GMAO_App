import customtkinter as ctk
from tkinter import messagebox, ttk

from impression import imprimer_fiche
from api_client import (
    ajouter_bon_travail,
    cloturer_bon_travail,
    lister_bons_travail,
    lister_demandes,
    lister_materiels,
    lister_techniciens,
    modifier_bon_travail,
    supprimer_bon_travail,
)
from models import STATUTS_BT


class GestionBonsTravail(ctk.CTkFrame):
    def __init__(self, parent, utilisateur=None):
        super().__init__(parent)
        self.utilisateur = utilisateur or {}
        self.role_technicien = self.utilisateur.get("role") == "Technicien"
        ctk.CTkLabel(self, text="Bons de travail", font=("Arial", 36)).pack(pady=(20, 10))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=(0, 12))
        ctk.CTkButton(actions, text="+ Ajouter", command=self.ajouter).grid(row=0, column=0, padx=5)
        ctk.CTkButton(actions, text="Modifier", command=self.modifier).grid(row=0, column=1, padx=5)
        ctk.CTkButton(actions, text="Rapport / Clôturer", fg_color="#0984e3", command=self.rapport).grid(row=0, column=2, padx=5)
        ctk.CTkButton(actions, text="Supprimer", fg_color="#b33939", command=self.supprimer).grid(row=0, column=3, padx=5)
        ctk.CTkButton(actions, text="Imprimer", command=self.imprimer).grid(row=0, column=4, padx=5)

        self.tableau = ttk.Treeview(
            self, columns=("id", "numero", "di", "equipement", "technicien", "statut"),
            show="headings", height=16,
        )
        for colonne, libelle in {
            "id": "ID", "numero": "N° BT", "di": "DI", "equipement": "Équipement",
            "technicien": "Technicien", "statut": "Statut",
        }.items():
            self.tableau.heading(colonne, text=libelle)
            self.tableau.column(colonne, width=150, anchor="w")
        self.tableau.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.tableau.bind("<Double-1>", lambda _event: self.modifier())
        self.rafraichir()

    def rafraichir(self):
        self.tableau.delete(*self.tableau.get_children())
        bons = lister_bons_travail()
        if self.role_technicien:
            bons = [b for b in bons if b["technicien"] == self.utilisateur.get("nom")]
        for bon in bons:
            self.tableau.insert(
                "", "end", iid=str(bon["id"]),
                values=(
                    bon["id"], bon["numero"], bon["di"], bon["equipement"], bon["technicien"],
                    bon["statut"],
                ),
            )

    def bon_selectionne(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez un bon de travail.", parent=self)
            return None
        identifiant = int(selection[0])
        return next(item for item in lister_bons_travail() if item["id"] == identifiant)

    def ajouter(self):
        FormulaireBonTravail(self, self.rafraichir)

    def modifier(self):
        bon = self.bon_selectionne()
        if bon:
            FormulaireBonTravail(self, self.rafraichir, bon)

    def rapport(self):
        bon = self.bon_selectionne()
        if bon:
            DialogRapport(self, self.rafraichir, bon)

    def supprimer(self):
        bon = self.bon_selectionne()
        if bon and messagebox.askyesno("Confirmer", "Supprimer ce bon de travail ?", parent=self):
            supprimer_bon_travail(bon["id"])
            self.rafraichir()

    def imprimer(self):
        bon = self.bon_selectionne()
        if bon:
            donnees = {
                "N° BT": bon["numero"], "DI": bon["di"], "Équipement": bon["equipement"],
                "Technicien": bon["technicien"], "Statut": bon["statut"],
                "Début": bon["date_debut"], "Fin": bon["date_fin"],
                "Travaux": bon["travaux"],
            }
            if bon.get("duree") or bon.get("cause") or bon.get("taches_realisees"):
                donnees.update({
                    "Durée (h)": bon["duree"], "Cause": bon["cause"],
                    "Tâches réalisées": bon["taches_realisees"],
                })
            imprimer_fiche("Bon de travail", donnees)


class DialogRapport(ctk.CTkToplevel):
    def __init__(self, parent, on_success, bon):
        super().__init__(parent)
        self.bon = bon
        self.on_success = on_success
        self.title("Rapport d'intervention")
        self.geometry("520x520")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        conteneur = ctk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(expand=True, padx=25)

        ctk.CTkLabel(
            conteneur, text=f"{bon['numero']} — {bon['equipement']}",
            font=("Arial", 18),
        ).pack(pady=(0, 16))

        ctk.CTkLabel(conteneur, text="Temps passé (heures)").pack(anchor="w")
        self.duree = ctk.CTkEntry(conteneur, width=420)
        self.duree.pack(pady=(2, 10))

        ctk.CTkLabel(conteneur, text="Cause de la panne").pack(anchor="w")
        self.cause = ctk.CTkEntry(conteneur, width=420)
        self.cause.pack(pady=(2, 10))

        ctk.CTkLabel(conteneur, text="Tâches réalisées").pack(anchor="w")
        self.taches = ctk.CTkTextbox(conteneur, height=140, width=420)
        self.taches.pack(pady=(2, 16))

        boutons = ctk.CTkFrame(conteneur, fg_color="transparent")
        boutons.pack()
        ctk.CTkButton(boutons, text="Clôturer", width=180, command=self.cloturer).pack(side="left", padx=5)
        ctk.CTkButton(boutons, text="Annuler", width=180, command=self.destroy).pack(side="left", padx=5)

    def cloturer(self):
        try:
            cloturer_bon_travail(
                self.bon["id"], self.duree.get(),
                self.cause.get(), self.taches.get("1.0", "end-1c"),
            )
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        messagebox.showinfo(
            "Bon clôturé",
            f"{self.bon['numero']} est clôturé. Le matériel {self.bon['equipement']} "
            "a été remis en marche automatiquement.",
            parent=self,
        )
        self.on_success()
        self.destroy()


class FormulaireBonTravail(ctk.CTkToplevel):
    def __init__(self, parent, on_success, bon=None):
        super().__init__(parent)
        self.bon = bon
        self.on_success = on_success
        self.title("Modifier le bon" if bon else "Ajouter un bon de travail")
        self.geometry("500x580")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        conteneur = ctk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(expand=True)
        conteneur.columnconfigure(0, weight=1)
        conteneur.columnconfigure(1, weight=1)

        self.numero = self._champ(conteneur, "Numéro du bon", bon["numero"] if bon else "", 0, 0)
        self.di = self._choix(
            conteneur, "DI concernée", [demande["numero"] for demande in lister_demandes()],
            bon["di"] if bon else "", 0, 1,
        )
        self.equipement = self._choix(
            conteneur, "Équipement",
            [f"{m['code']} — {m['nom']}" for m in lister_materiels()],
            bon["equipement"] if bon else "", 1, 0,
        )
        self.technicien = self._choix(
            conteneur, "Technicien", [technicien["nom"] for technicien in lister_techniciens()],
            bon["technicien"] if bon else "", 1, 1,
        )
        self.statut = self._choix(
            conteneur, "Statut", list(STATUTS_BT), bon["statut"] if bon else "À faire", 2, 0
        )
        self.date_debut = self._champ(conteneur, "Date de début", bon["date_debut"] if bon else "", 2, 1)
        self.date_fin = self._champ(conteneur, "Date de fin", bon["date_fin"] if bon else "", 3, 0, 2)

        ctk.CTkLabel(conteneur, text="Travaux à effectuer").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )
        self.travaux = ctk.CTkTextbox(conteneur, height=80)
        if bon:
            self.travaux.insert("1.0", bon["travaux"])
        self.travaux.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 2))

        ctk.CTkButton(conteneur, text="Valider", width=185, command=self.enregistrer).grid(
            row=10, column=0, pady=18
        )
        ctk.CTkButton(conteneur, text="Annuler", width=185, command=self.destroy).grid(
            row=10, column=1, pady=18
        )

    def _champ(self, parent, libelle, valeur, ligne, colonne, etendue=1):
        ctk.CTkLabel(parent, text=libelle).grid(
            row=ligne * 2, column=colonne, columnspan=etendue, sticky="w", pady=(6, 0)
        )
        entree = ctk.CTkEntry(parent, height=28)
        entree.insert(0, valeur or "")
        entree.grid(row=ligne * 2 + 1, column=colonne, columnspan=etendue, sticky="ew", pady=(0, 2))
        return entree

    def _choix(self, parent, libelle, valeurs, valeur, ligne, colonne):
        ctk.CTkLabel(parent, text=libelle).grid(
            row=ligne * 2, column=colonne, sticky="w", pady=(6, 0)
        )
        combo = ctk.CTkComboBox(parent, values=valeurs or ["-"])
        if valeur in valeurs:
            combo.set(valeur)
        combo.grid(row=ligne * 2 + 1, column=colonne, sticky="ew", pady=(0, 2))
        return combo

    def enregistrer(self):
        try:
            equipement = self.equipement.get().split(" — ")[0].strip()
            valeurs = (
                self.numero.get(), self.di.get(), equipement, self.technicien.get(),
                self.statut.get(), self.travaux.get("1.0", "end-1c"),
                self.date_debut.get(), self.date_fin.get(),
            )
            if self.bon:
                modifier_bon_travail(self.bon["id"], *valeurs)
            else:
                ajouter_bon_travail(*valeurs)
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        self.on_success()
        self.destroy()

