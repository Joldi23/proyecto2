from flask import request, jsonify, session
import json
import decimal
from __main__ import app
import controlador_juegos
from bd import obtener_conexion

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)



@app.route("/bienvenido", methods=["GET"])
def bienvenido():
    if "usuario" in session:
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                query = """ SELECT id_clase, nombre, id_entrenador, capacidad, horario, duracion_minutos FROM clases """
                cursor.execute(query)
                clases = cursor.fetchall()

            conexion.close()

            # Construir la respuesta con los datos de las clases
            clases_data = [
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

            return jsonify({
                "status": "OK",
                "usuario": session["usuario"],
                "foto": session["foto"],
                "es_trabajador" :session["es_trabajador"],
                "clases": clases_data
            }), 200

        except Exception as e:
            print(f"Error al obtener las clases: {e}")
            return jsonify({"status": "ERROR", "mensaje": "Error del servidor"}), 500
    else:
        return jsonify({"status": "ERROR", "mensaje": "No has iniciado sesión."}), 401

@app.route("/clase/<id>", methods=["GET"])
def clase_por_id(id):
    try:
        id_int = int(id)
        clase, code = controlador_juegos.obtener_clase_por_id(id_int)
        return json.dumps(clase, cls=Encoder), int(code)
    except ValueError:
        return json.dumps({"error": "ID inválido"}), 400




@app.route("/obtener_dni", methods=["GET"])
def obtener_dni_endpoint():
    try:
        email = session.get("usuario") 

        if not email:
            return jsonify({"status": "ERROR", "mensaje": "No se ha iniciado sesión"}), 400

        resultado = controlador_juegos.obtener_dni_por_usuario(email)
        return jsonify(resultado)

    except Exception as e:
        print(f"Error en /api/obtener_dni: {e}")
        return jsonify({"status": "ERROR", "mensaje": "Error interno del servidor"}), 500



@app.route("/agregarclase", methods=["POST"])
def guardar_clase():
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        try:
            clase_json = request.json
            required_fields = ["dni", "nombre", "capacidad", "horario", "duracion_minutos"]
            for field in required_fields:
                if field not in clase_json:
                    return json.dumps({"status": "Bad request", "message": f"Falta el campo: {field}"}), 400
                
            from datetime import datetime
            try:
                horario = datetime.strptime(clase_json["horario"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return json.dumps({
                    "status": "Bad request",
                    "message": "El campo 'horario' debe estar en formato 'YYYY-MM-DD HH:MM:SS'"
                }), 400
            
            ret, code = controlador_juegos.insertar_clase(
                dni=clase_json["dni"],
                nombre=clase_json["nombre"],
                capacidad=int(clase_json["capacidad"]),
                horario=horario.strftime("%Y-%m-%d %H:%M:%S"),
                duracion_minutos=int(clase_json["duracion_minutos"])
            )
        except Exception as e:
            ret = {"status": "Failure", "message": "Error interno del servidor"}
            code = 500      
    else:
        ret = {"status": "Bad request", "message": "Content-Type debe ser application/json"}
        code = 400

    return json.dumps(ret), code



@app.route("/actualizar/<id_clase>", methods=["PUT"])
def actualizar_clase_por_id(id_clase):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        try:
            clase_json = request.json
            required_fields = ["id_entrenador", "nombre", "capacidad", "horario", "duracion_minutos"]
            for field in required_fields:
                if field not in clase_json:
                    return json.dumps({"status": "Bad request", "message": f"Falta el campo: {field}"}), 400
            from datetime import datetime
            try:
                horario = datetime.strptime(clase_json["horario"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return json.dumps({
                    "status": "Bad request",
                    "message": "El campo 'horario' debe estar en formato 'YYYY-MM-DD HH:MM:SS'"
                }), 400

            ret, code = controlador_juegos.actualizar_clase(
                id_clase=id_clase,
                id_entrenador=clase_json["id_entrenador"],  
                nombre=clase_json["nombre"],
                capacidad=int(clase_json["capacidad"]),
                horario=horario.strftime("%Y-%m-%d %H:%M:%S"),
                duracion_minutos=int(clase_json["duracion_minutos"])
            )
        except Exception as e:
            print(f"Error al procesar la solicitud: {e}")
            ret = {"status": "Failure", "message": "Error interno del servidor"}
            code = 500
    else:
        ret = {"status": "Bad request", "message": "Content-Type debe ser application/json"}
        code = 400

    return json.dumps(ret), code



@app.route("/actualizarD/<dni>", methods=["PUT"])
def actualizarDA(dni):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        try:
            clase_json = request.json

            # Validar campos obligatorios
            required_fields = ["nombre", "apellido1", "apellido2", "email", "telefono"]
            for field in required_fields:
                if field not in clase_json:
                    return json.dumps({"status": "Bad request", "message": f"Falta el campo: {field}"}), 400

            ret, code = controlador_juegos.actualizarD(
                nombre=clase_json["nombre"],
                apellido1=clase_json["apellido1"],
                apellido2=clase_json["apellido2"],
                email=clase_json["email"],
                telefono=clase_json["telefono"],
                dni=dni,
                num_tarjeta=clase_json.get("num_tarjeta")
            )
        except Exception as e:
            print(f"Error al procesar la solicitud: {e}")
            ret = {"status": "Failure", "message": "Error interno del servidor"}
            code = 500
    else:
        ret = {"status": "Bad request", "message": "Content-Type debe ser application/json"}
        code = 400

    return json.dumps(ret), code


@app.route("/eliminar/<id>", methods=["DELETE"])
def eliminar_clase(id):
    ret,code=controlador_juegos.eliminar_clase(id)
    return json.dumps(ret), code



@app.route("/dni/<dni>", methods=["GET"])
def obtenerD(dni):
    try:
        clase, code = controlador_juegos.obtener_datos(dni)
        return json.dumps(clase, cls=Encoder), code 
    except ValueError:
        return json.dumps({"error": "ID inválido"}), 400
