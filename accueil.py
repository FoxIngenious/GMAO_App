
import customtkinter as tk
tk.set_appearance_mode('dark')

class Acceuill(tk.CTkFrame):
    def __init__(self,parent,Open_Materiels,Ajouter_materiels):
        super().__init__(parent, fg_color="transparent")

        titre = tk.CTkLabel(self, text="Gestion de matériel - ISSTM", font=("Arial", 100))
        titre.pack(pady=50)

        button_contenaire = tk.CTkFrame(self, fg_color="transparent")
        button_contenaire.pack(pady=20)


        materiels_button = tk.CTkButton(
            button_contenaire,
            text="Matériels Disponible",
            width=200,
            height=30,
            command=Open_Materiels,
            corner_radius=20,
            font=("Arial", 50)
        )

        ajouter_boutton = tk.CTkButton(
            button_contenaire,
            text="+ Nouveau matériels",
            width=200,
            height=30,
            command=Ajouter_materiels,
            corner_radius=20,
            font=("Arial", 50)
        )

        materiels_button.grid(
            row=0,
            column=0,
            padx=10
        )
        ajouter_boutton.grid(
            row=0,
            column=1,
            padx=10
        )







