import sqlite3 as sql


#=======================================Initier la connexion ==============================================
class DatabaseConnection:
    _instance = None
    def __new__(cls):
        if  cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = sql.connect("database.db")
            cls._instance.cursor = cls._instance.db.cursor()

        return cls._instance

    def get_connection(self):
        return self.db
    def get_cursor(self):
        return self.db.cursor


#========================== Creation des tables =======================

class CreateTable:
    def __init__(self ):
        self.conn = DatabaseConnection().get_connection()
        self.cursor = self.conn.cursor()

    def create_table(self, nom_table,colonnes):
        self.cursor.execute(f"CREATE TABLE  IF NOT EXISTS {nom_table} ({colonnes})")
        self.conn.commit()


