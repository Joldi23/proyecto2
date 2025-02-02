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
        print(f"Error al guardar usuario: {e}", file=sys.stdout)
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
        print(f"Excepción al recuperar un usuario: {e}", file=sys.stdout)
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
        print("Excepcion al eliminar un usuario", file=sys.stdout)
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
        print(f"Error al actualizar un usuario: {e}", file=sys.stdout)
        ret = {"status": "Failure", "message": "Error interno del servidor"}
        code = 500
    return ret, code




def obtener_datos(dni):
    datos_json = {}
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute(""" 
                SELECT nombre, apellido1, apellido2, email, telefono, num_tarjeta 
                FROM usuarios WHERE dni = %s 
            """, (dni,))
            datos = cursor.fetchone()

            if datos:  # Verifica si `datos` no es None ni vacío
                datos_json = datosusu_json(datos)  

        
        conexion.close()
        code = 200  # Código de éxito
    except Exception as e:  # Manejo de errores
        print(f"Excepción al recuperar datos: {e}", file=sys.stdout)
        code = 500  # Código de error

    return datos_json, code

def datosusu_json(datos):
    d = {
        'nombre': datos[0],
        'apellido1': datos[1],
        'apellido2': datos[2],
        'email': datos[3],
        'telefono': datos[4],
        'num_tarjeta': datos[5] if len(datos) > 5 else ""  # Si existe, se envía; si no, se envía vacío
    }
    return d




def actualizarD(nombre, apellido1, apellido2, email, telefono, dni, num_tarjeta=None):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Guardamos el número de filas afectadas en la primera actualización
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, apellido1 = %s, apellido2 = %s, email = %s, telefono = %s
                WHERE dni = %s
            """, (nombre, apellido1, apellido2, email, telefono, dni))
            filas_afectadas = cursor.rowcount  # Guardamos cuántas filas se actualizaron

            # Si se proporciona un num_tarjeta válido, actualizamos la tarjeta
            if num_tarjeta not in (None, ""):
                cursor.execute("""
                    UPDATE usuarios 
                    SET num_tarjeta = %s,
                    membresia = TRUE
                    WHERE dni = %s
                """, (num_tarjeta, dni))
                filas_afectadas += cursor.rowcount  # Sumamos los cambios de la segunda consulta

            # Confirmamos los cambios si al menos una consulta afectó registros
            if filas_afectadas > 0:
                conexion.commit()
                ret = {"status": "OK"}
            else:
                ret = {"status": "Failure", "message": "No se encontró el registro o no hubo cambios"}

    except Exception as e:
        ret = {"status": "Failure", "message": "Error interno del servidor"}
    finally:
        if conexion:
            conexion.close()

    return ret, 200 if ret["status"] == "OK" else 400
