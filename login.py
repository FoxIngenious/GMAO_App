import customtkinter as tk
from tkinter import messagebox

import api_client


class EcranConnexion(tk.CTkToplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("Connexion — GMAO")
        self.geometry("440x440")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        conteneur = tk.CTkFrame(self, fg_color="transparent")
        conteneur.pack(expand=True)

        tk.CTkLabel(conteneur, text="GMAO — Connexion", font=("Arial", 28)).pack(pady=(0, 20))

        tk.CTkLabel(conteneur, text="Email", font=("Arial", 14)).pack(anchor="w")
        self.email = tk.CTkEntry(conteneur, width=340, font=("Arial", 14))
        self.email.pack(pady=(2, 12))

        tk.CTkLabel(conteneur, text="Mot de passe", font=("Arial", 14)).pack(anchor="w")
        self.mot_de_passe = tk.CTkEntry(conteneur, width=340, show="•", font=("Arial", 14))
        self.mot_de_passe.pack(pady=(2, 4))

        tk.CTkLabel(conteneur, text="admin.maintenance@usine.com / Admin2026!", font=("Arial", 11), text_color="gray").pack(pady=(0, 16))

        tk.CTkButton(conteneur, text="Se connecter", width=340, height=36, font=("Arial", 15), command=self.se_connecter).pack()

        self.email.insert(0, "admin.maintenance@usine.com")
        self.mot_de_passe.insert(0, "Admin2026!")
        self.bind("<Return>", lambda _event: self.se_connecter())
        self.mot_de_passe.bind("<Return>", lambda _event: self.se_connecter())

    def se_connecter(self):
        try:
            utilisateur = api_client.login(self.email.get().strip(), self.mot_de_passe.get())
        except ValueError as erreur:
            messagebox.showerror("Connexion", str(erreur), parent=self)
            return
        except ConnectionError as erreur:
            messagebox.showerror("API GMAO", str(erreur), parent=self)
            return
        self.destroy()
        self.on_success(utilisateur)