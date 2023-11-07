import sqlite3
import datetime
import re


connection = sqlite3.connect("automoviles.db")
cursor = connection.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    rfc TEXT NOT NULL,
                    correo TEXT NOT NULL
                  )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    folio INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    monto_total REAL,
                    cancelada BOOLEAN DEFAULT 0,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                  )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS servicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    costo REAL NOT NULL
                  )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS detalles (
                    nota_id INTEGER,
                    servicio_id INTEGER,
                    PRIMARY KEY (nota_id, servicio_id),
                    FOREIGN KEY (nota_id) REFERENCES notas(id),
                    FOREIGN KEY (servicio_id) REFERENCES servicios(id)
                  )''')


connection.commit()
