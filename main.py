import customtkinter as tk
from accueil import  Acceuill
from ajouter import AjouterMateriel
from materiels import ListesMateriels

tk.set_appearance_mode('dark')
tk.set_default_color_theme("green")

app = tk.CTk()
app.attributes('-zoomed', True)

def Open_Materiels():
    print("waiting For it")

def Ajouter_materiels():
    AjouterMateriel(app)

app.title("Gestion Matériel | ISSTM")
page_acceuil = Acceuill(app,Open_Materiels,Ajouter_materiels)
page_acceuil.pack(expand=True)


liste_materiel = ListesMateriels(app)
# liste_materiel.pack(fill="both", pady=5)








app.mainloop()