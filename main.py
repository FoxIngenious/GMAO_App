import customtkinter as tk
from accueil import  Acceuill
tk.set_default_color_theme("green")

tk.set_appearance_mode('dark')
app = tk.CTk()
app.attributes('-zoomed', True)

def Open_Materiels():
    print("waiting For it")

def Ajouter_materiels():
    print("waiting For it")


app.title("Gestion Matériel | ISSTM")
page_acceuil = Acceuill(app,Open_Materiels,Ajouter_materiels)
page_acceuil.pack(expand=True)











app.mainloop()