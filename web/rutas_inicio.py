from __future__ import print_function
from __main__ import app
from flask import request, jsonify, session
from bd import obtener_conexion
import sys
import bcrypt
import traceback
import json
@app.route("/login", methods=['POST'])
def login():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        datos_json = request.json
        username = datos_json.get('username')
        password = datos_json.get('password')

        print(f"📌 Recibida solicitud de login para usuario: {username}", file=sys.stdout)

        try:
            # Conexión a la base de datos
            print("🔄 Intentando conectar a la base de datos...", file=sys.stdout)
            conexion = obtener_conexion()
            
            with conexion.cursor() as cursor:
                print(f"🔍 Buscando usuario en la base de datos: {username}", file=sys.stdout)
                cursor.execute("SELECT password, email, dni, es_trabajador FROM usuarios WHERE email = %s", (username,))
                usuario = cursor.fetchone()
                print(f"✅ Resultado de la consulta SQL: {usuario}", file=sys.stdout)

            conexion.close()
            print("🔒 Conexión a la base de datos cerrada.", file=sys.stdout)

            if usuario is None:
                print("⚠️ Usuario no encontrado.", file=sys.stdout)
                ret = {"status": "ERROR", "mensaje": "Usuario no encontrado"}
                code = 401
            else:
                stored_hash = usuario[0]  
                
                if stored_hash is None:
                    print("⚠️ El usuario no tiene una contraseña registrada.", file=sys.stdout)
                    ret = {"status": "ERROR", "mensaje": "Contraseña no establecida"}
                    code = 401
                else:
                    print(f"🔑 Comparando contraseñas para usuario: {username}", file=sys.stdout)
                    
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                        print("✅ Contraseña correcta.", file=sys.stdout)
                        session["usuario"] = username
                        session["dni"] = usuario[2]
                        session["es_trabajador"] = usuario[3]
                        ret = {"status": "OK", "mensaje": "Inicio de sesión exitoso"}
                        code = 200
                    else:
                        print("❌ Contraseña incorrecta.", file=sys.stdout)
                        ret = {"status": "ERROR", "mensaje": "Contraseña incorrecta"}
                        code = 401
        except Exception as e:
            print(f"🚨 Error en el login: {e}", file=sys.stdout)
            print(traceback.format_exc(), file=sys.stdout)  
            ret = {"status": "ERROR", "mensaje": "Error en el servidor"}
            code = 500

        return jsonify(ret), code



@app.route("/registro", methods=['POST'])
def registro():
    content_type = request.headers.get('Content-Type')
    
    if content_type == 'application/json':
        datos_json = request.json

        dni = datos_json.get('dni')
        nombre = datos_json.get('nombre')
        apellido1 = datos_json.get('apellido1')
        apellido2 = datos_json.get('apellido2')
        email = datos_json.get('email')
        password = datos_json.get('password')
        telefono = datos_json.get('telefono')
        fecha_nacimiento = datos_json.get('fecha_nacimiento')
        num_tarjeta = datos_json.get('num_tarjeta')

        
        num_tarjeta = None if num_tarjeta in [None, "", " "] else str(num_tarjeta)
        membresia = True if num_tarjeta else False

        try:
            if not password:
                return jsonify({"status": "ERROR", "mensaje": "La contraseña es obligatoria"}), 400

            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT dni FROM usuarios WHERE email = %s", (email,))
                usuario = cursor.fetchone()

                if usuario is None:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                    cursor.execute("""
                        INSERT INTO usuarios (dni, password, email, nombre, apellido1, apellido2, telefono, fecha_nacimiento, num_tarjeta, membresia)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (dni, hashed_password, email, nombre, apellido1, apellido2, telefono, fecha_nacimiento, num_tarjeta, membresia))
                    
                    if cursor.rowcount == 1:
                        conexion.commit()
                        ret = {"status": "OK", "mensaje": "Usuario registrado correctamente"}
                        code = 200
                    else:
                        ret = {"status": "ERROR", "mensaje": "No se pudo insertar el usuario"}
                        code = 500
                else:
                    ret = {"status": "ERROR", "mensaje": "El usuario con ese correo electrónico ya existe"}
                    code = 400

            conexion.close()
        except Exception as e:
            ret = {"status": "ERROR", "mensaje": str(e)}
            code = 500
    else:
        ret = {"status": "Bad request", "mensaje": "El contenido debe ser 'application/json'"}
        code = 400

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
                
                query = """
                    SELECT nombre, apellido1, apellido2, email, telefono, fecha_nacimiento, membresia, foto
                    FROM usuarios
                    WHERE email = %s
                """
                cursor.execute(query, (username,))
                usuario = cursor.fetchone()

            conexion.close()

            if usuario:
                
                nombre, apellido1, apellido2, email, telefono, fecha_nacimiento, membresia, foto = usuario

               
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

