
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



def validar_fecha(fecha):
    try:
        fecha_obj = datetime.datetime.strptime(fecha, "%d-%m-%Y")
        if fecha_obj <= datetime.datetime.now():
            return fecha_obj
        else:
            print("La fecha no puede ser posterior a la fecha actual.")
            return None
    except ValueError:
        print("Formato de fecha incorrecto. Debe ser dd-mm-aaaa.")
        return None

def agregar_cliente(nombre, rfc, correo):
    if not nombre or nombre.isspace():
        print("El nombre no puede estar vacío.")
        return

    if not re.match(r'^[A-ZÑ&]{3,4}\d{2}(0[1-9]|1[0-2])(0[1-9]|1\d|2\d|3[01])((H|M|h|m)(A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|NE|ne)[A-Z\d]{2}|[A-Z\d]{3})$', rfc):
        print("El RFC no es válido.")
        return

    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', correo):
        print("El correo electrónico no es válido.")
        return

    cursor.execute("INSERT INTO clientes (nombre, rfc, correo) VALUES (?, ?, ?)",
                   (nombre, rfc, correo))

    connection.commit()

def agregar_servicio(nombre, costo):
    if not nombre or nombre.isspace():
        print("El nombre no puede estar vacío.")
        return

    if costo <= 0:
        print("El costo debe ser superior a 0.00.")
        return

    cursor.execute("INSERT INTO servicios (nombre, costo) VALUES (?, ?)",
                   (nombre, costo))

    connection.commit()

def agregar_nota(cliente_id, servicios_ids):
    cursor.execute("SELECT id FROM clientes WHERE id=?", (cliente_id,))
    cliente = cursor.fetchone()

    if cliente is None:
        print("El cliente no está registrado.")
        return

    cursor.execute("SELECT MAX(folio) FROM notas")
    max_folio = cursor.fetchone()[0]
    folio = max_folio + 1 if max_folio is not None else 1

    while True:
        fecha_ingresada = input("Ingrese la fecha (dd-mm-aaaa): ")
        fecha_valida = validar_fecha(fecha_ingresada)
        if fecha_valida:
            break

    cursor.execute("INSERT INTO notas (folio, cliente_id, fecha) VALUES (?, ?, ?)",
                   (folio, cliente_id, fecha_valida.strftime("%d-%m-%Y")))
    nota_id = cursor.lastrowid

    monto_total = 0
    for servicio_id in servicios_ids:
        cursor.execute("SELECT costo FROM servicios WHERE id=?", (servicio_id,))
        costo_servicio = cursor.fetchone()[0]
        monto_total += costo_servicio

        cursor.execute("INSERT INTO detalles (nota_id, servicio_id) VALUES (?, ?)", (nota_id, servicio_id))

    cursor.execute("UPDATE notas SET monto_total=? WHERE id=?", (monto_total, nota_id))

    connection.commit()


def cancelar_nota(folio):
    
    cursor.execute("SELECT * FROM notas WHERE folio=?", (folio,))
    nota = cursor.fetchone()

    if nota is None:
        print("El folio indicado no existe.")
        return

   
    if nota[5]:  
        print("La nota ya ha sido cancelada.")
        return

    print(f"Folio: {nota[2]}, Fecha: {nota[3]}, Monto total: {nota[4]}")

    
    confirmacion = input("¿Estás seguro de que quieres cancelar esta nota? (s/n): ")

    if confirmacion.lower() == "s":
        
        cursor.execute("UPDATE notas SET cancelada=1 WHERE folio=?", (folio,))
        connection.commit()
        print("La nota ha sido cancelada.")
    else:
        print("La nota no ha sido cancelada.")



def recuperar_nota(folio):
    cursor.execute("SELECT * FROM notas WHERE folio=?", (folio,))
    nota = cursor.fetchone()

    if nota is None:
        print("El folio indicado no existe.")
        return

    if not nota[5]:  
        print("La nota no ha sido cancelada.")
        return
    print(f"Folio: {nota[2]}, Fecha: {nota[3]}, Monto total: {nota[4]}")

    confirmacion = input("¿Estás seguro de que quieres recuperar esta nota? (s/n): ")

    if confirmacion.lower() == "s":
        cursor.execute("UPDATE notas SET cancelada=0 WHERE folio=?", (folio,))
        connection.commit()
        print("La nota ha sido recuperada.")
    else:
        print("La nota no ha sido recuperada.")

# Se agregan las fuciones para consultas 


def consulta_por_periodo():
    fecha_inicial_ingresada = input("Ingrese la fecha inicial (dd-mm-aaaa) o deje en blanco para asumir 01-01-2000: ")
    if fecha_inicial_ingresada:
        fecha_inicial = validar_fecha(fecha_inicial_ingresada)
        if fecha_inicial is None:
            return
    else:
        fecha_inicial = datetime.datetime(2000, 1, 1)

    fecha_final_ingresada = input("Ingrese la fecha final (dd-mm-aaaa) o deje en blanco para asumir la fecha actual: ")
    if fecha_final_ingresada:
        fecha_final = validar_fecha(fecha_final_ingresada)
        if fecha_final is None:
            return
    else:
        fecha_final = datetime.datetime.now()

    if fecha_final < fecha_inicial:
        print("La fecha final debe ser igual o posterior a la fecha inicial.")
        return

    cursor.execute("""
        SELECT notas.folio, notas.fecha, clientes.nombre
        FROM notas
        JOIN clientes ON notas.cliente_id = clientes.id
        WHERE notas.fecha BETWEEN ? AND ?
        AND notas.cancelada = 0  -- Agregar esta condición para notas no canceladas
        GROUP BY notas.id
        """, (fecha_inicial.strftime("%d-%m-%Y"), fecha_final.strftime("%d-%m-%Y")))
    notas = cursor.fetchall()

    if notas:
        print('')
        print("Notas emitidas en el período especificado:")
        print('')
        print("*" * 50)
        print("{:<10} {:<15} {:<15}".format('Folio', 'Fecha', 'Nombre'))
        for nota in notas:
            print("{:<10} {:<15} {:<15}".format(nota[0], nota[1], nota[2]))
        print("*" * 50)
        print("")
    else:
        print("No hay notas emitidas para el período especificado.")



def consulta_por_folio():
    cursor.execute("""
        SELECT notas.folio, notas.fecha, clientes.nombre
        FROM notas
        JOIN clientes ON notas.cliente_id = clientes.id
        WHERE notas.cancelada = 0
        ORDER BY notas.folio
        """)
    notas = cursor.fetchall()

    print("Notas existentes:")
    for nota in notas:
        print(f"Folio: {nota[0]}, Fecha: {nota[1]}, Nombre del cliente: {nota[2]}")

    folio = int(input("Ingrese el folio de la nota a consultar: "))

    cursor.execute("""
        SELECT notas.folio, notas.fecha, clientes.nombre, clientes.rfc, clientes.correo, GROUP_CONCAT(servicios.nombre, ', '), notas.monto_total
        FROM notas
        JOIN clientes ON notas.cliente_id = clientes.id
        JOIN detalles ON notas.id = detalles.nota_id
        JOIN servicios ON detalles.servicio_id = servicios.id
        WHERE notas.folio = ? AND notas.cancelada = 0
        GROUP BY notas.id
        """, (folio,))
    nota = cursor.fetchone()

    if nota:
        
        print("")
        print('*' * 50)
        print(f"Folio: {nota[0]}")
        print(f"Fecha: {nota[1]}")
        print(f"Nombre del cliente: {nota[2]}")
        print(f"RFC del cliente: {nota[3]}")
        print(f"Correo del cliente: {nota[4]}")
        print(f"Servicios: {nota[5]}")
        print(f"Monto total: {nota[6]}")
        print('*' * 50)
        print("")
    else:
        print("El folio indicado no existe o corresponde a una nota cancelada.")