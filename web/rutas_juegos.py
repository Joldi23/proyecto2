from flask import request, jsonify, session, make_response
import json
import decimal
from __main__ import app
import controlador_usuarios
from datetime import datetime
from funciones_auxiliares import Encoder, sanitize_input,validar_session_normal,validar_session_admin
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)



@app.route("/bienvenido", methods=["GET"])
def bienvenido():
    if "usuario" in session:
        try:
            clases_data = controlador_usuarios.obtener_clases()
            if clases_data is None:
                return jsonify({"status": "ERROR", "mensaje": "Error al obtener clases"}), 500

            foto = controlador_usuarios.obtener_foto_usuario(session.get("dni"))
            if foto is None:
                return jsonify({"status": "ERROR", "mensaje": "Error al obtener la foto"}), 500

            return jsonify({
                "status": "OK",
                "usuario": session["usuario"],
                "foto": foto,
                "es_trabajador": session.get("es_trabajador"),
                "clases": clases_data
            }), 200

        except Exception as e:
            app.logger.error(f"Error en la ruta /bienvenido: {e}")
            return jsonify({"status": "ERROR", "mensaje": "Error del servidor"}), 500
    else:
        return jsonify({"status": "ERROR", "mensaje": "No has iniciado sesión."}), 401




@app.route("/clase/<id>",methods=["GET"])
def clase_por_id(id):
    id = sanitize_input(id)
    if isinstance(id, str) and len(id)<64:
        if (validar_session_normal()):
            respuesta,code = controlador_usuarios.obtener_clase_por_id(id)
        else:
            respuesta={"status":"Forbidden"}
            code=403
    else:
        respuesta={"status":"Bad parameters"}
        code=401
    response= make_response(json.dumps(respuesta, cls=Encoder), code)
    return response




# @app.route("/obtener_dni", methods=["GET"])  #BORRAR
# def obtener_dni_endpoint():
#     try:
#         email = session.get("usuario") 

#         if not email:
#             return jsonify({"status": "ERROR", "mensaje": "No se ha iniciado sesión"}), 400

#         resultado = controlador_usuarios.obtener_dni_por_usuario(email)
#         return jsonify(resultado)

#     except Exception as e:
#         print(f"Error en /api/obtener_dni: {e}")
#         return jsonify({"status": "ERROR", "mensaje": "Error interno del servidor"}), 500




@app.route("/agregarclase", methods=["POST"])
def guardar_clase():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        clase_json = request.json
        if "nombre" in clase_json and "capacidad" in clase_json and "horario" in clase_json and "duracion_minutos" in clase_json:
            nombre = sanitize_input(clase_json["nombre"])
            capacidad = clase_json["capacidad"]
            duracion_minutos = clase_json["duracion_minutos"]
            try:
                horario = datetime.strptime(clase_json["horario"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return json.dumps({
                    "status": "Bad request",
                }), 400
                
            usuario = session["usuario"]
            if usuario and isinstance(nombre, str) and isinstance(capacidad, (int, float)) and isinstance(horario, datetime) and isinstance(duracion_minutos, (int, float)) and len(nombre) < 128 and len(str(capacidad)) < 512 and len(str(duracion_minutos)) < 512:     
                if validar_session_admin():
                    respuesta, code = controlador_usuarios.insertar_clase(usuario, nombre, capacidad, horario, duracion_minutos)
                else:
                    respuesta = {"status": "Forbidden"}
                    code = 403
            else:
                respuesta = {"status": "Bad request"}
                code = 401
        else:
            respuesta = {"status": "Bad request"}
            code = 401
    else:
        respuesta = {"status": "Bad request"}
        code = 401
    
    response = make_response(json.dumps(respuesta, cls=Encoder),code)  
    return response

@app.route("/actualizarclase", methods=["PUT"])
def actualizar_clase():
    content_type = request.headers.get('Content-Type')
    
    print(f"Content-Type recibido: {content_type}")
    
    if content_type == 'application/json':
        clase_json = request.json
        if "id_clase" in clase_json and "nombre" in clase_json and "capacidad" in clase_json and "horario" in clase_json and "duracion_minutos" in clase_json:
            id = clase_json["id_clase"]
            nombre = sanitize_input(clase_json["nombre"])
            capacidad = clase_json["capacidad"]
            duracion_minutos = clase_json["duracion_minutos"]
            try:
                horario = datetime.strptime(clase_json["horario"], "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                return json.dumps({"status": "Bad request"}), 400
                
            usuario = session["usuario"]
            if not usuario:
                return json.dumps({"status": "Unauthorized"}), 401
            try:
                id = int(id)
                capacidad = int(capacidad)
                duracion_minutos = int(duracion_minutos)
            except ValueError:
                return json.dumps({"status": "Bad request"}), 400
            if (
                isinstance(id, int) and  
                usuario and 
                isinstance(nombre, str) and 
                isinstance(capacidad, int) and 
                isinstance(horario, datetime) and 
                isinstance(duracion_minutos, int) and 
                len(str(id)) < 10 and  
                len(nombre) < 128 and 
                len(str(capacidad)) < 512 and 
                len(str(duracion_minutos)) < 512
            ):  
                if validar_session_normal():
                    respuesta, code = controlador_usuarios.actualizar_clase(usuario, id, nombre, capacidad, horario, duracion_minutos)
                else:
                    respuesta = {"status": "Forbidden"}
                    code = 403
            else:
                respuesta = {"status": "Bad request"}
                code = 401
        else:
            respuesta = {"status": "Bad request"}
            code = 401
    else:
        respuesta = {"status": "Bad request"}
        code = 401
    
    response = make_response(json.dumps(respuesta, cls=Encoder), code)
    return response





@app.route("/actualizarDA", methods=["PUT"])
def actualizar_usu():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        clase_json = request.json
        if "nombre" in clase_json and "apellido1" in clase_json and "apellido2" in clase_json and "telefono" in clase_json:
            nombre = sanitize_input(clase_json["nombre"])
            apellido1 = sanitize_input(clase_json["apellido1"])
            apellido2 = sanitize_input(clase_json["apellido2"])
            telefono = sanitize_input(clase_json["telefono"])
            num_tarjeta = sanitize_input(clase_json.get("num_tarjeta", ""))
            usuario = session["usuario"]
            if isinstance(nombre, str) and isinstance(apellido1, str) and isinstance(apellido2, str) and telefono.isnumeric() and \
               len(nombre) < 128 and len(apellido1) < 128 and len(apellido2) < 128 and len(telefono) < 10 and \
               (num_tarjeta == "" or (num_tarjeta.isnumeric() and len(num_tarjeta) < 12)):

                telefono = int(telefono)
                
                if validar_session_normal():  
                    respuesta, code = controlador_usuarios.actualizarD(nombre, apellido1, apellido2, telefono, num_tarjeta, usuario)
                else:
                    respuesta = {"status": "Forbidden"}
                    code = 403
            else:
                respuesta = {"status": "Bad request", "message": "Datos no válidos"}
                code = 400
        else:
            respuesta = {"status": "Bad request", "message": "Campos incompletos"}
            code = 400
    else:
        respuesta = {"status": "Bad request", "message": "Content-Type incorrecto"}
        code = 400
    
    response = make_response(json.dumps(respuesta, cls=Encoder), code)
    return response



@app.route("/eliminar/<int:id>", methods=["DELETE"])
def eliminar_clase(id):
    if (validar_session_admin()):
        respuesta,code=controlador_usuarios.eliminar_clase(id)
    else: 
        respuesta={"status":"Forbidden"}
        code=403
    response= make_response(json.dumps(respuesta, cls=Encoder), code)
    return response



@app.route("/datos", methods=["GET"])
def obtener_datos_usuario():
    if "usuario" not in session:
        return jsonify({"error": "No autorizado"}), 403
    usuario = session["usuario"]  # Obtener DNI desde la sesión
    try:
        clase, code = controlador_usuarios.obtener_datos(usuario)
        return jsonify(clase), code
    except ValueError:
        return jsonify({"error": "ID inválido"}), 400
