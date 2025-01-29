from __future__ import print_function
from __main__ import app
from flask import request, jsonify, session
from bd import obtener_conexion
import json
import sys
import bcrypt


@app.route("/login", methods=['POST'])
def login():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        datos_json = request.json
        username = datos_json.get('username')
        password = datos_json.get('password')

        try:
            # Conexión a la base de datos
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                # Buscar el usuario en la base de datos (ahora incluyendo el DNI)
                cursor.execute("SELECT password, email, dni , foto, es_trabajador FROM usuarios WHERE email = %s", (username,))
                usuario = cursor.fetchone()

            conexion.close()

            if usuario is None:
                # Si el usuario no existe
                ret = {"status": "ERROR", "mensaje": "Usuario no encontrado"}
                code = 401
            else:
                # Usuario encontrado, comparar la contraseña
                stored_hash = usuario[0]  # Contraseña hasheada en la base de datos

                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    # Contraseña correcta
                    session["usuario"] = username
                    session["dni"] = usuario[2]
                    session["foto"] = usuario[3]
                    session["es_trabajador"] = usuario[4]
                    ret = {"status": "OK", "mensaje": "Inicio de sesión exitoso"}
                    code = 200
                else:
                    # Contraseña incorrecta
                    ret = {"status": "ERROR", "mensaje": "Contraseña incorrecta"}
                    code = 401
        except Exception as e:
            print(f"Error en el login: {e}")
            ret = {"status": "ERROR", "mensaje": "Error en el servidor"}
            code = 500

        return jsonify(ret), code



@app.route("/registro", methods=['POST'])
def registro():
    content_type = request.headers.get('Content-Type')
    
    if content_type == 'application/json':
        datos_json = request.json

        # Extraer los campos del JSON
        dni = datos_json.get('dni')
        nombre = datos_json.get('nombre')
        apellido1 = datos_json.get('apellido1')
        apellido2 = datos_json.get('apellido2')
        email = datos_json.get('email')
        password = datos_json.get('password')
        telefono = datos_json.get('telefono')
        fecha_nacimiento = datos_json.get('fecha_nacimiento')
        num_tarjeta = datos_json.get('num_tarjeta')
        

        print(f"Datos recibidos: {dni}, {nombre}, {apellido1}, {apellido2}, {email}, {telefono}, {fecha_nacimiento}, {num_tarjeta}")
        
        try:
            # Conectar a la base de datos
            conexion = obtener_conexion()

            if conexion:
                print("Conexión exitosa a la base de datos")
            else:
                print("Error al conectar con la base de datos")
                app.logger.error("Error al conectar con la base de datos")

            with conexion.cursor() as cursor:
                # Comprobamos si el usuario ya existe en la base de datos por el email
                cursor.execute("SELECT dni FROM usuarios WHERE email = %s", (email,))
                usuario = cursor.fetchone()

                if usuario is None:
                    # Si el usuario no existe, hasheamos la contraseña antes de guardarla
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                    # Inserción del nuevo usuario con la contraseña hasheada
                    cursor.execute("""INSERT INTO usuarios (dni, password, email, nombre, apellido1, apellido2, telefono, fecha_nacimiento)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (dni, hashed_password, email, nombre, apellido1, apellido2, telefono, fecha_nacimiento))

                    if num_tarjeta and len(num_tarjeta) > 0:
                        cursor.execute("""INSERT INTO pagos (id_usuario, num_tarjeta)
                        VALUES (%s, %s)""",
                        (dni, num_tarjeta))

                        if cursor.rowcount == 1:
                            conexion.commit()  # Confirmamos la transacción
                            ret = {"status": "OK", "mensaje": "Usuario registrado correctamente"}
                            code = 200
                        else:
                            app.logger.error(f"No se pudo insertar el usuario con email: {email}")
                            ret = {"status": "ERROR", "mensaje": "No se pudo insertar el usuario"}
                            code = 500
                else:
                    app.logger.warning(f"El usuario con el correo electrónico {email} ya existe")
                    ret = {"status": "ERROR", "mensaje": "El usuario con ese correo electrónico ya existe"}
                    code = 400  # Código de error 400 para "Bad Request"

            conexion.close()

        except Exception as e:
            app.logger.error(f"Excepción al registrar al usuario: {e}", exc_info=True)  # Log de excepción
            ret = {"status": "ERROR", "mensaje": str(e)}  # Incluimos la excepción en la respuesta
            code = 500
    else:
        ret = {"status": "Bad request", "mensaje": "El contenido debe ser 'application/json'"}
        code = 400

    # Retornamos la respuesta como JSON
    return jsonify(ret), code

@app.route("/logout",methods=['GET'])
def logout():
    session.clear()
    return json.dumps({"status":"OK"}),200



@app.route("/membresia", methods=["GET"])
def obtener_membresia():
    if "usuario" in session:
        try:
            username = session["usuario"]

            # Conexión a la base de datos
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                # Consulta para obtener los datos del usuario
                query = """
                    SELECT nombre, apellido1, apellido2, email, telefono, fecha_nacimiento, membresia, foto
                    FROM usuarios
                    WHERE email = %s
                """
                cursor.execute(query, (username,))
                usuario = cursor.fetchone()

            conexion.close()

            if usuario:
                # Descomponer los datos
                nombre, apellido1, apellido2, email, telefono, fecha_nacimiento, membresia, foto = usuario

                # Respuesta con los datos
                return jsonify({
                    "status": "OK",
                    "nombre": nombre,
                    "apellido1": apellido1,
                    "apellido2": apellido2,
                    "email": email,
                    "telefono": telefono,
                    "fecha_nacimiento": fecha_nacimiento,
                    "membresia": membresia,
                    "foto":foto
                }), 200
            else:
                return jsonify({"status": "ERROR", "mensaje": "Usuario no encontrado"}), 404

        except Exception as e:
            print(f"Error al obtener datos del usuario: {e}")
            return jsonify({"status": "ERROR", "mensaje": "Error del servidor"}), 500
    else:
        return jsonify({"status": "ERROR", "mensaje": "No has iniciado sesión"}), 401
