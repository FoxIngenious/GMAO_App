import customtkinter as tk
from accueil import  Acceuill
from ajouter import AjouterMateriel
from materiels import ListesMateriels
from sideBar import SideBar

tk.set_appearance_mode('dark')
tk.set_default_color_theme("green")

app = tk.CTk()
app.attributes('-zoomed', True)

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
        page_active.pack_forget()

    nouvel_page.pack(fill ="both", expand=True)
    page_active = nouvel_page




def ajouter_materiels():
    AjouterMateriel(app)

def page_acceuil():
    home = Acceuill(page_conteneur,open_materiels,ajouter_materiels)
    afficher_page(home)

def open_materiels():
    page_materiel = ListesMateriels(page_conteneur)
    afficher_page(page_materiel)


def side_bar():
    side_bar_page = SideBar(menu, page_acceuil, open_materiels)
    side_bar_page.pack()


side_bar()
app.mainloop()
