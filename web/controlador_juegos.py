from __future__ import print_function
from bd import obtener_conexion
import sys

def insertar_clase(dni, nombre, capacidad, horario, duracion_minutos):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:

            cursor.execute("INSERT INTO clases (id_entrenador, nombre, capacidad, horario, duracion_minutos) VALUES (%s, %s, %s, %s, %s)",
                       (dni, nombre, capacidad, horario, duracion_minutos))
            if cursor.rowcount == 1:
                ret={"status": "OK" }
            else:
                ret = {"status": "Failure" }
        code=200
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Error al guardar el juego: {e}", file=sys.stdout)
        ret = {"status": "Failure", "message": "Error interno del servidor"}
        code = 500
    return ret,code




def obtener_dni_por_usuario(email):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Consulta para obtener el DNI asociado al usuario
            cursor.execute("SELECT dni FROM usuarios WHERE email = %s", (email,))
            resultado = cursor.fetchone()
        
        conexion.close()
        
        if resultado:
            return {"status": "OK", "dni": resultado[0]}  # Devuelve el DNI si existe
        else:
            return {"status": "ERROR", "mensaje": "Usuario no encontrado"}
    
    except Exception as e:
        print(f"Error al obtener el DNI: {e}")
        return {"status": "ERROR", "mensaje": "Error al acceder a la base de datos"}


def convertir_clase_json(clase):
    d = {}
    d['id_clase'] = clase[0]
    d['nombre'] = clase[1]
    d['id_entrenador'] = clase[2]
    d['capacidad'] = clase[3]
    
    # Formatear el horario si no es None
    if clase[4] is not None:
        d['horario'] = clase[4].strftime('%Y-%m-%dT%H:%M')  # Formato compatible con datetime-local
    else:
        d['horario'] = None
    
    d['duracion_minutos'] = clase[5]
    return d


def obtener_clase_por_id(id_clase):
    clasejson = {}
    
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_clase, nombre, id_entrenador, capacidad, horario, duracion_minutos FROM clases WHERE id_clase = %s", (id_clase,))
            clase = cursor.fetchone()
            if clase is not None:
                clasejson = convertir_clase_json(clase)
        conexion.close()
        code = 200
    except Exception as e:  # Manejo específico de excepciones
        print(f"Excepción al recuperar un juego: {e}", file=sys.stdout)
        code = 500
    return clasejson,code


def eliminar_clase(id_clase):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM clases WHERE id_clase = %s", (id_clase,))
            if cursor.rowcount == 1:
                ret={"status": "OK" }
            else:
                ret={"status": "Failure" }
        conexion.commit()
        conexion.close()
        code=200
    except:
        print("Excepcion al eliminar un juego", file=sys.stdout)
        ret = {"status": "Failure" }
        code=500
    return ret,code




def actualizar_clase(id_clase, id_entrenador, nombre, capacidad, horario, duracion_minutos):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Actualizar los datos en la tabla clases, ahora incluyendo el id_entrenador
            cursor.execute("""
                UPDATE clases 
                SET id_entrenador = %s, 
                    nombre = %s, 
                    capacidad = %s, 
                    horario = %s, 
                    duracion_minutos = %s
                WHERE id_clase = %s
            """, (id_entrenador, nombre, capacidad, horario, duracion_minutos, id_clase))
            
            # Comprobar si se actualizó al menos una fila
            if cursor.rowcount == 1:
                ret = {"status": "OK"}
            else:
                ret = {"status": "Failure", "message": "No se encontró el registro o no se realizó ningún cambio"}
        
        code = 200
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Error al actualizar el juego: {e}", file=sys.stdout)
        ret = {"status": "Failure", "message": "Error interno del servidor"}
        code = 500
    return ret, code



def obtener_datos(dni):
    datos_json = {}
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Consulta SQL con INNER JOIN
            cursor.execute("""
                SELECT 
                    u.nombre, 
                    u.apellido1, 
                    u.apellido2, 
                    u.email, 
                    u.telefono, 
                    p.num_tarjeta
                FROM 
                    usuarios u
                INNER JOIN 
                    pagos p
                ON 
                    u.dni = p.id_usuario
                WHERE 
                    u.dni = %s
            """, (dni,))
            
            datos = cursor.fetchone()  # Obtener los datos
            if datos is not None:
                datos_json = datosusu_json(datos)  # Convertir en JSON
        
        conexion.close()
        code = 200  # Código de éxito
    except Exception as e:  # Manejo de errores
        print(f"Excepción al recuperar datos: {e}", file=sys.stdout)
        code = 500  # Código de error

    return datos_json, code

def datosusu_json(datos):
    d = {}
    d['nombre'] = datos[0]
    d['apellido1'] = datos[1]
    d['apellido2'] = datos[2]
    d['email'] = datos[3]
    d['telefono'] = datos[4]
    # Agregar el número de tarjeta
    d['num_tarjeta'] = datos[5]
    return d



def actualizarD(nombre, apellido1, apellido2, email, telefono, dni, num_tarjeta=None):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Actualizar los datos en la tabla usuarios
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, 
                    apellido1 = %s, 
                    apellido2 = %s, 
                    email = %s, 
                    telefono = %s
                WHERE dni = %s
            """, (nombre, apellido1, apellido2, email, telefono, dni))

            if cursor.rowcount >= 1:
                ret = {"status": "OK"}
            else:
                ret = {"status": "Failure", "message": "No se encontró el registro o no se realizó ningún cambio"}


            # Actualizar el número de tarjeta en la tabla pagos, si se proporciona
            if num_tarjeta is not None:
                cursor.execute("""
                    UPDATE pagos 
                    SET num_tarjeta = %s
                    WHERE id_usuario = %s
                """, (num_tarjeta, dni))
                
            if cursor.rowcount >= 1:
                ret = {"status": "OK"}
            else:
                ret = {"status": "Failure", "message": "No se encontró el registro o no se realizó ningún cambio"}


            # Comprobar si se actualizó al menos una fila en la tabla usuarios
            
        code = 200
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Error al actualizar el juego: {e}", file=sys.stdout)
        ret = {"status": "Failure", "message": "Error interno del servidor"}
        code = 500
    return ret, code

