import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException

import models
import security
from schemas import (
    BonEntree,
    DemandeEntree,
    EtatEntree,
    GenererBtEntree,
    LoginEntree,
    MaterielEntree,
    PreventiveEntree,
    RapportEntree,
    TechnicienEntree,
    UtilisateurEntree,
)

API_KEY = os.getenv("GMAO_API_KEY", "gmao-dev-key")


@asynccontextmanager
async def lifespan(_app):
    models.initialiser_base()
    yield


app = FastAPI(title="API GMAO", version="2.0", lifespan=lifespan)


#======================================= sécurité ==============================================
def exiger_cle(x_api_key: Optional[str] = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante.")
    return x_api_key


def Depends_cle(x_api_key: Optional[str] = Header(default=None)):
    exiger_cle(x_api_key)
    return x_api_key


def exiger_utilisateur(
    x_api_key: Optional[str] = Header(default=None),
    x_auth_token: Optional[str] = Header(default=None),
):
    exiger_cle(x_api_key)
    email = security.email_par_token(x_auth_token or "")
    utilisateur = models.utilisateur_par_email(email) if email else None
    if not utilisateur:
        raise HTTPException(status_code=401, detail="Connexion requise. Utilisez /auth/login.")
    return utilisateur


def _introuvable(entite, identifiant):
    raise HTTPException(status_code=404, detail=f"{entite} {identifiant} introuvable.")


def _vers_dict(ligne):
    return dict(ligne)


def _utilisateur_public(utilisateur):
    return {c: utilisateur[c] for c in utilisateur.keys() if c != "mot_de_passe"}


def _erreur(fonction):
    try:
        return fonction()
    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))


@app.get("/health")
def sante():
    return {"statut": "ok"}


#======================================= authentification ==============================================
@app.post("/auth/login")
def connexion(entree: LoginEntree):
    utilisateur = models.utilisateur_par_email(entree.email)
    if not utilisateur or not security.verifier_mot_de_passe(entree.mot_de_passe, utilisateur["mot_de_passe"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
    token = security.creer_token(utilisateur["email"])
    return {"token": token, "utilisateur": _utilisateur_public(utilisateur)}


@app.get("/auth/me")
def moi(_cle: str = Depends(Depends_cle), utilisateur=Depends(exiger_utilisateur)):
    return _utilisateur_public(utilisateur)


#======================================= matériels ==============================================
@app.get("/materiels")
def liste_materiels(_cle: str = Depends(Depends_cle)):
    return [_vers_dict(m) for m in models.lister_materiels()]


@app.post("/materiels")
def creer_materiel(entree: MaterielEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.ajouter_materiel(
            entree.code, entree.nom, entree.categorie, entree.emplacement, entree.service, entree.etat
        )
        return {"detail": "Matériel créé."}

    return _erreur(_action)


@app.get("/materiels/{identifiant}")
def materiel_detail(identifiant: int, _cle: str = Depends(Depends_cle)):
    materiel = models.materiel_par_id(identifiant)
    if not materiel:
        _introuvable("Matériel", identifiant)
    return _vers_dict(materiel)


@app.put("/materiels/{identifiant}")
def modifier_materiel_endpoint(identifiant: int, entree: MaterielEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.modifier_materiel(
            identifiant, entree.code, entree.nom, entree.categorie, entree.emplacement,
            entree.service, entree.etat,
        )
        return {"detail": "Matériel modifié."}

    return _erreur(_action)


@app.delete("/materiels/{identifiant}")
def supprimer_materiel_endpoint(identifiant: int, _cle: str = Depends(Depends_cle)):
    models.supprimer_materiel(identifiant)
    return {"detail": "Matériel supprimé."}


@app.post("/materiels/{identifiant}/etat")
def changer_etat(identifiant: int, entree: EtatEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.changer_etat_materiel(identifiant, entree.etat)
        return {"detail": "État du matériel modifié."}

    return _erreur(_action)


#======================================= demandes d'intervention ==============================================
@app.get("/demandes-intervention")
def liste_demandes(_cle: str = Depends(Depends_cle)):
    return [_vers_dict(d) for d in models.lister_demandes()]


@app.post("/demandes-intervention")
def creer_demande(entree: DemandeEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        numero = models.ajouter_demande(
            entree.equipement, entree.description, entree.demandeur, entree.priorite, entree.statut
        )
        return {"numero": numero}

    return _erreur(_action)


@app.get("/demandes-intervention/{identifiant}")
def demande_detail(identifiant: int, _cle: str = Depends(Depends_cle)):
    demande = models.demande_par_id(identifiant)
    if not demande:
        _introuvable("Demande", identifiant)
    return _vers_dict(demande)


@app.put("/demandes-intervention/{identifiant}")
def modifier_demande_endpoint(identifiant: int, entree: DemandeEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.modifier_demande(
            identifiant, entree.equipement, entree.description, entree.demandeur,
            entree.priorite, entree.statut,
        )
        return {"detail": "Demande modifiée."}

    return _erreur(_action)


@app.delete("/demandes-intervention/{identifiant}")
def supprimer_demande_endpoint(identifiant: int, _cle: str = Depends(Depends_cle)):
    models.supprimer_demande(identifiant)
    return {"detail": "Demande supprimée."}


@app.post("/demandes-intervention/{identifiant}/generer-bt")
def generer_bt(identifiant: int, entree: GenererBtEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        numero = models.generer_bon_travail(identifiant, entree.technicien)
        return {"numero": numero}

    return _erreur(_action)


#======================================= techniciens ==============================================
@app.get("/techniciens")
def liste_techniciens(_cle: str = Depends(Depends_cle)):
    return [_vers_dict(t) for t in models.lister_techniciens()]


@app.post("/techniciens")
def creer_technicien(entree: TechnicienEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.ajouter_technicien(entree.nom, entree.specialite, entree.telephone)
        return {"detail": "Technicien créé."}

    return _erreur(_action)


@app.get("/techniciens/{identifiant}")
def technicien_detail(identifiant: int, _cle: str = Depends(Depends_cle)):
    technicien = models.technicien_par_id(identifiant)
    if not technicien:
        _introuvable("Technicien", identifiant)
    return _vers_dict(technicien)


@app.put("/techniciens/{identifiant}")
def modifier_technicien_endpoint(identifiant: int, entree: TechnicienEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.modifier_technicien(identifiant, entree.nom, entree.specialite, entree.telephone)
        return {"detail": "Technicien modifié."}

    return _erreur(_action)


@app.delete("/techniciens/{identifiant}")
def supprimer_technicien_endpoint(identifiant: int, _cle: str = Depends(Depends_cle)):
    models.supprimer_technicien(identifiant)
    return {"detail": "Technicien supprimé."}


#======================================= bons de travail ==============================================
@app.get("/bons-travail")
def liste_bons(_cle: str = Depends(Depends_cle)):
    return [_vers_dict(b) for b in models.lister_bons_travail()]


@app.post("/bons-travail")
def creer_bon(entree: BonEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        numero = models.ajouter_bon_travail(
            entree.numero, entree.di, entree.equipement, entree.technicien, entree.statut,
            entree.travaux, entree.date_debut, entree.date_fin,
        )
        return {"numero": numero}

    return _erreur(_action)


@app.get("/bons-travail/{identifiant}")
def bon_detail(identifiant: int, _cle: str = Depends(Depends_cle)):
    bon = models.bon_travail_par_id(identifiant)
    if not bon:
        _introuvable("Bon de travail", identifiant)
    return _vers_dict(bon)


@app.put("/bons-travail/{identifiant}")
def modifier_bon_endpoint(identifiant: int, entree: BonEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.modifier_bon_travail(
            identifiant, entree.numero, entree.di, entree.equipement, entree.technicien,
            entree.statut, entree.travaux, entree.date_debut, entree.date_fin,
        )
        return {"detail": "Bon de travail modifié."}

    return _erreur(_action)


@app.delete("/bons-travail/{identifiant}")
def supprimer_bon_endpoint(identifiant: int, _cle: str = Depends(Depends_cle)):
    models.supprimer_bon_travail(identifiant)
    return {"detail": "Bon de travail supprimé."}


@app.post("/bons-travail/{identifiant}/rapport")
def cloturer_bon(identifiant: int, entree: RapportEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.cloturer_bon_travail(
            identifiant, entree.duree, entree.cause, entree.taches_realisees
        )
        return {"detail": "Bon de travail clôturé, matériel remis en marche."}

    return _erreur(_action)


#======================================= maintenance préventive ==============================================
@app.get("/maintenance-preventive")
def liste_preventifs(_cle: str = Depends(Depends_cle)):
    return [_vers_dict(p) for p in models.lister_maintenances_preventives()]


@app.post("/maintenance-preventive")
def creer_preventif(entree: PreventiveEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.ajouter_maintenance_preventive(
            entree.titre, entree.equipement, entree.periodicite, entree.prochaine_echeance
        )
        return {"detail": "Maintenance préventive planifiée."}

    return _erreur(_action)


@app.get("/maintenance-preventive/{identifiant}")
def preventif_detail(identifiant: int, _cle: str = Depends(Depends_cle)):
    prev = models.maintenance_preventive_par_id(identifiant)
    if not prev:
        _introuvable("Maintenance préventive", identifiant)
    return _vers_dict(prev)


@app.put("/maintenance-preventive/{identifiant}")
def modifier_preventif_endpoint(identifiant: int, entree: PreventiveEntree, _cle: str = Depends(Depends_cle)):
    def _action():
        models.modifier_maintenance_preventive(
            identifiant, entree.titre, entree.equipement, entree.periodicite, entree.prochaine_echeance
        )
        return {"detail": "Maintenance préventive modifiée."}

    return _erreur(_action)


@app.delete("/maintenance-preventive/{identifiant}")
def supprimer_preventif_endpoint(identifiant: int, _cle: str = Depends(Depends_cle)):
    models.supprimer_maintenance_preventive(identifiant)
    return {"detail": "Maintenance préventive supprimée."}


@app.post("/maintenance-preventive/verifier-echeances")
def verifier_echeances(_cle: str = Depends(Depends_cle)):
    return {"bons_generes": models.verifier_echeances()}