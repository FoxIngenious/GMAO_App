import sqlite3 as sql
from pathlib import Path


#=======================================Initier la connexion ==============================================
class DatabaseConnection:
    chemin = Path(__file__).resolve().parent / "database.db"

    def get_connection(self):
        connexion = sql.connect(self.chemin)
        connexion.row_factory = sql.Row
        return connexion

    def get_cursor(self):
        return self.get_connection().cursor()


#========================== Creation des tables =======================

class CreateTable:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()
        self.cursor = self.conn.cursor()

    def create_table(self, nom_table, colonnes):
        self.cursor.execute(f"CREATE TABLE  IF NOT EXISTS {nom_table} ({colonnes})")
        self.conn.commit()