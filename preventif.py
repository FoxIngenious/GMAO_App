from datetime import date

import customtkinter as ctk
from tkinter import messagebox, ttk

from api_client import (
    ajouter_maintenance_preventive,
    lister_maintenances_preventives,
    lister_materiels,
    modifier_maintenance_preventive,
    supprimer_maintenance_preventive,
    verifier_echeances,
)
from models import PERIODICITES


class GestionMaintenancePreventive(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Maintenance préventive", font=("Arial", 36)).pack(pady=(20, 10))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=(0, 12))
        ctk.CTkButton(actions, text="+ Planifier", command=self.ajouter).grid(row=0, column=0, padx=5)
        ctk.CTkButton(actions, text="Modifier", command=self.modifier).grid(row=0, column=1, padx=5)
        ctk.CTkButton(actions, text="Vérifier les échéances", fg_color="#0984e3", command=self.verifier).grid(row=0, column=2, padx=5)
        ctk.CTkButton(actions, text="Supprimer", fg_color="#b33939", command=self.supprimer).grid(row=0, column=3, padx=5)

        self.tableau = ttk.Treeview(
            self, columns=("id", "titre", "equipement", "periodicite", "echeance", "statut"),
            show="headings", height=16,
        )
        for colonne, libelle in {
            "id": "ID", "titre": "Titre", "equipement": "Équipement",
            "periodicite": "Périodicité", "echeance": "Prochaine échéance", "statut": "Statut",
        }.items():
            self.tableau.heading(colonne, text=libelle)
            self.tableau.column(colonne, width=190, anchor="center")
        self.tableau.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.tableau.bind("<Double-1>", lambda _event: self.modifier())
        self.rafraichir()

    def rafraichir(self):
        self.tableau.delete(*self.tableau.get_children())
        for prev in lister_maintenances_preventives():
            self.tableau.insert(
                "", "end", iid=str(prev["id"]),
                values=(
                    prev["id"], prev["titre"], prev["equipement"],
                    prev["periodicite"], prev["prochaine_echeance"], prev["statut"],
                ),
            )

    def prev_selectionne(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Sélectionnez une maintenance préventive.", parent=self)
            return None
        identifiant = int(selection[0])
        return next(item for item in lister_maintenances_preventives() if item["id"] == identifiant)

    def ajouter(self):
        FormulairePreventif(self, self.rafraichir)

    def modifier(self):
        prev = self.prev_selectionne()
        if prev:
            FormulairePreventif(self, self.rafraichir, prev)

    def supprimer(self):
        prev = self.prev_selectionne()
        if prev and messagebox.askyesno("Confirmer", "Supprimer cette planification ?", parent=self):
            supprimer_maintenance_preventive(prev["id"])
            self.rafraichir()

    def verifier(self):
        try:
            resultat = verifier_echeances()
        except ValueError as erreur:
            messagebox.showwarning("Erreur", str(erreur), parent=self)
            return
        if resultat["bons_generes"]:
            messagebox.showinfo(
                "Échéances",
                f"{resultat['bons_generes']} bon(s) de travail généré(s) automatiquement.",
                parent=self,
            )
        else:
            messagebox.showinfo("Échéances", "Aucune échéance à générer pour le moment.", parent=self)
        self.rafraichir()


class FormulairePreventif(ctk.CTkToplevel):
    def __init__(self, parent, on_success, prev=None):
        super().__init__(parent)
        self.prev = prev
        self.on_success = on_success
        self.title("Modifier la planification" if prev else "Planifier une maintenance")
        self.geometry("480x440")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        conteneur = ctk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(conteneur, text="Titre").pack(anchor="w")
        self.titre = ctk.CTkEntry(conteneur, width=420)
        self.titre.insert(0, prev["titre"] if prev else "")
        self.titre.pack(pady=(2, 10))

        ctk.CTkLabel(conteneur, text="Équipement").pack(anchor="w")
        materiels = lister_materiels()
        equipements = [f"{m['code']} — {m['nom']}" for m in materiels]
        self.equipement = ctk.CTkComboBox(conteneur, values=equipements or ["Aucun matériel"])
        if prev:
            self.equipement.set(prev["equipement"])
        elif equipements:
            self.equipement.set(equipements[0])
        self.equipement.pack(pady=(2, 10))

        ctk.CTkLabel(conteneur, text="Périodicité").pack(anchor="w")
        self.periodicite = ctk.CTkComboBox(conteneur, values=list(PERIODICITES))
        self.periodicite.set(prev["periodicite"] if prev else "Mensuelle")
        self.periodicite.pack(pady=(2, 10))

        ctk.CTkLabel(conteneur, text="Prochaine échéance (AAAA-MM-JJ)").pack(anchor="w")
        self.echeance = ctk.CTkEntry(conteneur, width=420)
        self.echeance.insert(0, prev["prochaine_echeance"] if prev else date.today().isoformat())
        self.echeance.pack(pady=(2, 18))

        boutons = ctk.CTkFrame(conteneur, fg_color="transparent")
        boutons.pack()
        ctk.CTkButton(boutons, text="Valider", width=180, command=self.enregistrer).pack(side="left", padx=5)
        ctk.CTkButton(boutons, text="Annuler", width=180, command=self.destroy).pack(side="left", padx=5)

    def enregistrer(self):
        equipement = self.equipement.get().split(" — ")[0].strip()
        try:
            if self.prev:
                modifier_maintenance_preventive(
                    self.prev["id"], self.titre.get(), equipement,
                    self.periodicite.get(), self.echeance.get().strip(),
                )
            else:
                ajouter_maintenance_preventive(
                    self.titre.get(), equipement,
                    self.periodicite.get(), self.echeance.get().strip(),
                )
        except ValueError as erreur:
            messagebox.showwarning("Champs incomplets", str(erreur), parent=self)
            return
        self.on_success()
        self.destroy()