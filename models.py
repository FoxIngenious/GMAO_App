from database import DatabaseConnection


def initialiser_base() -> None:
    """Crée le stockage local de l'application s'il n'existe pas encore."""
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        """
        CREATE TABLE IF NOT EXISTS materiels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            emplacement TEXT NOT NULL,
            etat TEXT NOT NULL
        )
        """
    )
    colonnes_demande = {
        ligne["name"]
        for ligne in connexion.execute("PRAGMA table_info(demandes_intervention)").fetchall()
    }
    colonnes_attendues = {"id", "description", "technicien", "materiel", "statut"}
    if colonnes_demande and colonnes_demande != colonnes_attendues:
        connexion.execute("ALTER TABLE demandes_intervention RENAME TO demandes_intervention_ancienne")
    connexion.execute(
        """
        CREATE TABLE IF NOT EXISTS demandes_intervention (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            technicien TEXT NOT NULL,
            materiel TEXT NOT NULL,
            statut TEXT NOT NULL
        )
        """
    )
    if colonnes_demande and colonnes_demande != colonnes_attendues:
        connexion.execute(
            """
            INSERT INTO demandes_intervention (id, description, technicien, materiel, statut)
            SELECT id, description, '', '', statut FROM demandes_intervention_ancienne
            """
        )
        connexion.execute("DROP TABLE demandes_intervention_ancienne")
    colonnes_bon = {
        ligne["name"] for ligne in connexion.execute("PRAGMA table_info(bons_travail)").fetchall()
    }
    colonnes_bon_attendues = {"id", "numero_bon", "statut"}
    if colonnes_bon and colonnes_bon != colonnes_bon_attendues:
        connexion.execute("ALTER TABLE bons_travail RENAME TO bons_travail_ancien")
    connexion.execute(
        """
        CREATE TABLE IF NOT EXISTS bons_travail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_bon TEXT NOT NULL,
            statut TEXT NOT NULL
        )
        """
    )
    if colonnes_bon and colonnes_bon != colonnes_bon_attendues:
        connexion.execute(
            """
            INSERT INTO bons_travail (id, numero_bon, statut)
            SELECT id, titre, statut FROM bons_travail_ancien
            """
        )
        connexion.execute("DROP TABLE bons_travail_ancien")
    connexion.commit()


def ajouter_bon_travail(numero_bon: str, statut: str) -> None:
    valeurs = (numero_bon.strip(), statut.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "INSERT INTO bons_travail (numero_bon, statut) VALUES (?, ?)", valeurs
    )
    connexion.commit()


def lister_bons_travail():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute(
        "SELECT id, numero_bon, statut FROM bons_travail ORDER BY id DESC"
    ).fetchall()


def modifier_bon_travail(identifiant: int, numero_bon: str, statut: str) -> None:
    valeurs = (numero_bon.strip(), statut.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "UPDATE bons_travail SET numero_bon = ?, statut = ? WHERE id = ?",
        (*valeurs, identifiant),
    )
    connexion.commit()


def supprimer_bon_travail(identifiant: int) -> None:
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM bons_travail WHERE id = ?", (identifiant,))
    connexion.commit()


def ajouter_demande(description: str, technicien: str, materiel: str, statut: str) -> None:
    valeurs = (description.strip(), technicien.strip(), materiel.strip(), statut.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        """
        INSERT INTO demandes_intervention (description, technicien, materiel, statut)
        VALUES (?, ?, ?, ?)
        """,
        valeurs,
    )
    connexion.commit()


def lister_demandes():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute(
        """
        SELECT id, description, technicien, materiel, statut
        FROM demandes_intervention ORDER BY id DESC
        """
    ).fetchall()


def modifier_demande(
    identifiant: int, description: str, technicien: str, materiel: str, statut: str
) -> None:
    valeurs = (description.strip(), technicien.strip(), materiel.strip(), statut.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        """
        UPDATE demandes_intervention
        SET description = ?, technicien = ?, materiel = ?, statut = ?
        WHERE id = ?
        """,
        (*valeurs, identifiant),
    )
    connexion.commit()


def supprimer_demande(identifiant: int) -> None:
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM demandes_intervention WHERE id = ?", (identifiant,))
    connexion.commit()




def ajouter_materiel(nom: str, categorie: str, emplacement: str, etat: str) -> None:
    valeurs = (nom.strip(), categorie.strip(), emplacement.strip(), etat.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")

    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        "INSERT INTO materiels (nom, categorie, emplacement, etat) VALUES (?, ?, ?, ?)",
        valeurs,
    )
    connexion.commit()


def lister_materiels():
    connexion = DatabaseConnection().get_connection()
    return connexion.execute(
        "SELECT id, nom, categorie, emplacement, etat FROM materiels ORDER BY id DESC"
    ).fetchall()


def modifier_materiel(
    identifiant: int, nom: str, categorie: str, emplacement: str, etat: str
) -> None:
    valeurs = (nom.strip(), categorie.strip(), emplacement.strip(), etat.strip())
    if not all(valeurs):
        raise ValueError("Tous les champs sont obligatoires.")
    connexion = DatabaseConnection().get_connection()
    connexion.execute(
        """
        UPDATE materiels SET nom = ?, categorie = ?, emplacement = ?, etat = ?
        WHERE id = ?
        """,
        (*valeurs, identifiant),
    )
    connexion.commit()


def supprimer_materiel(identifiant: int) -> None:
    connexion = DatabaseConnection().get_connection()
    connexion.execute("DELETE FROM materiels WHERE id = ?", (identifiant,))
    connexion.commit()
