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
        mock_conexion.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1  
        mock_connect.return_value = mock_conexion
        

        respuesta, codigo = insertar_clase("12345678", "Yoga", 20, "08:00", 60)

        self.assertEqual(respuesta, {"status": "OK"})
        self.assertEqual(codigo, 200)
        

        mock_cursor.execute.assert_called_once()
        mock_conexion.commit.assert_called_once()
        mock_conexion.close.assert_called_once()
    
    @patch('pymysql.connect')
    def test_insertar_clase_fallida(self, mock_connect):
        """❌ Prueba de inserción fallida"""
        # Configurar el mock de la conexión
        mock_conexion = MagicMock()
        mock_cursor = MagicMock()
        mock_conexion.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0  # Simula que la inserción falló
        mock_connect.return_value = mock_conexion
        
        # Llamar a la función
        respuesta, codigo = insertar_clase("87654321", "Pilates", 15, "10:00", 45)
        
        # Verificar la respuesta esperada
        self.assertEqual(respuesta, {"status": "Failure"})
        self.assertEqual(codigo, 200)
        
        # Verificar que se ejecutó la consulta SQL
        mock_cursor.execute.assert_called_once()
        mock_conexion.commit.assert_called_once()
        mock_conexion.close.assert_called_once()
    
    @patch('pymysql.connect')
    def test_insertar_clase_excepcion(self, mock_connect):
        """⚠️ Prueba de error en la conexión"""
        # Configurar el mock para simular un error
        mock_connect.side_effect = Exception("Error de conexión")
        
        # Llamar a la función
        respuesta, codigo = insertar_clase("11111111", "CrossFit", 10, "12:00", 30)
        
        # Verificar la respuesta esperada
        self.assertEqual(respuesta, {"status": "Failure", "message": "Error interno del servidor"})
        self.assertEqual(codigo, 500)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner, verbosity=2)

