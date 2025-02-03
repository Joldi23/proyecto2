from __future__ import print_function
from __main__ import app
from flask import request, jsonify
from bd import obtener_conexion
import os
import logging
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/var/www/html/fotos' 


logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    try:
        
        if 'fichero' not in request.files or 'dni' not in request.form:
            return jsonify({"status": "ERROR", "message": "Faltan parámetros (fichero o dni)."}), 400

        file = request.files['fichero']
        dni = request.form.get("dni")

        
        if file.filename == '':
            return jsonify({"status": "ERROR", "message": "El archivo no tiene nombre."}), 400

        
        if not allowed_file(file.filename):
            return jsonify({"status": "ERROR", "message": "Formato de archivo no permitido."}), 400

        
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)  
        logging.info(f'Intentando guardar archivo en: {upload_path}')

        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        
        file.save(upload_path)

        
        relative_path = os.path.join('fotos', filename)  
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

        
        return jsonify({"status": "OK", "ruta": relative_path}), 200

    except Exception as e:
        logging.error(f"Error al subir el archivo: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@app.route('/update', methods=['PUT'])
def update_photo():
    try:
        
        if 'fichero' not in request.files or 'dni' not in request.form:
            return jsonify({"status": "ERROR", "message": "Faltan parámetros (fichero o dni)."}), 400

        file = request.files['fichero']
        dni = request.form.get("dni")

        
        if file.filename == '':
            return jsonify({"status": "ERROR", "message": "El archivo no tiene nombre."}), 400

        
        if not allowed_file(file.filename):
            return jsonify({"status": "ERROR", "message": "Formato de archivo no permitido."}), 400

        
        filename = secure_filename(file.filename)
        new_upload_path = os.path.join(UPLOAD_FOLDER, filename)  
        relative_path = os.path.join('fotos', filename)  

        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                
                cursor.execute("SELECT foto FROM usuarios WHERE dni = %s", (dni,))
                result = cursor.fetchone()

                if result and result[0]:  
                    old_photo_path = os.path.join('/var/www/html', result[0])  
                    
                    if result[0] != "foto/example.png":
                        if os.path.exists(old_photo_path):
                            os.remove(old_photo_path)  
                            logging.info(f"Foto antigua eliminada: {old_photo_path}")
                    else:
                        logging.info(f"Foto antigua no eliminada, es la predeterminada: {result[0]}")

                
                file.save(new_upload_path)
                logging.info(f'Nueva foto guardada en: {new_upload_path}')

                
                cursor.execute("UPDATE usuarios SET foto = %s WHERE dni = %s", (relative_path, dni))
                conexion.commit()
                logging.info(f'Foto actualizada en la base de datos para el DNI: {dni}')

        except Exception as e:
            logging.error(f"Error en la base de datos: {e}")
            return jsonify({"status": "ERROR", "message": "Error al interactuar con la base de datos."}), 500
        finally:
            conexion.close()

        
        return jsonify({"status": "OK", "ruta": relative_path}), 200

    except Exception as e:
        logging.error(f"Error al procesar la actualización: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

