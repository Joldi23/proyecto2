CREATE DATABASE IF NOT EXISTS PEPS;
USE PEPS;

-- Tabla Usuarios
CREATE TABLE usuarios (
    dni VARCHAR(100) NOT NULL PRIMARY KEY, 
    nombre VARCHAR(100) NOT NULL,
    apellido1 VARCHAR(100) NOT NULL,
    apellido2 VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    fecha_nacimiento DATE,
    fecha_registro DATE DEFAULT CURRENT_DATE,
    membresia BOOLEAN DEFAULT FALSE, 
    es_trabajador BOOLEAN DEFAULT FALSE, 
    descuento_trabajador DECIMAL(5, 2) DEFAULT 0.00,
    password VARCHAR(255) NOT NULL -- Cambié "passwordd" por "password"
);

-- Tabla Clases
CREATE TABLE clases (
    id_clase INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL, 
    id_entrenador VARCHAR(100), 
    capacidad INT NOT NULL, 
    horario DATETIME NOT NULL, 
    duracion_minutos INT NOT NULL, 
    FOREIGN KEY (id_entrenador) REFERENCES usuarios(dni) -- Corregí la referencia a "usuarios"
);

-- Tabla Pagos
CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario VARCHAR(100) NOT NULL,
    num_tarjeta VARCHAR(100),
    monto DECIMAL(10, 2) NOT NULL, 
    fecha_pago DATE DEFAULT CURRENT_DATE, 
    metodo_pago VARCHAR(50) NOT NULL, 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(dni) -- Corregí la referencia a "usuarios"
);
