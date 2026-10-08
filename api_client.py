import os

import requests

BASE = os.getenv("GMAO_API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("GMAO_API_KEY", "gmao-dev-key")

_session = requests.Session()
_session.headers["X-API-Key"] = API_KEY


def est_joignable():
    try:
        return _session.get(BASE + "/health", timeout=1).status_code == 200
    except requests.RequestException:
        return False


def _requete(methode, chemin, **kwargs):
    try:
        reponse = _session.request(methode, BASE + chemin, timeout=10, **kwargs)
    except requests.ConnectionError:
        raise ConnectionError(
            f"Impossible de joindre l'API GMAO sur {BASE}. Vérifiez qu'elle est démarrée."
        )
    except requests.RequestException as erreur:
        raise ConnectionError(str(erreur))
    if reponse.status_code >= 400:
        detail = reponse.json().get("detail", "Erreur inconnue.") if reponse.content else "Erreur inconnue."
        raise ValueError(detail)
    return reponse.json() if reponse.status_code != 204 else None


#======================================= authentification ==============================================
def login(email, mot_de_passe):
    resultat = _requete("POST", "/auth/login", json={"email": email, "mot_de_passe": mot_de_passe})
    _session.headers["X-Auth-Token"] = resultat["token"]
    return resultat["utilisateur"]


def logout():
    _session.headers.pop("X-Auth-Token", None)


#======================================= matériels ==============================================
def lister_materiels():
    return _requete("GET", "/materiels")


def materiel_par_id(identifiant):
    return _requete("GET", f"/materiels/{identifiant}")


def ajouter_materiel(code, nom, categorie, emplacement, service, etat):
    _requete("POST", "/materiels", json={
        "code": code, "nom": nom, "categorie": categorie,
        "emplacement": emplacement, "service": service, "etat": etat,
    })


def modifier_materiel(identifiant, code, nom, categorie, emplacement, service, etat):
    _requete("PUT", f"/materiels/{identifiant}", json={
        "code": code, "nom": nom, "categorie": categorie,
        "emplacement": emplacement, "service": service, "etat": etat,
    })


def supprimer_materiel(identifiant):
    _requete("DELETE", f"/materiels/{identifiant}")


def changer_etat_materiel(identifiant, etat):
    _requete("POST", f"/materiels/{identifiant}/etat", json={"etat": etat})


#======================================= demandes d'intervention ==============================================
def lister_demandes():
    return _requete("GET", "/demandes-intervention")


def demande_par_id(identifiant):
    return _requete("GET", f"/demandes-intervention/{identifiant}")


def ajouter_demande(equipement, description, demandeur, priorite, statut):
    _requete("POST", "/demandes-intervention", json={
        "equipement": equipement, "description": description, "demandeur": demandeur,
        "priorite": priorite, "statut": statut,
    })


def modifier_demande(identifiant, equipement, description, demandeur, priorite, statut):
    _requete("PUT", f"/demandes-intervention/{identifiant}", json={
        "equipement": equipement, "description": description, "demandeur": demandeur,
        "priorite": priorite, "statut": statut,
    })


def supprimer_demande(identifiant):
    _requete("DELETE", f"/demandes-intervention/{identifiant}")


def generer_bon_travail(di_id, technicien):
    _requete("POST", f"/demandes-intervention/{di_id}/generer-bt", json={"technicien": technicien})


#======================================= techniciens ==============================================
def lister_techniciens():
    return _requete("GET", "/techniciens")


def technicien_par_id(identifiant):
    return _requete("GET", f"/techniciens/{identifiant}")


def ajouter_technicien(nom, specialite, telephone):
    _requete("POST", "/techniciens", json={
        "nom": nom, "specialite": specialite, "telephone": telephone,
    })


def modifier_technicien(identifiant, nom, specialite, telephone):
    _requete("PUT", f"/techniciens/{identifiant}", json={
        "nom": nom, "specialite": specialite, "telephone": telephone,
    })


def supprimer_technicien(identifiant):
    _requete("DELETE", f"/techniciens/{identifiant}")


#======================================= bons de travail ==============================================
def lister_bons_travail():
    return _requete("GET", "/bons-travail")


def bon_travail_par_id(identifiant):
    return _requete("GET", f"/bons-travail/{identifiant}")


def ajouter_bon_travail(numero, di, equipement, technicien, statut, travaux, date_debut, date_fin):
    _requete("POST", "/bons-travail", json={
        "numero": numero, "di": di, "equipement": equipement, "technicien": technicien,
        "statut": statut, "travaux": travaux, "date_debut": date_debut, "date_fin": date_fin,
    })


def modifier_bon_travail(identifiant, numero, di, equipement, technicien, statut, travaux, date_debut, date_fin):
    _requete("PUT", f"/bons-travail/{identifiant}", json={
        "numero": numero, "di": di, "equipement": equipement, "technicien": technicien,
        "statut": statut, "travaux": travaux, "date_debut": date_debut, "date_fin": date_fin,
    })


def supprimer_bon_travail(identifiant):
    _requete("DELETE", f"/bons-travail/{identifiant}")


def cloturer_bon_travail(identifiant, duree, cause, taches_realisees):
    _requete("POST", f"/bons-travail/{identifiant}/rapport", json={
        "duree": duree, "cause": cause, "taches_realisees": taches_realisees,
    })


#======================================= maintenance préventive ==============================================
def lister_maintenances_preventives():
    return _requete("GET", "/maintenance-preventive")


def maintenance_preventive_par_id(identifiant):
    return _requete("GET", f"/maintenance-preventive/{identifiant}")


def ajouter_maintenance_preventive(titre, equipement, periodicite, prochaine_echeance):
    _requete("POST", "/maintenance-preventive", json={
        "titre": titre, "equipement": equipement,
        "periodicite": periodicite, "prochaine_echeance": prochaine_echeance,
    })


def modifier_maintenance_preventive(identifiant, titre, equipement, periodicite, prochaine_echeance):
    _requete("PUT", f"/maintenance-preventive/{identifiant}", json={
        "titre": titre, "equipement": equipement,
        "periodicite": periodicite, "prochaine_echeance": prochaine_echeance,
    })


def supprimer_maintenance_preventive(identifiant):
    _requete("DELETE", f"/maintenance-preventive/{identifiant}")


def verifier_echeances():
    return _requete("POST", "/maintenance-preventive/verifier-echeances")