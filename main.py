import subprocess
import sys
import threading
import time

import customtkinter as tk
from tkinter import TclError

from accueil import Acceuill
from ajouter import AjouterMateriel
from bons_travail import GestionBonsTravail
from demandes_intervention import GestionDemandesIntervention
from login import EcranConnexion
from landing import AccueilPublic
from materiels import ListesMateriels
from preventif import GestionMaintenancePreventive
from sideBar import SideBar
from techniciens import GestionTechniciens
import api_client

tk.set_appearance_mode('dark')
tk.set_default_color_theme("green")

app = tk.CTk()

page_active = None
utilisateur_courant = None
barre_laterale = None


#=============== démarrage de l'API =================
def _lancer_api():
    try:
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def demarrer_api():
    if api_client.est_joignable():
        return
    threading.Thread(target=_lancer_api, daemon=True).start()
    for _ in range(75):
        if api_client.est_joignable():
            return
        time.sleep(0.2)


#=============== navigation =================
def afficher_page(nouvel_page):
    global page_active
    if page_active is not None:
        page_active.destroy()
    if isinstance(nouvel_page, Acceuill):
        nouvel_page.pack(expand=True)
    else:
        nouvel_page.pack(fill="both", expand=True)
    page_active = nouvel_page


def ajouter_materiels():
    AjouterMateriel(app, open_materiels)


def page_acceuil():
    home = Acceuill(page_conteneur, open_materiels, ajouter_materiels)
    afficher_page(home)


def open_materiels():
    page_materiel = ListesMateriels(page_conteneur)
    afficher_page(page_materiel)


def open_demandes():
    page_demandes = GestionDemandesIntervention(page_conteneur, utilisateur_courant)
    afficher_page(page_demandes)


def open_bons_travail():
    page_bons_travail = GestionBonsTravail(page_conteneur, utilisateur_courant)
    afficher_page(page_bons_travail)


def open_techniciens():
    page_techniciens = GestionTechniciens(page_conteneur)
    afficher_page(page_techniciens)


def open_preventif():
    page_preventif = GestionMaintenancePreventive(page_conteneur)
    afficher_page(page_preventif)


def ouvrir_connexion():
    EcranConnexion(app, ouvrir_interface)


def deconnexion():
    global utilisateur_courant, barre_laterale
    api_client.logout()
    utilisateur_courant = None
    if barre_laterale is not None:
        barre_laterale.destroy()
        barre_laterale = None
    menu.pack_forget()
    afficher_page(AccueilPublic(page_conteneur, ouvrir_connexion))


def ouvrir_interface(utilisateur):
    global utilisateur_courant, barre_laterale
    utilisateur_courant = utilisateur
    actions = {
        "utilisateur": utilisateur["nom"],
        "page_acceuil": page_acceuil,
        "open_materiels": open_materiels,
        "open_demandes": open_demandes,
        "open_bons_travail": open_bons_travail,
        "open_preventif": open_preventif,
        "open_techniciens": open_techniciens,
        "deconnexion": deconnexion,
    }
    if barre_laterale is not None:
        barre_laterale.destroy()
    menu.pack(side="left", fill=tk.Y, before=page_conteneur)
    barre_laterale = SideBar(menu, utilisateur["role"], actions)
    barre_laterale.pack(fill="both", expand=True)
    page_acceuil()


#=============== fenêtre principale =================
try:
    app.state("zoomed")
except TclError:
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")

app.title("Gestion Matériel | Groupe 02")

menu = tk.CTkFrame(app, bg_color="black")
menu.pack_forget()

page_conteneur = tk.CTkFrame(app, corner_radius=0, fg_color="transparent")
page_conteneur.pack(side="left", expand=True, fill="both")

demarrer_api()
afficher_page(AccueilPublic(page_conteneur, ouvrir_connexion))

app.mainloop()