
import customtkinter as tk
tk.set_appearance_mode('dark')

class SideBar(tk.CTkFrame):
    def __init__(self,parent, page_acceuil,open_materiels):
        super().__init__(parent, fg_color="transparent")

        menu_contenaire = tk.CTkFrame(self, bg_color="black")
        menu_contenaire.pack()

        menus = [
            ["Acceuil", page_acceuil],
            ["Matériels", open_materiels]
        ]

        for label, command in menus:
            bttn = tk.CTkButton(
            menu_contenaire,
            text=label,
            fg_color="transparent",
            width=50,
            height=30,
            command=command,
            corner_radius=20,
            font=("Arial", 30)
            )
            bttn.pack(fill="x", padx=10, pady=8)