import customtkinter as tk
from accueil import  Acceuill
from ajouter import AjouterMateriel
from materiels import ListesMateriels

tk.set_appearance_mode('dark')
tk.set_default_color_theme("green")

app = tk.CTk()
app.attributes('-zoomed', True)

def open_materiels():
    page_acceuil.pack_forget()
    page_materiel = ListesMateriels(app)
    page_materiel.pack(expand=True)

def ajouter_materiels():
    AjouterMateriel(app)

app.title("Gestion Matériel | ISSTM")
page_acceuil = Acceuill(app,open_materiels,ajouter_materiels)
page_acceuil.pack(expand=True)









app.mainloop()