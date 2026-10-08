from datetime import date

import calendar
from datetime import timedelta

from database import DatabaseConnection
from security import hash_mot_de_passe

ETATS_MATERIEL = ("Disponible", "En marche", "En panne", "En maintenance", "Réservé")
PRIORITES = ("Basse", "Normale", "Haute", "Urgente", "Critique")
STATUTS_DI = ("Nouvelle", "En attente", "Prise en charge", "Clôturée", "Annulée")
STATUTS_BT = ("À faire", "En cours", "Terminé", "Clôturé", "Annulé")
STATUTS_PREVENTIF = ("Planifiée", "À faire", "BT généré")
PERIODICITES = ("Hebdomadaire", "Mensuelle", "Trimestrielle", "Annuelle")
ROLES = ("Responsable Maintenance", "Technicien", "Opérateur")

TABLES = {
    "materiels": (
        "id, code, nom, categorie, emplacement, service, etat",
        """
        CREATE TABLE IF NOT EXISTS materiels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            nom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            emplacement TEXT NOT NULL,
            service TEXT NOT NULL DEFAULT '',
            etat TEXT NOT NULL
        )
        """,
    ),
    "demandes_intervention": (
        "id, numero, equipement, description, demandeur, date_creation, priorite, statut",
        """
        CREATE TABLE IF NOT EXISTS demandes_intervention (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            equipement TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL,
            demandeur TEXT NOT NULL,
            date_creation TEXT NOT NULL,
            priorite TEXT NOT NULL DEFAULT 'Normale',
            statut TEXT NOT NULL DEFAULT 'Nouvelle'
        )
        """,
    ),
    "techniciens": (
        "id, nom, specialite, telephone",
        """
        CREATE TABLE IF NOT EXISTS techniciens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            specialite TEXT NOT NULL DEFAULT '',
            telephone TEXT NOT NULL DEFAULT ''
        )
        """,
    ),
    "bons_travail": (
        "id, numero, di, equipement, technicien, statut, travaux, date_debut, date_fin, duree, cause, taches_realisees",
        """
        CREATE TABLE IF NOT EXISTS bons_travail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            di TEXT NOT NULL DEFAULT '',
            equipement TEXT NOT NULL DEFAULT '',
            technicien TEXT NOT NULL DEFAULT '',
            statut TEXT NOT NULL DEFAULT 'À faire',
            travaux TEXT NOT NULL DEFAULT '',
            date_debut TEXT NOT NULL DEFAULT '',
            date_fin TEXT NOT NULL DEFAULT '',
            duree TEXT NOT NULL DEFAULT '',
            cause TEXT NOT NULL DEFAULT '',
            taches_realisees TEXT NOT NULL DEFAULT ''
        )
        """,
    ),
    "utilisateurs": (
        "id, nom, email, mot_de_passe, role",
        """
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mot_de_passe TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """,
    ),
    "maintenance_preventive": (
        "id, titre, equipement, periodicite, prochaine_echeance, statut",
        """
        CREATE TABLE IF NOT EXISTS maintenance_preventive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            equipement TEXT NOT NULL,
            periodicite TEXT NOT NULL,
            prochaine_echeance TEXT NOT NULL,
            statut TEXT NOT NULL DEFAULT 'Planifiée'
        )
        """,
    ),
}


def _colonnes(connexion, table):
    return {ligne["name"] for ligne in connexion.execute(f"PRAGMA table_info({table})")}


def _prochain_numero(connexion, table, colonne, prefixe):
    nombre = connexion.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] + 1
    return f"{prefixe}-{nombre:03d}"


def initialiser_base():
    """Crée les tables de l'application, et les recrée si leur structure a changé."""
    connexion = DatabaseConnection().get_connection()
    for table, (colonnes, creation) in TABLES.items():
        if _colonnes(connexion, table) != set(colonnes.split(", ")):
            connexion.execute(f"DROP TABLE IF EXISTS {table}")
        connexion.execute(creation)
    connexion.commit()


#======================================= Matériels ==============================================
def _valider_etat(etat):
    if etat not in ETATS_MATERIEL:
        raise ValueError("État invalide. Choisissez parmi : " + ", ".join(ETATS_MATERIEL) + ".")


def ajouter_materiel(code, nom, categorie, emplacement, service, etat):
    valeurs = (code.strip(), nom.strip(), categorie.strip(), emplacement.strip(), etat.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    _valider_etat(etat.strip())
    connexion = DatabaseConnection().get_connection()
    if connexion.execute("SELECT 1 FROM materiels WHERE code = ?", (code.strip(),)).fetchone():
        raise ValueError(f"Le code matériel '{code.strip()}' existe déjà.")
    connexion.execute(
        "INSERT INTO materiels (code, nom, categorie, emplacement, service, etat) VALUES (?, ?, ?, ?, ?, ?)",
        (code.strip(), nom.strip(), categorie.strip(), emplacement.strip(), service, etat.strip()),
    )
    connexion.commit()


def lister_materiels():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM materiels ORDER BY id DESC").fetchall()


def materiel_par_id(identifiant):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM materiels WHERE id = ?", (identifiant,)).fetchone()


def materiel_par_code(code):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM materiels WHERE code = ?", (code.strip(),)).fetchone()


def modifier_materiel(identifiant, code, nom, categorie, emplacement, service, etat):
    valeurs = (code.strip(), nom.strip(), categorie.strip(), emplacement.strip(), etat.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    _valider_etat(etat.strip())
    connexion = DatabaseConnection().get_connection()
    doublon = connexion.execute(
        "SELECT id FROM materiels WHERE code = ? AND id != ?", (code.strip(), identifiant)
    ).fetchone()
    if doublon:
        raise ValueError(f"Le code matériel '{code.strip()}' existe déjà.")
    connexion.execute(
        "UPDATE materiels SET code = ?, nom = ?, categorie = ?, emplacement = ?, service = ?, etat = ? WHERE id = ?",
        (code.strip(), nom.strip(), categorie.strip(), emplacement.strip(), service, etat.strip(), identifiant),
    )
    connexion.commit()


def supprimer_materiel(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM materiels WHERE id = ?", (identifiant,))
    connexion.execute("UPDATE materiels SET id = id - 1 WHERE id > ?", (identifiant,))
    connexion.execute("DELETE FROM sqlite_sequence WHERE name = 'materiels'")
    connexion.commit()


def changer_etat_materiel(identifiant, etat):
    _valider_etat(etat.strip())
    connexion = DatabaseConnection().get_connection()
    connexion.execute("UPDATE materiels SET etat = ? WHERE id = ?", (etat.strip(), identifiant))
    connexion.commit()


def remettre_materiel_en_marche(equipement):
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "UPDATE materiels SET etat = 'En marche' WHERE code = ? OR nom = ?", (equipement, equipement)
    )
    connexion.commit()


#======================================= Demandes d'intervention ==============================================
def _valider_priorite(priorite):
    if priorite not in PRIORITES:
        raise ValueError("Priorité invalide. Choisissez parmi : " + ", ".join(PRIORITES) + ".")


def _valider_statut_di(statut):
    if statut not in STATUTS_DI:
        raise ValueError("Statut invalide. Choisissez parmi : " + ", ".join(STATUTS_DI) + ".")


def ajouter_demande(equipement, description, demandeur, priorite, statut):
    valeurs = (equipement.strip(), description.strip(), demandeur.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    _valider_priorite(priorite)
    _valider_statut_di(statut)
    connexion = DatabaseConnection().get_connection()
    numero = _prochain_numero(connexion, "demandes_intervention", "numero", "DI")
    connexion.execute(
        """
        INSERT INTO demandes_intervention (numero, equipement, description, demandeur, date_creation, priorite, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (numero, *valeurs, date.today().isoformat(), priorite, statut),
    )
    connexion.commit()
    return numero


def lister_demandes():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM demandes_intervention ORDER BY id DESC").fetchall()


def demande_par_id(identifiant):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM demandes_intervention WHERE id = ?", (identifiant,)).fetchone()


def modifier_demande(identifiant, equipement, description, demandeur, priorite, statut):
    valeurs = (equipement.strip(), description.strip(), demandeur.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    _valider_priorite(priorite)
    _valider_statut_di(statut)
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        """
        UPDATE demandes_intervention
        SET equipement = ?, description = ?, demandeur = ?, priorite = ?, statut = ?
        WHERE id = ?
        """,
        (*valeurs, priorite, statut, identifiant),
    )
    connexion.commit()


def supprimer_demande(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM demandes_intervention WHERE id = ?", (identifiant,))
    connexion.commit()


def generer_bon_travail(di_id, technicien):
    demande = demande_par_id(di_id)
    if not demande:
        raise ValueError("Demande d'intervention introuvable.")
    if not technicien.strip():
        raise ValueError("Choisissez un technicien pour le bon de travail.")
    connexion = DatabaseConnection().get_connection()
    numero = _prochain_numero(connexion, "bons_travail", "numero", "BT")
    connexion.execute(
        """
        INSERT INTO bons_travail
            (numero, di, equipement, technicien, statut, travaux, date_debut, date_fin, duree, cause, taches_realisees)
        VALUES (?, ?, ?, ?, 'À faire', ?, ?, '', '', '', '')
        """,
        (numero, demande["numero"], demande["equipement"], technicien.strip(),
         demande["description"], date.today().isoformat()),
    )
    connexion.execute(
        "UPDATE demandes_intervention SET statut = 'Prise en charge' WHERE id = ?", (di_id,)
    )
    connexion.commit()
    return numero


#======================================= Techniciens ==============================================
def ajouter_technicien(nom, specialite, telephone):
    if not nom.strip():
        raise ValueError("Le nom du technicien est obligatoire.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "INSERT INTO techniciens (nom, specialite, telephone) VALUES (?, ?, ?)",
        (nom.strip(), specialite.strip(), telephone.strip()),
    )
    connexion.commit()


def lister_techniciens():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM techniciens ORDER BY nom").fetchall()


def technicien_par_id(identifiant):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM techniciens WHERE id = ?", (identifiant,)).fetchone()


def modifier_technicien(identifiant, nom, specialite, telephone):
    if not nom.strip():
        raise ValueError("Le nom du technicien est obligatoire.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "UPDATE techniciens SET nom = ?, specialite = ?, telephone = ? WHERE id = ?",
        (nom.strip(), specialite.strip(), telephone.strip(), identifiant),
    )
    connexion.commit()


def supprimer_technicien(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM techniciens WHERE id = ?", (identifiant,))
    connexion.commit()


#======================================= Bons de travail ==============================================
def _valider_statut_bt(statut):
    if statut not in STATUTS_BT:
        raise ValueError("Statut invalide. Choisissez parmi : " + ", ".join(STATUTS_BT) + ".")


def ajouter_bon_travail(numero, di, equipement, technicien, statut, travaux, date_debut, date_fin):
    if not travaux.strip():
        raise ValueError("Les travaux à effectuer sont obligatoires.")
    _valider_statut_bt(statut)
    connexion = DatabaseConnection().get_connection()
    if not numero.strip():
        numero = _prochain_numero(connexion, "bons_travail", "numero", "BT")
    connexion.execute(
        """
        INSERT INTO bons_travail
            (numero, di, equipement, technicien, statut, travaux, date_debut, date_fin, duree, cause, taches_realisees)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', '', '')
        """,
        (
            numero.strip(), di.strip(), equipement, technicien, statut, travaux.strip(),
            date_debut.strip(), date_fin.strip(),
        ),
    )
    connexion.commit()
    return numero.strip()


def lister_bons_travail():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM bons_travail ORDER BY id DESC").fetchall()


def bon_travail_par_id(identifiant):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM bons_travail WHERE id = ?", (identifiant,)).fetchone()


def modifier_bon_travail(identifiant, numero, di, equipement, technicien, statut, travaux, date_debut, date_fin):
    if not travaux.strip():
        raise ValueError("Les travaux à effectuer sont obligatoires.")
    _valider_statut_bt(statut)
    connexion = DatabaseConnection().get_connection()
    if not numero.strip():
        numero = f"BT-{date.today().year}-{identifiant:04d}"
    connexion.execute(
        """
        UPDATE bons_travail
        SET numero = ?, di = ?, equipement = ?, technicien = ?, statut = ?, travaux = ?,
            date_debut = ?, date_fin = ?
        WHERE id = ?
        """,
        (
            numero.strip(), di.strip(), equipement, technicien, statut, travaux.strip(),
            date_debut.strip(), date_fin.strip(), identifiant,
        ),
    )
    connexion.commit()
    if statut in ("Terminé", "Clôturé"):
        remettre_materiel_en_marche(equipement)


def cloturer_bon_travail(identifiant, duree, cause, taches_realisees):
    bon = bon_travail_par_id(identifiant)
    if not bon:
        raise ValueError("Bon de travail introuvable.")
    if not duree.strip() or not cause.strip() or not taches_realisees.strip():
        raise ValueError("Durée, cause et tâches réalisées sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        """
        UPDATE bons_travail
        SET duree = ?, cause = ?, taches_realisees = ?, statut = 'Clôturé', date_fin = ?
        WHERE id = ?
        """,
        (
            duree.strip(), cause.strip(), taches_realisees.strip(),
            date.today().isoformat(), identifiant,
        ),
    )
    connexion.commit()
    remettre_materiel_en_marche(bon["equipement"])


def supprimer_bon_travail(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM bons_travail WHERE id = ?", (identifiant,))
    connexion.commit()


#======================================= Utilisateurs ==============================================
def _valider_role(role):
    if role not in ROLES:
        raise ValueError("Rôle invalide. Choisissez parmi : " + ", ".join(ROLES) + ".")


def ajouter_utilisateur(nom, email, mot_de_passe, role):
    if not nom.strip() or not email.strip() or not mot_de_passe:
        raise ValueError("Tous les champs sont obligatoires.")
    _valider_role(role)
    connexion = DatabaseConnection().get_connection()
    if connexion.execute("SELECT 1 FROM utilisateurs WHERE email = ?", (email.strip().lower(),)).fetchone():
        raise ValueError(f"L'email '{email.strip()}' est déjà utilisé.")
    connexion.execute(
        "INSERT INTO utilisateurs (nom, email, mot_de_passe, role) VALUES (?, ?, ?, ?)",
        (nom.strip(), email.strip().lower(), hash_mot_de_passe(mot_de_passe), role),
    )
    connexion.commit()


def lister_utilisateurs():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM utilisateurs ORDER BY id").fetchall()


def utilisateur_par_email(email):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM utilisateurs WHERE email = ?", (email.strip().lower(),)).fetchone()


def modifier_utilisateur(identifiant, nom, email, role):
    if not nom.strip() or not email.strip():
        raise ValueError("Tous les champs sont obligatoires.")
    _valider_role(role)
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "UPDATE utilisateurs SET nom = ?, email = ?, role = ? WHERE id = ?",
        (nom.strip(), email.strip().lower(), role, identifiant),
    )
    connexion.commit()


def supprimer_utilisateur(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM utilisateurs WHERE id = ?", (identifiant,))
    connexion.commit()


#======================================= Maintenance préventive ==============================================
def _valider_periodicite(periodicite):
    if periodicite not in PERIODICITES:
        raise ValueError("Périodicité invalide. Choisissez parmi : " + ", ".join(PERIODICITES) + ".")


def ajouter_maintenance_preventive(titre, equipement, periodicite, prochaine_echeance):
    if not titre.strip() or not equipement.strip():
        raise ValueError("Le titre et l'équipement sont obligatoires.")
    _valider_periodicite(periodicite)
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "INSERT INTO maintenance_preventive (titre, equipement, periodicite, prochaine_echeance, statut) "
        "VALUES (?, ?, ?, ?, 'Planifiée')",
        (titre.strip(), equipement.strip(), periodicite, prochaine_echeance.strip()),
    )
    connexion.commit()


def lister_maintenances_preventives():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute(
        "SELECT * FROM maintenance_preventive ORDER BY prochaine_echeance, id"
    ).fetchall()


def maintenance_preventive_par_id(identifiant):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM maintenance_preventive WHERE id = ?", (identifiant,)).fetchone()


def modifier_maintenance_preventive(identifiant, titre, equipement, periodicite, prochaine_echeance):
    if not titre.strip() or not equipement.strip():
        raise ValueError("Le titre et l'équipement sont obligatoires.")
    _valider_periodicite(periodicite)
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "UPDATE maintenance_preventive SET titre = ?, equipement = ?, periodicite = ?, prochaine_echeance = ? WHERE id = ?",
        (titre.strip(), equipement.strip(), periodicite, prochaine_echeance.strip(), identifiant),
    )
    connexion.commit()


def supprimer_maintenance_preventive(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM maintenance_preventive WHERE id = ?", (identifiant,))
    connexion.commit()


def _ajouter_mois(d, mois):
    total = d.month - 1 + mois
    annee = d.year + total // 12
    mois_resultat = total % 12 + 1
    dernier_jour = calendar.monthrange(annee, mois_resultat)[1]
    return d.replace(year=annee, month=mois_resultat, day=min(d.day, dernier_jour))


def _avancer_echeance(echeance, periodicite):
    d = date.fromisoformat(echeance) if isinstance(echeance, str) else echeance
    if periodicite == "Hebdomadaire":
        return d + timedelta(days=7)
    if periodicite == "Trimestrielle":
        return _ajouter_mois(d, 3)
    if periodicite == "Annuelle":
        return d.replace(year=d.year + 1)
    return _ajouter_mois(d, 1)


def verifier_echeances():
    """Génère un bon de travail pour chaque préventif dont l'échéance est atteinte."""
    connexion = DatabaseConnection().get_connection()
    aujourd_hui = date.today().isoformat()
    generes = 0
    for prev in connexion.execute(
        "SELECT * FROM maintenance_preventive WHERE statut != 'BT généré' AND prochaine_echeance <= ?",
        (aujourd_hui,),
    ).fetchall():
        numero = _prochain_numero(connexion, "bons_travail", "numero", "BT")
        connexion.execute(
            """
            INSERT INTO bons_travail
                (numero, di, equipement, technicien, statut, travaux, date_debut, date_fin, duree, cause, taches_realisees)
            VALUES (?, 'Préventif', ?, '', 'À faire', ?, ?, '', '', '', '')
            """,
            (numero, prev["equipement"], prev["titre"], aujourd_hui),
        )
        prochaine = _avancer_echeance(prev["prochaine_echeance"], prev["periodicite"])
        connexion.execute(
            "UPDATE maintenance_preventive SET statut = 'BT généré', prochaine_echeance = ? WHERE id = ?",
            (prochaine.isoformat(), prev["id"]),
        )
        generes += 1
    connexion.commit()
    return generes