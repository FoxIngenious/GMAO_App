import customtkinter as tk
from accueil import  Acceuill
from ajouter import AjouterMateriel

tk.set_appearance_mode('dark')
tk.set_default_color_theme("green")

app = tk.CTk()
app.attributes('-zoomed', True)

def Open_Materiels():
    print("waiting For it")

def Ajouter_materiels():
    boite_dialogue_ajouter_materiel = AjouterMateriel(app)
    boite_dialogue_ajouter_materiel.pack()


app.title("Gestion Matériel | ISSTM")
page_acceuil = Acceuill(app,Open_Materiels,Ajouter_materiels)
page_acceuil.pack(expand=True)











app.mainloop()