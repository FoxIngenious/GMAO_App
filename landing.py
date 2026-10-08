import customtkinter as tk


class AccueilPublic(tk.CTkFrame):
    def __init__(self, parent, ouvrir_connexion):
        super().__init__(parent, fg_color="transparent")

        centre = tk.CTkFrame(self, fg_color="transparent")
        centre.place(relx=0.5, rely=0.5, anchor="center")

        tk.CTkLabel(centre, text="GMAO", font=("Arial", 110, "bold")).pack()
        tk.CTkLabel(
            centre,
            text="Gestion de matériel",
            font=("Arial", 34),
            text_color="gray",
        ).pack(pady=(0, 50))

        tk.CTkButton(
            centre,
            text="Se connecter",
            width=280,
            height=52,
            corner_radius=26,
            font=("Arial", 20),
            command=ouvrir_connexion,
        ).pack()
