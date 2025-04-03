from __future__ import print_function
from __main__ import app
from flask import request,make_response, jsonify, session
import json
import sys
from funciones_auxiliares import Encoder, sanitize_input,delete_session
import controlador_usu

@app.route("/login", methods=['POST'])
def login():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        login_json = request.json
        if "username" in login_json and "password" in login_json:
            username = sanitize_input(login_json['username'])
            password = sanitize_input(login_json['password'])
            if isinstance(username, str) and isinstance(password, str) and len(username) < 50 and len(password) < 50:
                respuesta,code= controlador_usu.login_usuario(username,password)
            else:
                respuesta={"status":"Bad parameters"}
                code=401
        else:
            respuesta={"status":"Bad request"}
            code=401
    else:
        respuesta={"status":"Bad request"}
        code=401
    response= make_response(json.dumps(respuesta, cls=Encoder), code)
    return response


@app.route("/registro", methods=['POST'])
def registro():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        datos_json = request.json
        if "password" in datos_json and "email" in datos_json:
            dni = sanitize_input(datos_json['dni'])
            nombre = sanitize_input(datos_json['nombre'])
            apellido1 = sanitize_input(datos_json['apellido1'])
            apellido2 = sanitize_input(datos_json['apellido2'])  
            username = sanitize_input(datos_json['email'])
            password = sanitize_input(datos_json['password'])
            telefono = sanitize_input(datos_json['telefono'])
            fecha_nacimiento = sanitize_input(datos_json['fecha_nacimiento'])  
            num_tarjeta = sanitize_input(datos_json['num_tarjeta'])

            num_tarjeta = None if num_tarjeta in [None, "", " "] else str(num_tarjeta)
            
            if isinstance(username, str) and isinstance(password, str) and len(username) < 50 and len(password) < 50:
                respuesta, code = controlador_usu.alta_usuario(dni, password, username, nombre, apellido1, apellido2, telefono, fecha_nacimiento, num_tarjeta)

            else:
                respuesta = {"status": "Bad parameters"}
                code = 401
        else:
            respuesta = {"status": "Bad request"}
            code = 400 
    else:
        respuesta = {"status": "Bad request"}
        code = 400  
    response = make_response(json.dumps(respuesta, cls=Encoder), code)
    return response


@app.route("/logout",methods=['GET'])
def logout():
    try:
        delete_session()
        ret={"status":"OK"}
        code=200
    except:
        ret={"status":"ERROR"}
        code=500
    response=make_response(json.dumps(ret),code)
    return response



@app.route("/membresia", methods=["GET"])
def obtener_membresia():
    if "usuario" not in session:
        return jsonify({"status": "ERROR", "mensaje": "No has iniciado sesión"}), 401

    try:
        username = session["usuario"]
        usuario = controlador_usu.obtener_datos_usuario(username)

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
                "foto": foto
            }), 200
        else:
            return jsonify({"status": "ERROR", "mensaje": "Usuario no encontrado"}), 404

    except Exception as e:
        print(f"Error al obtener datos del usuario: {e}")
        return jsonify({"status": "ERROR", "mensaje": "Error del servidor"}), 500