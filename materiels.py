# from tkinter import treeview
import customtkinter as ctk

class ListesMateriels(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        titre = ctk.CTkLabel(self, text="Nos matériel", font=("Arial", 50))
        titre.pack(pady=20)