import sqlite3
from sqlite3 import Error
import sys
import datetime
import re

# Conectar a la base de datos
try:
    with sqlite3.connect("Taller_Mecanico.db") as conn:
        mi_cursor = conn.cursor()

    # Crear las tablas
        mi_cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            rfc TEXT NOT NULL,
                            correo TEXT NOT NULL
                        )''')

        mi_cursor.execute('''CREATE TABLE IF NOT EXISTS notas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cliente_id INTEGER,
                            folio INTEGER NOT NULL,
                            fecha timestamp NOT NULL,
                            monto_total REAL,
                            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                        )''')

        mi_cursor.execute('''CREATE TABLE IF NOT EXISTS servicios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            costo REAL NOT NULL
                        )''')

        mi_cursor.execute('''CREATE TABLE IF NOT EXISTS detalles (
                            nota_id INTEGER,
                            servicio_id INTEGER,
                            PRIMARY KEY (nota_id, servicio_id),
                            FOREIGN KEY (nota_id) REFERENCES notas(id),
                            FOREIGN KEY (servicio_id) REFERENCES servicios(id)
                        )''')
except Error as e:
    print(e)
except Exception:
    print(f"Se produjo un problema:{sys.int_info()[0]}")
finally:
        # Guardar los cambios
        conn.commit()

def validar_fecha(fecha):
    try:
        fecha_obj = datetime.datetime.strptime(fecha, "%m-%d-%Y")
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

    mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo) VALUES (?, ?, ?)",
                   (nombre, rfc, correo))

    conn.commit()

def agregar_servicio(nombre, costo):
    if not nombre or nombre.isspace():
        print("El nombre no puede estar vacío.")
        return

    if costo <= 0:
        print("El costo debe ser superior a 0.00.")
        return

    mi_cursor.execute("INSERT INTO servicios (nombre, costo) VALUES (?, ?)",
                   (nombre, costo))

    conn.commit()

    import sqlite3
import datetime

# Conectar a la base de datos SQLite
conn = sqlite3.connect("taller_mecanico.db")
cursor = conn.cursor()

# Crear la tabla de servicios si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicios (
        clave INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        costo REAL NOT NULL
    )
""")
conn.commit()

def agregar_servicio():
    nombre = input("Ingrese el nombre del servicio: ")
    costo = float(input("Ingrese el costo del servicio: "))
    
    if costo <= 0:
        print("Los datos proporcionados no cumplen con las condiciones.")
        return
    
    cursor.execute("INSERT INTO servicios (nombre, costo) VALUES (?, ?)", (nombre, costo))
    conn.commit()
    print("Servicio agregado con éxito.")

def buscar_por_clave():
        cursor.execute("SELECT * FROM servicios ")
        servicios = cursor.fetchall()
    
        for servicio in servicios:
            print(f"Clave: {servicio[0]} |   Nombre: {servicio[1]}")
            print("-----------------------------------------------")


        clave = input("Ingrese el clave del servicio a buscar: ")
        cursor.execute("SELECT * FROM servicios WHERE (id) = (?)", (clave,))
        servicios = cursor.fetchall()
        
        if servicios:
            for servicio in servicios:
                print(f"Clave: {servicio[0]} | Nombre: {servicio[1]} | Costo: ${servicio[2]} ")
                print("-----------------------------------------------------------------------")
        else:
            print("No se encontraron servicios con ese nombre.")

    



def buscar_por_nombre():
    nombre = input("Ingrese el nombre del servicio a buscar: ")
    cursor.execute("SELECT * FROM servicios WHERE UPPER(nombre) = UPPER(?)", (nombre,))
    servicios = cursor.fetchall()
    
    if servicios:
        for servicio in servicios:
            print(f"Clave: {servicio[0] } | Nombre:      {servicio[1]} |  Costo: ${servicio[2]} ")
            print("-----------------------------------------------------------------------")
         
    else:
        print("No se encontraron servicios con ese nombre.")

def lista_clave():
        cursor.execute("SELECT * FROM servicios")
        servicios = cursor.fetchall()
        for servicio in servicios:
            print(f"Clave: {servicio[0]} |  Nombre: {servicio[1]}| Costo: ${servicio[2]} ")
            print("-----------------------------------------------------------------------")
                

def lista_nombre():
    cursor.execute("SELECT * FROM servicios ORDER BY nombre")
    servicios = cursor.fetchall()
    for servicio in servicios:
        print(f"Nombre: {servicio[1]}  | Clave: {servicio[0]}  | Costo: ${servicio[2]} ")
        print("-----------------------------------------------------------------------")
                


def agregar_nota(cliente_id, servicios_ids):
    mi_cursor.execute("SELECT id FROM clientes WHERE id=?", (cliente_id,))
    cliente = mi_cursor.fetchone()

    if cliente is None:
        print("El cliente no está registrado.")
        return

    mi_cursor.execute("SELECT MAX(folio) FROM notas")
    max_folio = mi_cursor.fetchone()[0]
    folio = max_folio + 1 if max_folio is not None else 1

    while True:
        fecha_ingresada = input("Ingrese la fecha (mm-dd-aaaa): ")
        fecha_valida = validar_fecha(fecha_ingresada)
        if fecha_valida:
            break

    mi_cursor.execute("INSERT INTO notas (folio, cliente_id, fecha) VALUES (?, ?, ?)",
                   (folio, cliente_id, fecha_valida.strftime("%m-%d-%Y")))
    nota_id = mi_cursor.lastrowid

    monto_total = 0
    for servicio_id in servicios_ids:
        mi_cursor.execute("SELECT costo FROM servicios WHERE id=?", (servicio_id,))
        costo_servicio = mi_cursor.fetchone()[0]
        monto_total += costo_servicio

        mi_cursor.execute("INSERT INTO detalles (nota_id, servicio_id) VALUES (?, ?)", (nota_id, servicio_id))

    mi_cursor.execute("UPDATE notas SET monto_total=? WHERE id=?", (monto_total, nota_id))

    conn.commit()

def main():
    while True:
        print("Taller Mecánico\n")
        print("MENU PRINCIPAL")
        print("1. Nota")
        print("2. Cliente")
        print("3. Servicio")
        print("4. Salir")
        opcion_menu = int(input("Elige una opción: "))

        if opcion_menu ==1:
            while True:
                print("1. Registrar una nota")
                print("2. Cancelar una nota")
                print("3. Consultas y Reportes")
                print("4. Volver al menu principal")
                print("")
                opcion_nota = int(input("Elige una opción:\n"))
                print("")
                if opcion_nota == 1:
                    #agregar_nota(cliente_id, servicios_ids)
                    try:
                        with sqlite3.connect("Taller_Mecanico.db") as conn:
                            mi_cursor = conn.cursor()
                            mi_cursor.execute("SELECT id, nombre FROM clientes")
                            
                            registro_clientes = mi_cursor.fetchall()
                            
                            print("Clientes Registrados")
                            print("")
                            print("Claves\tNombre")
                            print("*" * 30)
                            if registro_clientes:
                                for clave, nombre in registro_clientes:
                                    print(f"{clave:6}\t{nombre}")
                                
                            print("")
                                    
                    except Error as e:
                        print(e)
                    else:
                        try:
                            cliente_id = int(input("Ingresa la clave del cliente donde quiere registrar la nota: "))
                            
                            
                            valores_cliente = {"clave": cliente_id}
                            with sqlite3.connect("Taller_Mecanico.db") as conn:
                                mi_cursor = conn.cursor()
                                mi_cursor.execute("SELECT * FROM clientes WHERE id = :clave", valores_cliente)
                                llave = False
                                registro = mi_cursor.fetchall()
                                if registro:
                                    llave = True
                                if llave==True:
                                    try:
                                        servicios_ids = input("Ingresa las claves de los servicios (separadas por espacios): ")
                                        valores_servicios = {"servicio": servicios_ids}
                                        with sqlite3.connect("Taller_Mecanico.db") as conn:
                                            mi_cursor = conn.cursor()
                                            mi_cursor.execute("SELECT * FROM servicios WHERE id = :servicio", valores_servicios)
                                            registro = mi_cursor.fetchall()
                                            if registro:
                                                agregar_nota(cliente_id, servicios_ids)
                                                print("NOTA REGISTRADA")
                                                print("")
                                            else:
                                                print(f"No se encontro ningun servicio asociado a la clave: {servicios_ids}")
                                    except Error as e:
                                        print(e)
                                else:
                                    print(f"No se encontro el cliente con la clave {cliente_id}")
                                    print("")
                        
                        
                                    
                        except Error as e:
                            print(e)
                        except Exception:
                            print(f"Se produjo el siguiente error: {sys.int_info()[0]}")
                        
                            
                            
                            
                            
                elif opcion_nota == 2:
                    folio = input("Ingrese el folio de la nota a cancelar: \n")
                    valores = {"folio":folio}
                    try:
                        with sqlite3.connect("Taller_Mecanico.db") as conn:
                            mi_cursor = conn.cursor()
                            mi_cursor.execute("SELECT * FROM notas WHERE folio = :folio", valores)
                            llave2 = False
                            registro = mi_cursor.fetchall()
                            if registro:
                                llave2 = True
                                
                            if llave2==True:
                                try:
                                    with sqlite3.connect("Taller_Mecanico.db") as conn:
                                        mi_cursor = conn.cursor()
                                        mi_cursor.execute("")
                                        
                                except Error as e:
                                    print(e)
                            else:
                                print(f"No se encontro una nota en el sistema con el siguiente folio: {folio}")
                                print("")
                            
                    
                    except Error as e:
                        print(e)
                    finally:
                        conn.commit()
                        
                elif opcion_nota==4:
                    break
                    
                            
                        
                
                    
                    
        elif opcion_menu==2:
            while True:
                print("")
                print("1. Agregar Cliente")
                print("2. Consultas y Reportes")
                print("3. Volver al Menu")
                print("")
                
                opcion_servcios = int(input("Eliga una opcion:\n"))
                print("")
                if opcion_servcios==1:
                    nombre = input("Ingresa el nombre del cliente: ")
                    rfc = input("Ingresa el RFC del cliente: ")
                    correo = input("Ingresa el correo electrónico del cliente: ")
                    agregar_cliente(nombre, rfc, correo)
                    print("")
                    print("DATOS INSERTADOS")
                    print("")
                    
                elif opcion_servcios==2:
                    while True:
                        print("1. Listado de clientes registrados")
                        print("2. Busqueda por clave")
                        print("3. Busqueda por nombre")
                        print("4. Volver al menu de clientes")
                        print("")
                        
                        opcion_servcios_2 = int(input("Eliga una opcion:\n"))
                        print("")
                        
                        
                        if opcion_servcios_2==1:
                            while True:
                                print("")
                                print("1. Ordenado Por Clave")
                                print("2. Ordenado Por Nombre")
                                print("3. Volver al menu anterior")
                                print("")
                                opcion_servcios_3 = int(input("Eliga una opcion:\n"))
                                if opcion_servcios_3==1:
                                    try:
                                        with sqlite3.connect("Taller_Mecanico.db") as conn:
                                            mi_cursor = conn.cursor()
                                            mi_cursor.execute("select * from clientes \
                                                            order by id;")
                                            
                                            registro= mi_cursor.fetchall()
                                            print("Clientes Ordenados por ID")
                                            print("")
                                            print("Claves\tNombre\tRFC\t\tCorreo")
                                            print("*" * 60)
                                            if registro:
                                                for clave, nombre, rfc, correo in registro:
                                                    print(f"{clave:^6}{nombre}\t{rfc}\t{correo}")
                                                    print("")
                                                    
                                    except Error as e:
                                        print(e)
                                    except Exception:
                                        print(f"Se produjo el siguiente error: {sys.int_info()[0]}")
                                elif opcion_servcios_3==2:
                                    try:
                                        with sqlite3.connect("Taller_Mecanico.db") as conn:
                                            mi_cursor = conn.cursor()
                                            mi_cursor.execute("select * from clientes \
                                                            order by nombre;")
                                            
                                            registro= mi_cursor.fetchall()
                                            print("Clientes Ordenados por ID")
                                            print("")
                                            print("Claves\tNombre\tRFC\t\tCorreo")
                                            print("*" * 60)
                                            if registro:
                                                for clave, nombre, rfc, correo in registro:
                                                    print(f"{clave:^6}{nombre}\t{rfc}\t{correo}")
                                    except Error as e:
                                        print(e)
                                    except Exception:
                                        print(f"Se produjo el siguiente error: {sys.int_info()[0]}")
                                        
                                elif opcion_servcios_3==3:
                                    break
                        elif opcion_servcios_2==2:
                            clave_buscar=input("Ingrese el Id del cliente:\n")
                            valores = {"clave": clave_buscar}
                            try:
                                with sqlite3.connect("Taller_Mecanico.db") as conn:
                                    mi_cursor = conn.cursor()
                                    mi_cursor.execute("SELECT * FROM clientes WHERE id = :clave", valores)
                                    
                                    registro = mi_cursor.fetchall()
                                    
                                    print("")
                                    print("Claves\tNombre\tRFC\t\tCorreo")
                                    print("*" * 60)
                                    if registro:
                                        for clave, nombre, rfc, correo in registro:
                                            print(f"{clave:^6}{nombre}\t{rfc}\t{correo}")
                                            print("")
                            except Error as e:
                                print(e)
                            except Exception:
                                print(f"Se produjo el siguiente error: {sys.int_info()[0]}")
                                print("")
                                
                        elif opcion_servcios_2==3:
                            nombre_buscar=input("Ingrese el nombre del cliente:\n")
                            valores = {"nombre": nombre_buscar}
                            try:
                                with sqlite3.connect("Taller_Mecanico.db") as conn:
                                    mi_cursor = conn.cursor()
                                    mi_cursor.execute("SELECT * FROM clientes WHERE nombre = :nombre", valores)
                                    
                                    registro = mi_cursor.fetchall()
                                    
                                    print("")
                                    print("Claves\tNombre\tRFC\t\tCorreo")
                                    print("*" * 60)
                                    if registro:
                                        for clave, nombre, rfc, correo in registro:
                                            print(f"{clave:^6}{nombre}\t{rfc}\t{correo}")
                                            print("")
                            except Error as e:
                                print(e)
                            except Exception:
                                print(f"Se produjo el siguiente error: {sys.int_info()[0]}")
                                print("")
                                
                        elif opcion_servcios_2==4:
                            break
                            
                                                    
                elif opcion_servcios==3:
                    break
            
        elif opcion_menu==3:
            
            print ("1. Agregar un servicio")
            print ("2. Consultas y reportes")
            print ("3. Volver al menu principal")
            opcserv = int(input("Elija la opcion que desea: "))
            if opcserv == 1:
                agregar_servicio()
            elif opcserv == 2:
                print("Consultas y reportes")
                print("1. Busqueda por clave de servicio")
                print("2. Busqueda por nombre de servicio")
                print("3. Listado de servicios ordenados por clave")
                print("4. Listado de servicios ordenados por nombre")
                opcconsultas= int(input("Seleccione la opcion que desea: "))
                if opcconsultas == 1 :
                    buscar_por_clave()
                elif opcconsultas == 2:
                    buscar_por_nombre()
                elif opcconsultas == 3:
                    lista_clave()
                elif opcconsultas == 4:
                    lista_nombre()
                else : print ("Caracter invalido")
            
        elif opcion_menu==4:
            break
            
            
if __name__ == "__main__":
    main()
