from datetime import date, timedelta

import models

UTILISATEURS = [
    {"nom": "Jean Dupont", "email": "admin.maintenance@usine.com", "mot_de_passe": "Admin2026!", "role": "Responsable Maintenance"},
    {"nom": "Pierre Martin", "email": "tech.pierre@usine.com", "mot_de_passe": "Tech2026!", "role": "Technicien"},
    {"nom": "Lucas Bernard", "email": "op.lucas@usine.com", "mot_de_passe": "Op2026!", "role": "Opérateur"},
]

MATERIELS = [
    {"code": "ROB-01", "nom": "Robot de soudage KUKA", "categorie": "Robotique", "emplacement": "Ligne d'Assemblage A", "service": "Production", "etat": "En marche"},
    {"code": "PRE-02", "nom": "Presse Hydraulique 50T", "categorie": "Machine-outil", "emplacement": "Atelier Forge", "service": "Production", "etat": "En marche"},
    {"code": "COM-01", "nom": "Compresseur d'air ATLAS", "categorie": "Infrastructure", "emplacement": "Local Technique", "service": "Services Généraux", "etat": "En marche"},
]

TECHNICIENS = [
    {"nom": "Pierre Martin", "specialite": "Hydraulique", "telephone": "06 12 34 56 78"},
    {"nom": "Sophie Lambert", "specialite": "Robotique", "telephone": "06 98 76 54 32"},
]

PREVENTIFS = [
    {
        "titre": "Remplacement des filtres à air",
        "equipement": "COM-01",
        "periodicite": "Mensuelle",
        "prochaine_echeance": date.today().isoformat(),
    },
]


def _creer_utilisateur():
    for donnees in UTILISATEURS:
        if models.utilisateur_par_email(donnees["email"]):
            print(f"Utilisateur {donnees['email']} : déjà présent, ignoré.")
            continue
        models.ajouter_utilisateur(
            donnees["nom"], donnees["email"], donnees["mot_de_passe"], donnees["role"]
        )
        print(f"Utilisateur {donnees['email']} ({donnees['role']}) créé.")


def _creer_materiels():
    for donnees in MATERIELS:
        if models.materiel_par_code(donnees["code"]):
            print(f"Matériel {donnees['code']} : déjà présent, ignoré.")
            continue
        models.ajouter_materiel(
            donnees["code"], donnees["nom"], donnees["categorie"],
            donnees["emplacement"], donnees["service"], donnees["etat"],
        )
        print(f"Matériel {donnees['code']} — {donnees['nom']} créé.")


def _creer_techniciens():
    for donnees in TECHNICIENS:
        if any(t["nom"] == donnees["nom"] for t in models.lister_techniciens()):
            print(f"Technicien {donnees['nom']} : déjà présent, ignoré.")
            continue
        models.ajouter_technicien(donnees["nom"], donnees["specialite"], donnees["telephone"])
        print(f"Technicien {donnees['nom']} créé.")


def _creer_preventifs():
    for donnees in PREVENTIFS:
        existants = [
            p for p in models.lister_maintenances_preventives()
            if p["titre"] == donnees["titre"] and p["equipement"] == donnees["equipement"]
        ]
        if existants:
            print(f"Préventif '{donnees['titre']}' (COM-01) : déjà présent, ignoré.")
            continue
        models.ajouter_maintenance_preventive(
            donnees["titre"], donnees["equipement"],
            donnees["periodicite"], donnees["prochaine_echeance"],
        )
        print(f"Préventif '{donnees['titre']}' (COM-01) créé.")


def seeder():
    models.initialiser_base()
    print("== Utilisateurs ==")
    _creer_utilisateur()
    print("== Matériels ==")
    _creer_materiels()
    print("== Techniciens ==")
    _creer_techniciens()
    print("== Maintenance préventive ==")
    _creer_preventifs()
    print("Seed terminé.")


if __name__ == "__main__":
    seeder()