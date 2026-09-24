import customtkinter as tk
from accueil import  Acceuill
from ajouter import AjouterMateriel
from materiels import ListesMateriels
from demandes_intervention import GestionDemandesIntervention
from bons_travail import GestionBonsTravail
from sideBar import SideBar
from models import initialiser_base

tk.set_appearance_mode('dark')
tk.set_default_color_theme("green")

app = tk.CTk()
initialiser_base()
try:
    app.state("zoomed")
except tk.TclError:
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")

app.title("Gestion Matériel | Groupe XX")


#=============== page menu
menu = tk.CTkFrame(app, bg_color="black")
menu.pack(side="left", fill=tk.Y)


#=============== conteneur page

page_conteneur = tk.CTkFrame(app, corner_radius=0, fg_color="transparent")
page_conteneur.pack(side="left", expand=True)

page_active = None


def afficher_page(nouvel_page):

    global page_active

    if page_active is not None:
        page_active.destroy()

    nouvel_page.pack(fill ="both", expand=True)
    page_active = nouvel_page




def ajouter_materiels():
    AjouterMateriel(app, open_materiels)

def page_acceuil():
    home = Acceuill(page_conteneur,open_materiels,ajouter_materiels)
    afficher_page(home)

def open_materiels():
    page_materiel = ListesMateriels(page_conteneur)
    afficher_page(page_materiel)


def open_demandes():
    page_demandes = GestionDemandesIntervention(page_conteneur)
    afficher_page(page_demandes)


def open_bons_travail():
    page_bons_travail = GestionBonsTravail(page_conteneur)
    afficher_page(page_bons_travail)


def side_bar():
    side_bar_page = SideBar(
        menu, page_acceuil, open_materiels, open_demandes, open_bons_travail
    )
    side_bar_page.pack()

page_acceuil()
side_bar()




app.mainloop()
