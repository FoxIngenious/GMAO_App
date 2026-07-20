import customtkinter as tk

tk.set_appearance_mode('dark')
tk.set_default_color_theme("green")


class AjouterMateriel(tk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Ajouter un matériel")
        self.geometry("500x500")

# ===========================INPUT
        input_contenaire = tk.CTkFrame(self, fg_color="transparent")
        input_contenaire.pack(expand=True)

        def Enregistrer():
            nom = self.nom.get()
            categories = self.categories.get()
            emplacements = self.emplacements.get()
            etas= self.etas.get()

            # Ajouter_materiel(nom, categories, emplacements, etas) // a importer from models.py
            self.destroy()


        def annuler():
            self.nom.delete(0, "end")
            self.categories.delete(0, "end")
            self.emplacements.delete(0, "end")
            self.etas.delete(0, "end")

            self.destroy()


        nom_label = tk.CTkLabel(self, text="Nom du matériel", font=("Arial", 20))
        self.nom = tk.CTkEntry(
            input_contenaire,
            width=380,
            height=30,
            placeholder_text="Nom du matériel",
            font=("Arial", 20)
        )
        
        categories_label = tk.CTkLabel(self, text="Catégories", font=("Arial", 20))
        self.categories = tk.CTkEntry(
            input_contenaire,
            placeholder_text="Catégories",
            font=("Arial", 20),
            width=380,
            height=30
        )

        emplacements_label = tk.CTkLabel(self, text="Emplacements", font=("Arial", 20))
        self.emplacements = tk.CTkEntry(
            input_contenaire,
            placeholder_text="Emplacements( ex: labo Ginfo)",
            font=("Arial", 20),
            width=380,
            height=30
        )

        etas_label = tk.CTkLabel(self, text="Etas du matériel", font=("Arial", 20))
        self.etas = tk.CTkEntry(
            input_contenaire,
            placeholder_text="Etat (enddomagé)",
            font=("Arial", 20),
            width=380,
            height=30
        )

        self.enregistrer = tk.CTkButton(
            input_contenaire,
            text="Enregistrer",
            width=185,
            height=30,
            command=Enregistrer,
            corner_radius=8,
            font=("Arial", 20)
        )


        self.annuler = tk.CTkButton(
            input_contenaire,
            text="Annuler",
            width=185,
            height=30,
            command=annuler,
            corner_radius=8,
            font=("Arial", 20)
        )
        self.nom.grid(
            row=0,
            column=0,
            columnspan = 2,
            pady=10
        )

        self.categories.grid(
            row=1,
            column=0,
            columnspan = 2,
            pady=10
        )

        self.emplacements.grid(
            row=2,
            column=0,
            columnspan = 2,
            pady=10
        )

        self.etas.grid(
            row=3,
            column=0,
            columnspan = 2,
            pady=10
        )

        self.enregistrer.grid(
            row=4,
            column=0,
            pady=25
        )
        self.annuler.grid(
            row=4,
            column=1,
            pady=25
        )