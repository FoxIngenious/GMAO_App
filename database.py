import sqlite3 as sql
from pathlib import Path


#=======================================Initier la connexion ==============================================
class DatabaseConnection:
    _instance = None
    def __new__(cls):
        if  cls._instance is None:
            cls._instance = super().__new__(cls)
            database_path = Path(__file__).resolve().parent / "database.db"
            cls._instance.db = sql.connect(database_path)
            cls._instance.db.row_factory = sql.Row

        return cls._instance

    def get_connection(self):
        return self.db
    def get_cursor(self):
        return self.db.cursor()


#========================== Creation des tables =======================

class CreateTable:
    def __init__(self ):
        self.conn = DatabaseConnection().get_connection()
        self.cursor = self.conn.cursor()

    def create_table(self, nom_table,colonnes):
        self.cursor.execute(f"CREATE TABLE  IF NOT EXISTS {nom_table} ({colonnes})")
        self.conn.commit()


