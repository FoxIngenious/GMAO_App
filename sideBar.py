import customtkinter as tk


class SideBar(tk.CTkFrame):
    def __init__(self, parent, role, actions):
        super().__init__(parent, fg_color="transparent")

        en_tete = tk.CTkFrame(self, fg_color="transparent")
        en_tete.pack(fill="x", padx=10, pady=(12, 6))
        tk.CTkLabel(
            en_tete, text=actions["utilisateur"], font=("Arial", 13), text_color="white"
        ).pack(anchor="w")
        tk.CTkLabel(
            en_tete, text=role, font=("Arial", 11), text_color="gray"
        ).pack(anchor="w")

        tk.CTkButton(
            self,
            text="Déconnexion",
            fg_color="#7a1f1f",
            hover_color="#9c2b2b",
            width=50,
            height=34,
            command=actions["deconnexion"],
            corner_radius=20,
            font=("Arial", 18),
        ).pack(side="bottom", fill="x", padx=10, pady=(10, 14))

        menu_contenaire = tk.CTkFrame(self, bg_color="black")
        menu_contenaire.pack(fill="both", expand=True)

        menus = []
        if role == "Responsable Maintenance":
            menus = [
                ("Accueil", actions["page_acceuil"]),
                ("Matériels", actions["open_materiels"]),
                ("Intervention", actions["open_demandes"]),
                ("Bons de travail", actions["open_bons_travail"]),
                ("Préventif", actions["open_preventif"]),
                ("Techniciens", actions["open_techniciens"]),
            ]
        elif role == "Technicien":
            menus = [
                ("Accueil", actions["page_acceuil"]),
                ("Bons de travail", actions["open_bons_travail"]),
                ("Intervention", actions["open_demandes"]),
            ]
        elif role == "Opérateur":
            menus = [
                ("Accueil", actions["page_acceuil"]),
                ("Intervention", actions["open_demandes"]),
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