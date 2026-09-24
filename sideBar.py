import customtkinter as tk


class SideBar(tk.CTkFrame):
    def __init__(self, parent, page_acceuil, open_materiels, open_demandes, open_bons_travail):
        super().__init__(parent, fg_color="transparent")

        menu_contenaire = tk.CTkFrame(self, bg_color="black")
        menu_contenaire.pack()
        menus = [
            ("Accueil", page_acceuil),
            ("Matériels", open_materiels),
            ("Intervention", open_demandes),
            ("Bons de travail", open_bons_travail),
        ]

        for label, command in menus:
            tk.CTkButton(
                menu_contenaire,
                text=label,
                fg_color="transparent",
                width=50,
                height=30,
                command=command,
                corner_radius=20,
                font=("Arial", 20),
            ).pack(fill="x", padx=10, pady=8)
