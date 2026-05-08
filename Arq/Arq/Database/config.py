
import sqlite3
from functools import lru_cache


SQLITE_DATABASE = "ProLink.db"
MONGODB_URI = "mongodb+srv://Admin:ProLink123@prolink.bcknvo4.mongodb.net/chats_db?appName=ProLink"


def get_sqlite_connection():
    conn = sqlite3.connect(SQLITE_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def close_sqlite_connection(conn):
    if conn:
        conn.close()


class DatabaseConfig:
    
    SQLITE_DB = SQLITE_DATABASE
    MONGODB_URI = MONGODB_URI
    
    # Table names
    USUARIO = "usuario"
    CANDIDATO = "candidato"
    DELEGADO = "delegado"
    EMPRESA = "empresa"
    OFERTA = "oferta"
    POSTULACION = "postulacion"
    
    # MongoDB collections
    CHATS_COLLECTION = "chats"
