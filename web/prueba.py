import unittest
from unittest.mock import patch, MagicMock
import pymysql
from controlador_usuarios import insertar_clase  

class TestInsertarClase(unittest.TestCase):
    @patch('pymysql.connect')
    def test_insertar_clase_exitosa(self, mock_connect):
        """✅ Prueba de inserción exitosa"""

        mock_conexion = MagicMock()
        mock_cursor = MagicMock()

        # Configuración de mocks
        mock_conexion.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_cursor.fetchone.return_value = ('12345678',)  # Simula que el SELECT devuelve un dni válido

        mock_connect.return_value = mock_conexion

        # Ejecutar la función
        respuesta, codigo = insertar_clase("12345678", "Yoga", 20, "08:00", 60)

        # Verificar resultado
        self.assertEqual(respuesta, {"status": "OK"})
        self.assertEqual(codigo, 200)

        # Verificar llamadas SQL
        mock_cursor.execute.assert_any_call(
            'SELECT dni FROM usuarios WHERE email = %s', ('12345678',)
        )
        mock_cursor.execute.assert_any_call(
            'INSERT INTO clases (id_entrenador, nombre, capacidad, horario, duracion_minutos) VALUES (%s, %s, %s, %s, %s)',
            ('12345678', 'Yoga', 20, '08:00', 60)
        )

        mock_conexion.commit.assert_called_once()
        mock_conexion.close.assert_called_once()

    @patch('pymysql.connect')
    def test_insertar_clase_fallida(self, mock_connect):
        """❌ Prueba de inserción fallida"""

        mock_conexion = MagicMock()
        mock_cursor = MagicMock()
        mock_conexion.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0
        mock_cursor.fetchone.return_value = ('87654321',)

        mock_connect.return_value = mock_conexion

        respuesta, codigo = insertar_clase("87654321", "Pilates", 15, "10:00", 45)

        self.assertEqual(respuesta, {"status": "Failure"})
        self.assertEqual(codigo, 200)

        mock_conexion.commit.assert_called_once()
        mock_conexion.close.assert_called_once()

    @patch('pymysql.connect')
    def test_insertar_clase_excepcion(self, mock_connect):
        """⚠️ Prueba de error en la conexión"""

        mock_connect.side_effect = Exception("Error de conexión")

        respuesta, codigo = insertar_clase("11111111", "CrossFit", 10, "12:00", 30)

        self.assertEqual(respuesta, {"status": "Failure", "message": "Error interno del servidor"})
        self.assertEqual(codigo, 500)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner, verbosity=2)
