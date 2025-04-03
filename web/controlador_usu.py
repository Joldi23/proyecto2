from __future__ import print_function
from bd import obtener_conexion
import sys
import bcrypt
import traceback
from flask_wtf.csrf import generate_csrf
from funciones_auxiliares import compare_password, cipher_password,create_session
import datetime as dt
from __main__ import app

def verificar_contraseña(password, stored_hash):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    except Exception as e:
        print(f"Error al verificar contraseña: {e}", file=sys.stdout)
        return False

def alta_usuario(dni, password, username, nombre, apellido1, apellido2, telefono, fecha_nacimiento, num_tarjeta):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT perfil FROM usuarios WHERE email = %s",(username,))
            membresia = True if num_tarjeta else False
            usuario = cursor.fetchone()
            if usuario is None:
                passwordC=cipher_password(password)
                cursor.execute("""
                INSERT INTO usuarios (dni, password, email, nombre, apellido1, apellido2, telefono, fecha_nacimiento, num_tarjeta, membresia)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (dni, passwordC, username, nombre, apellido1, apellido2, telefono, fecha_nacimiento, num_tarjeta, membresia))
                if cursor.rowcount == 1:
                    conexion.commit()
                    app.logger.info("Nuevo usuario creado")
                    ret={"status": "OK" }
                    code=200
                else:
                    ret={"status": "ERROR" }
                    code=500
            else:
                ret = {"status": "ERROR","mensaje":"Usuario ya existe" }
                code=200
        conexion.close()
    except Exception as e:
        app.logger.error(f"Excepción al registrar el usuario: {e}")
        ret={"status":"ERROR"}
        code=500
    return ret,code

def obtener_datos_usuario(email):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            query = """
                SELECT nombre, apellido1, apellido2, email, telefono, fecha_nacimiento, membresia, foto
                FROM usuarios
                WHERE email = %s
            """
            cursor.execute(query, (email,))
            usuario = cursor.fetchone()
        conexion.close()
        return usuario
    except Exception as e:
        print(f"🚨 Error al obtener datos del usuario: {e}", file=sys.stdout)
        print(traceback.format_exc(), file=sys.stdout)
        return None
    

#perfil = es_trabajador
def login_usuario(username,passwordIn):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT perfil,password,numeroAccesosErroneo FROM usuarios WHERE estado='activo' and email = %s",(username))
            usuario = cursor.fetchone()
            
            if usuario is None:
                ret = {"status": "ERROR","mensaje":"Usuario/clave erroneo" }
            else:
                perfil=usuario[0]
                password=usuario[1]
                numAccesosErroneos=usuario[2]

                current_date = dt.date.today()
                hoy=current_date.strftime('%Y-%m-%d')
                    
                if (compare_password(password.encode("utf-8"),passwordIn.encode("utf-8"))):
                    ret = {"status": "OK",
                           "csrf_token": generate_csrf(),
                           "perfil":perfil}
                    app.logger.info("Acceso usuario %s correcto",username)
                    create_session(username,perfil)
                    numAccesosErroneos=0
                    estado='activo'
                else:
                    app.logger.info("Acceso usuario %s incorrecto",username)
                    numAccesosErroneos=numAccesosErroneos+1
                    if (numAccesosErroneos>2):
                        estado="bloqueado"
                        app.logger.info("Usuario %s bloqueado",username)
                    else:
                        estado='activo'
                    ret = {"status": "ERROR","mensaje":"Usuario/clave erroneo"}
                cursor.execute("UPDATE usuarios SET numeroAccesosErroneo=%s, fechaUltimoAcceso=%s, estado=%s WHERE email = %s",(numAccesosErroneos,hoy,estado,username))
                conexion.commit()
                conexion.close()
            code=200
    except:
        print("Excepcion al validar al usuario")   
        ret={"status":"ERROR"}
        code=500
    return ret,code

