from __future__ import print_function
from bd import obtener_conexion
import sys
import bcrypt
import traceback

def insertar_clase(usuario, nombre, capacidad, horario, duracion_minutos):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT dni FROM usuarios WHERE email = %s", (usuario,))
            resultado = cursor.fetchone()
            
            if not resultado:
                return {"status": "Failure", "message": "Usuario no encontrado"}, 404     
            dni = resultado[0]
            
            cursor.execute(
                "INSERT INTO clases (id_entrenador, nombre, capacidad, horario, duracion_minutos) VALUES (%s, %s, %s, %s, %s)",
                (dni, nombre, capacidad, horario, duracion_minutos)
            )
            
            if cursor.rowcount == 1:
                ret = {"status": "OK"}
            else:
                ret = {"status": "Failure"}
        
        code = 200
        conexion.commit()
        conexion.close()
    except Exception as e:
        ret = {"status": "Failure", "message": "Error interno del servidor"}
        code = 500
    
    return ret, code


def convertir_clase_json(clase):
    d = {}
    d['id_clase'] = clase[0]
    d['nombre'] = clase[1]
    d['id_entrenador'] = clase[2]
    d['capacidad'] = clase[3]
    
    
    if clase[4] is not None:
        d['horario'] = clase[4].strftime('%Y-%m-%dT%H:%M')  
    else:
        d['horario'] = None
    
    d['duracion_minutos'] = clase[5]
    return d


def obtener_clases():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            query = """SELECT id_clase, nombre, id_entrenador, capacidad, horario, duracion_minutos FROM clases"""
            cursor.execute(query)
            clases = cursor.fetchall()
        conexion.close()

        return [
            {
                "id_clase": clase[0],
                "nombre": clase[1],
                "id_entrenador": clase[2],
                "capacidad": clase[3],
                "horario": clase[4].strftime('%Y-%m-%d %H:%M:%S'),
                "duracion_minutos": clase[5],
            }
            for clase in clases
        ]
    except Exception as e:
        print(f"Error al obtener las clases: {e}")
        return None


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
    except Exception as e:  
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




def actualizar_clase(usuario, id_clase, nombre, capacidad, horario, duracion_minutos):
    try:
        conexion = obtener_conexion()
        
        with conexion.cursor() as cursor:
            cursor.execute("SELECT dni FROM usuarios WHERE email = %s", (usuario,))
            resultado = cursor.fetchone()

            if not resultado:
                return {"status": "Failure", "message": "Usuario no encontrado"}, 404

            id_entrenador = resultado[0]
            cursor.execute("""
                UPDATE clases 
                SET 
                    nombre = %s, 
                    capacidad = %s, 
                    horario = %s, 
                    duracion_minutos = %s
                WHERE id_clase = %s AND id_entrenador = %s
            """, (nombre, capacidad, horario, duracion_minutos, id_clase, id_entrenador))
            
            if cursor.rowcount == 1:
                ret = {"status": "OK"}
                code = 200  
            else:
                ret = {"status": "Failure", "message": "No se encontró el registro o no se realizó ningún cambio"}
                code = 404  
        conexion.commit()
        conexion.close()
    except Exception as e:
        ret = {"status": "Failure", "message": "Error interno del servidor"}
        code = 500 
        print("Detalles del error:", e)
    
    return ret, code







def obtener_datos(usuario):  #revisar
    datos_json = {}
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute(""" 
                SELECT nombre, apellido1, apellido2, email, telefono, num_tarjeta 
                FROM usuarios WHERE email = %s 
            """, (usuario,))
            datos = cursor.fetchone()

            if datos:  
                datos_json = datosusu_json(datos)  

        
        conexion.close()
        code = 200  
    except Exception as e:  
        print(f"Excepción al recuperar datos: {e}", file=sys.stdout)
        code = 500  

    return datos_json, code

def datosusu_json(datos):
    d = {
        'nombre': datos[0],
        'apellido1': datos[1],
        'apellido2': datos[2],
        'email': datos[3],
        'telefono': datos[4],
        'num_tarjeta': datos[5] if len(datos) > 5 else ""  
    }
    return d


def actualizarD(nombre, apellido1, apellido2, telefono,num_tarjeta, usuario):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, apellido1 = %s, apellido2 = %s, telefono = %s 
                WHERE email = %s
            """, (nombre, apellido1, apellido2, telefono, usuario))
            
            filas_afectadas = cursor.rowcount
            
            if num_tarjeta not in (None, ""):
                cursor.execute("""
                    UPDATE usuarios 
                    SET num_tarjeta = %s, membresia = TRUE
                    WHERE email = %s
                """, (num_tarjeta, usuario))
                filas_afectadas += cursor.rowcount
            
            if filas_afectadas > 0:
                conexion.commit()
                ret = {"status": "OK"}
            else:
                ret = {"status": "Failure"}
        
        conexion.close()
        return ret, 200
    except Exception as e:
        return {"status": "Failure", "message": "Error interno del servidor"}, 500



def obtener_foto_usuario(dni):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT foto FROM usuarios WHERE dni=%s", (dni,))
            resultado = cursor.fetchone()
        conexion.close()
        
        return resultado[0] if resultado and resultado[0] else ""
    except Exception as e:
        print(f"Error al obtener la foto del usuario: {e}")
        return None







