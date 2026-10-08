from pydantic import BaseModel


class LoginEntree(BaseModel):
    email: str
    mot_de_passe: str


class MaterielEntree(BaseModel):
    code: str
    nom: str
    categorie: str
    emplacement: str
    service: str = ""
    etat: str


class EtatEntree(BaseModel):
    etat: str


class DemandeEntree(BaseModel):
    equipement: str
    description: str
    demandeur: str
    priorite: str = "Normale"
    statut: str = "Nouvelle"


class TechnicienEntree(BaseModel):
    nom: str
    specialite: str = ""
    telephone: str = ""


class BonEntree(BaseModel):
    numero: str = ""
    di: str = ""
    equipement: str = ""
    technicien: str = ""
    statut: str = "À faire"
    travaux: str
    date_debut: str = ""
    date_fin: str = ""
    duree: str = ""
    cause: str = ""
    taches_realisees: str = ""


class RapportEntree(BaseModel):
    duree: str
    cause: str
    taches_realisees: str


class GenererBtEntree(BaseModel):
    technicien: str


class UtilisateurEntree(BaseModel):
    nom: str
    email: str
    mot_de_passe: str | None = None
    role: str


class PreventiveEntree(BaseModel):
    titre: str
    equipement: str
    periodicite: str
    prochaine_echeance: str