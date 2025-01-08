from __future__ import print_function
from __main__ import app
from flask import request,session
from bd import obtener_conexion
import json
import sys
import bcrypt

@app.route("/login", methods=['POST'])
def login():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        juego_json = request.json
        username = juego_json.get('username')
        password = juego_json.get('passwordd')

        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                # Buscar el hash de la contraseña almacenado en la base de datos
                cursor.execute("SELECT passwordd, dni FROM usuarios WHERE email = %s", (username,))
                usuario = cursor.fetchone()

            conexion.close()

            if usuario is None:
                # Si no se encuentra el usuario
                ret = {"status": "ERROR", "mensaje": "Usuario/clave erróneo"}
                code = 401
            else:
                # Obtener el hash de la contraseña almacenada
                stored_hash = usuario[0]

                # Verificar la contraseña con el hash almacenado
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    # Si la contraseña es correcta, se almacena la información en la sesión
                    ret = {"status": "OK"}
                    session["usuario"] = username
                    session["perfil"] = usuario[1]  # 'dni' o el campo que desees

                    code = 200
                else:
                    # Si la contraseña no coincide
                    ret = {"status": "ERROR", "mensaje": "Usuario/clave erróneo"}
                    code = 401

        except Exception as e:
            print(f"Excepción al validar al usuario: {e}")
            ret = {"status": "ERROR"}
            code = 500

    else:
        ret = {"status": "Bad request"}
        code = 401

    return json.dumps(ret), code

@app.route("/registro", methods=['POST'])
def registro():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        juego_json = request.json #cambiar juegos
        dni = juego_json.get('dni')
        nombre = juego_json.get('nombre')
        apellido1 = juego_json.get('apellido1')
        apellido2 = juego_json.get('apellido2')
        email = juego_json.get('email')
        passwordd = juego_json.get('passwordd')
        telefono = juego_json.get('telefono')
        fecha_nacimiento = juego_json.get('fecha_nacimiento')
        
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                # Comprobamos si el usuario ya existe en la base de datos por el email
                cursor.execute("SELECT dni FROM usuarios WHERE email = %s", (email,))
                usuario = cursor.fetchone()

                if usuario is None:
                    # Si el usuario no existe, hasheamos la contraseña antes de guardarla
                    hashed_password = bcrypt.hashpw(passwordd.encode('utf-8'), bcrypt.gensalt())

                    # Inserción del nuevo usuario con la contraseña hasheada
                    cursor.execute("""
                        INSERT INTO usuarios (dni, passwordd, email, nombre, apellido1, apellido2, telefono, fecha_nacimiento)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (dni, hashed_password, email, nombre, apellido1, apellido2, telefono, fecha_nacimiento))

                    if cursor.rowcount == 1:
                        conexion.commit()  # Confirmamos la transacción
                        ret = {"status": "OK"}
                        code = 200
                    else:
                        ret = {"status": "ERROR"}
                        code = 500
                else:
                    ret = {"status": "ERROR", "mensaje": "El usuario con ese correo electrónico ya existe"}
                    code = 400  # Código de error 400 para "Bad Request"

            conexion.close()
        except Exception as e:
            print(f"Excepción al registrar al usuario: {e}")
            ret = {"status": "ERROR"}
            code = 500
    else:
        ret = {"status": "Bad request"}
        code = 401

    return json.dumps(ret), code

@app.route("/logout",methods=['GET'])
def logout():
    session.clear()
    return json.dumps({"status":"OK"}),200
