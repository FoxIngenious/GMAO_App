from datetime import date, datetime

from database import DatabaseConnection

ETATS_MATERIEL = ("Disponible", "En panne", "En maintenance", "Réservé")
PRIORITES = ("Basse", "Normale", "Haute", "Urgente")
STATUTS_DI = ("Nouvelle", "En attente", "Prise en charge", "Clôturée", "Annulée")
STATUTS_BT = ("À faire", "En cours", "Terminé", "Annulé")

TABLES = {
    "materiels": (
        "id, nom, categorie, emplacement, service, etat",
        """
        CREATE TABLE IF NOT EXISTS materiels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        "id, numero, di, equipement, technicien, statut, travaux, date_debut, date_fin, "
        "diagnostic, travail_realise, pieces, observations, resultat, date_cloture",
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
            diagnostic TEXT NOT NULL DEFAULT '',
            travail_realise TEXT NOT NULL DEFAULT '',
            pieces TEXT NOT NULL DEFAULT '',
            observations TEXT NOT NULL DEFAULT '',
            resultat TEXT NOT NULL DEFAULT '',
            date_cloture TEXT NOT NULL DEFAULT ''
        )
        """,
    ),
}


def _colonnes(connexion, table):
    return {ligne["name"] for ligne in connexion.execute(f"PRAGMA table_info({table})")}


def _prochain_numero(connexion, table, colonne, prefixe):
    nombre = connexion.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] + 1
    return f"{prefixe}-{date.today().year}-{nombre:04d}"


def initialiser_base():
    """Crée les tables de l'application, et les recrée si leur structure a changé."""
    connexion = DatabaseConnection().get_connection()
    for table, (colonnes, creation) in TABLES.items():
        if _colonnes(connexion, table) != set(colonnes.split(", ")):
            connexion.execute(f"DROP TABLE IF EXISTS {table}")
        connexion.execute(creation)
    connexion.commit()


#======================================= Matériels ==============================================
def ajouter_materiel(nom, categorie, emplacement, service, etat):
    valeurs = (nom.strip(), categorie.strip(), emplacement.strip(), etat.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "INSERT INTO materiels (nom, categorie, emplacement, service, etat) VALUES (?, ?, ?, ?, ?)",
        (*valeurs, service),
    )
    connexion.commit()


def lister_materiels():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM materiels ORDER BY id DESC").fetchall()


def materiel_par_id(identifiant):
    connexion = DatabaseConnection().get_connection()
    return connexion.execute("SELECT * FROM materiels WHERE id = ?", (identifiant,)).fetchone()


def modifier_materiel(identifiant, nom, categorie, emplacement, service, etat):
    valeurs = (nom.strip(), categorie.strip(), emplacement.strip(), etat.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "UPDATE materiels SET nom = ?, categorie = ?, emplacement = ?, service = ?, etat = ? WHERE id = ?",
        (*valeurs, service, identifiant),
    )
    connexion.commit()


def supprimer_materiel(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM materiels WHERE id = ?", (identifiant,))
    connexion.execute("UPDATE materiels SET id = id - 1 WHERE id > ?", (identifiant,))
    connexion.execute("DELETE FROM sqlite_sequence WHERE name = 'materiels'")
    connexion.commit()


#======================================= Demandes d'intervention ==============================================
def ajouter_demande(equipement, description, demandeur, priorite, statut):
    valeurs = (description.strip(), demandeur.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    numero = _prochain_numero(connexion, "demandes_intervention", "numero", "DI")
    connexion.execute(
        """
        INSERT INTO demandes_intervention (numero, equipement, description, demandeur, date_creation, priorite, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (numero, equipement, *valeurs, date.today().isoformat(), priorite, statut),
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
    valeurs = (description.strip(), demandeur.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        """
        UPDATE demandes_intervention
        SET equipement = ?, description = ?, demandeur = ?, priorite = ?, statut = ?
        WHERE id = ?
        """,
        (equipement, *valeurs, priorite, statut, identifiant),
    )
    connexion.commit()


def supprimer_demande(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM demandes_intervention WHERE id = ?", (identifiant,))
    connexion.commit()


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
def ajouter_bon_travail(numero, di, equipement, technicien, statut, travaux, date_debut, date_fin):
    if not travaux.strip():
        raise ValueError("Les travaux à effectuer sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    if not numero.strip():
        numero = _prochain_numero(connexion, "bons_travail", "numero", "BT")
    connexion.execute(
        """
        INSERT INTO bons_travail
            (numero, di, equipement, technicien, statut, travaux, date_debut, date_fin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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


def supprimer_bon_travail(identifiant):
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM bons_travail WHERE id = ?", (identifiant,))
    connexion.commit()


def cloturer_bon(identifiant, diagnostic, travail_realise, pieces, observations, resultat, date_debut, date_fin):
    if not all(valeur.strip() for valeur in (diagnostic, travail_realise, resultat)):
        raise ValueError("Le diagnostic, le travail réalisé et le résultat sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    if not date_fin.strip():
        date_fin = datetime.now().strftime("%d/%m/%Y %H:%M")
    connexion.execute(
        """
        UPDATE bons_travail
        SET diagnostic = ?, travail_realise = ?, pieces = ?, observations = ?, resultat = ?,
            date_debut = ?, date_fin = ?, date_cloture = ?, statut = 'Terminé'
        WHERE id = ?
        """,
        (
            diagnostic.strip(), travail_realise.strip(), pieces.strip(), observations.strip(),
            resultat.strip(), date_debut.strip(), date_fin, datetime.now().strftime("%d/%m/%Y %H:%M"),
            identifiant,
        ),
    )
    connexion.commit()
