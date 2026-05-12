import sqlite3
import os
import sys

# --- ESTA ES LA PARTE CLAVE ---
# Agregamos la carpeta actual al camino de búsqueda de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from jwt_middleware import hash_password
except ImportError:
    # Si lo ejecutas desde la raíz del proyecto
    from Cross.jwt_middleware import hash_password

# ... resto del código (setup_database, seed_data, etc.)

def setup_database():
    try:
        conn = sqlite3.connect("ProLink.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # --- Creación de Tablas ---
        cursor.execute(''' 
                   CREATE TABLE IF NOT EXISTS usuario 
                   (Id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nombre VARCHAR(100), 
                   correo VARCHAR(50) UNIQUE NOT NULL,
                   numero VARCHAR(10) NOT NULL,
                   tipoUsuario VARCHAR(20),
                   password TEXT NOT NULL
                   );
                   ''')
        cursor.execute(''' 
                   CREATE TABLE IF NOT EXISTS empresa 
                   ( empresaId INTEGER PRIMARY KEY AUTOINCREMENT,
                   razonSocial VARCHAR (100),
                   correoContacto VARCHAR(50),
                   direccion VARCHAR (50)    
                   );
                   ''')
        cursor.execute('''
                   CREATE TABLE IF NOT EXISTS delegado 
                   (delegadoId INTEGER PRIMARY KEY AUTOINCREMENT,
                   Id INTEGER NOT NULL REFERENCES usuario(Id) , 
                   empresaId INTEGER REFERENCES empresa(empresaId)                  
                   );
                   ''')
        cursor.execute('''
                   CREATE TABLE IF NOT EXISTS candidato 
                   (
                    candidatoId INTEGER PRIMARY KEY AUTOINCREMENT,
                    Id INTEGER NOT NULL REFERENCES usuario(Id),
                    profesion VARCHAR(50)
                   );
                   ''')
        cursor.execute('''
                   CREATE TABLE IF NOT EXISTS oferta
                   (
                    ofertaId INTEGER PRIMARY KEY AUTOINCREMENT,
                    empresaId INTEGER NOT NULL REFERENCES empresa(empresaId),
                    titulo VARCHAR (100) NOT NULL,
                    descripcionOferta VARCHAR (500),
                    profesionBuscar VARCHAR (50),
                    estadoOferta INTEGER DEFAULT 1
                   )
                   ''')
        cursor.execute('''
                   CREATE TABLE IF NOT EXISTS postulacion
                   (
                    postulacionId INTEGER PRIMARY KEY AUTOINCREMENT,
                    ofertaId INTEGER NOT NULL REFERENCES oferta(ofertaId),
                    candidatoId INTEGER NOT NULL REFERENCES candidato(candidatoId),
                    fechaPostulacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estadoPostulacion INTEGER DEFAULT 2  
                   ) 
                   ''')
        
        seed_data(cursor)
        conn.commit()
        print("Base de datos inicializada con éxito y contraseñas encriptadas.")
    except sqlite3.Error as e:
        print(f"Error al crear la base de datos: {e}")
    finally:
        if conn:            
            conn.close()

def seed_data(cursor):
    # Limpieza de datos existentes
    tables = ["postulacion", "oferta", "candidato", "delegado", "empresa", "usuario"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")

    # --- Usuarios con Claves Encriptadas ---
    # Candidatos
    cursor.execute('''INSERT INTO usuario (nombre, correo, numero, tipoUsuario, password) VALUES (?, ?, ?, ?, ?)''',
        ("Juan Perez", "juan@mail.com", "3001111111", "candidato", hash_password("JuanPerez123")))
    juan_id = cursor.lastrowid

    cursor.execute('''INSERT INTO usuario (nombre, correo, numero, tipoUsuario, password) VALUES (?, ?, ?, ?, ?)''',
        ("Maria Gomez", "maria@mail.com", "3002222222", "candidato", hash_password("MariaGomez123")))
    maria_id = cursor.lastrowid

    # Delegados
    cursor.execute('''INSERT INTO usuario (nombre, correo, numero, tipoUsuario, password) VALUES (?, ?, ?, ?, ?)''',
        ("Carlos Ruiz", "carlos@empresa.com", "3003333333", "delegado", hash_password("CarlosRuiz123")))
    carlos_id = cursor.lastrowid

    cursor.execute('''INSERT INTO usuario (nombre, correo, numero, tipoUsuario, password) VALUES (?, ?, ?, ?, ?)''',
        ("Ana Torres", "ana@empresa.com", "3004444444", "delegado", hash_password("AnaTorres123")))
    ana_id = cursor.lastrowid

    # --- Empresas ---
    cursor.execute("INSERT INTO empresa (razonSocial, correoContacto, direccion) VALUES (?, ?, ?)",
        ("Tech Solutions SAS", "contacto@tech.com", "Bogotá"))
    tech_id = cursor.lastrowid

    cursor.execute("INSERT INTO empresa (razonSocial, correoContacto, direccion) VALUES (?, ?, ?)",
        ("Innovatech Ltda", "info@innovatech.com", "Medellín"))
    innova_id = cursor.lastrowid

    # --- Relaciones Delegados ---
    cursor.execute("INSERT INTO delegado (Id, empresaId) VALUES (?, ?)", (carlos_id, tech_id))
    cursor.execute("INSERT INTO delegado (Id, empresaId) VALUES (?, ?)", (ana_id, innova_id))

    # --- Relaciones Candidatos ---
    cursor.execute("INSERT INTO candidato (Id, profesion) VALUES (?, ?)", (juan_id, "Ingeniero de Software"))
    juan_cand_id = cursor.lastrowid

    cursor.execute("INSERT INTO candidato (Id, profesion) VALUES (?, ?)", (maria_id, "Analista de Datos"))
    maria_cand_id = cursor.lastrowid

    # --- Ofertas ---
    cursor.execute('''INSERT INTO oferta (empresaId, titulo, descripcionOferta, profesionBuscar, estadoOferta) VALUES (?, ?, ?, ?, ?)''',
        (tech_id, "Backend Developer", "Desarrollador backend con Python", "Ingeniero de Software", 1))
    oferta1_id = cursor.lastrowid

    # --- Postulaciones ---
    cursor.execute("INSERT INTO postulacion (ofertaId, candidatoId, estadoPostulacion) VALUES (?, ?, ?)",
        (oferta1_id, juan_cand_id, 0))

if __name__=="__main__":
    setup_database()