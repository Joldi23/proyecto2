from __future__ import print_function
from __main__ import app
from flask import request, jsonify
from bd import obtener_conexion
import os
import logging
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/var/www/html/fotos' 

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Validar la presencia de parámetros
        if 'fichero' not in request.files or 'dni' not in request.form:
            return jsonify({"status": "ERROR", "message": "Faltan parámetros (fichero o dni)."}), 400

        file = request.files['fichero']
        dni = request.form.get("dni")

        # Validar nombre de archivo
        if file.filename == '':
            return jsonify({"status": "ERROR", "message": "El archivo no tiene nombre."}), 400

        # Validar extensión de archivo
        if not allowed_file(file.filename):
            return jsonify({"status": "ERROR", "message": "Formato de archivo no permitido."}), 400

        # Asegurar nombre de archivo seguro y definir la ruta de subida
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)  # Guardar en /var/www/html/fotos
        logging.info(f'Intentando guardar archivo en: {upload_path}')

        # Crear carpeta si no existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Guardar el archivo
        file.save(upload_path)

        # Guardar la ruta relativa en la base de datos
        relative_path = os.path.join('fotos', filename)  # Ruta relativa desde /var/www/html
        conexion = obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute("UPDATE usuarios SET foto = %s WHERE dni = %s", (relative_path, dni))
                conexion.commit()
                logging.info(f'Foto registrada en la base de datos para el DNI: {dni}')
        except Exception as e:
            logging.error(f"Error al actualizar la base de datos: {e}")
            return jsonify({"status": "ERROR", "message": "Error al guardar en la base de datos."}), 500
        finally:
            conexion.close()

        # Respuesta exitosa
        return jsonify({"status": "OK", "ruta": relative_path}), 200

    except Exception as e:
        logging.error(f"Error al subir el archivo: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@app.route('/update', methods=['PUT'])
def update_photo():
    try:
        # Validar la presencia de parámetros
        if 'fichero' not in request.files or 'dni' not in request.form:
            return jsonify({"status": "ERROR", "message": "Faltan parámetros (fichero o dni)."}), 400

        file = request.files['fichero']
        dni = request.form.get("dni")

        # Validar nombre de archivo
        if file.filename == '':
            return jsonify({"status": "ERROR", "message": "El archivo no tiene nombre."}), 400

        # Validar extensión de archivo
        if not allowed_file(file.filename):
            return jsonify({"status": "ERROR", "message": "Formato de archivo no permitido."}), 400

        # Asegurar nombre de archivo seguro y definir la nueva ruta
        filename = secure_filename(file.filename)
        new_upload_path = os.path.join(UPLOAD_FOLDER, filename)  # Nueva ruta: /var/www/html/fotos
        relative_path = os.path.join('fotos', filename)  # Ruta relativa desde /var/www/html

        # Crear carpeta si no existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Conexión a la base de datos
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Obtener la ruta actual de la foto del usuario
                cursor.execute("SELECT foto FROM usuarios WHERE dni = %s", (dni,))
                result = cursor.fetchone()

                if result and result[0]:  # Si existe una foto registrada
                    old_photo_path = os.path.join('/var/www/html', result[0])  # Ruta completa
                    # Verificar si la ruta de la foto es "/foto/example.png"
                    if result[0] != "foto/example.png":
                        if os.path.exists(old_photo_path):
                            os.remove(old_photo_path)  # Eliminar la foto anterior
                            logging.info(f"Foto antigua eliminada: {old_photo_path}")
                    else:
                        logging.info(f"Foto antigua no eliminada, es la predeterminada: {result[0]}")

                # Guardar la nueva foto en el servidor
                file.save(new_upload_path)
                logging.info(f'Nueva foto guardada en: {new_upload_path}')

                # Actualizar la base de datos con la nueva ruta
                cursor.execute("UPDATE usuarios SET foto = %s WHERE dni = %s", (relative_path, dni))
                conexion.commit()
                logging.info(f'Foto actualizada en la base de datos para el DNI: {dni}')

        except Exception as e:
            logging.error(f"Error en la base de datos: {e}")
            return jsonify({"status": "ERROR", "message": "Error al interactuar con la base de datos."}), 500
        finally:
            conexion.close()

        # Respuesta exitosa
        return jsonify({"status": "OK", "ruta": relative_path}), 200

    except Exception as e:
        logging.error(f"Error al procesar la actualización: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

