CREATE DATABASE IF NOT EXISTS PEPS;
USE PEPS;

-- Tabla Usuarios
CREATE TABLE usuarios (
    dni INT NOT NULL PRIMARY KEY, -- Corregido: Eliminar VARCHAR
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    fecha_nacimiento DATE,
    fecha_registro DATE DEFAULT CURRENT_DATE,
    membresia BOOLEAN DEFAULT FALSE, -- Indica si tiene membresía
    es_trabajador BOOLEAN DEFAULT FALSE, -- Indica si es trabajador
    descuento_trabajador DECIMAL(5, 2) DEFAULT 0.00,
    passwordd VARCHAR(255) NOT NULL
);

-- Tabla Clases
CREATE TABLE clases (
    id_clase INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL, -- Ejemplo: Yoga, Spinning
    id_entrenador INT, -- Relacionado con un entrenador
    capacidad INT NOT NULL, -- Número máximo de participantes
    horario DATETIME NOT NULL, -- Fecha y hora de la clase
    duracion_minutos INT NOT NULL, -- Duración en minutos
    FOREIGN KEY (id_entrenador) REFERENCES Usuarios(dni) -- Relación con Usuarios
);

-- Tabla Pagos
CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL, -- Relacionado con un usuario (cliente)
    monto DECIMAL(10, 2) NOT NULL, -- Monto del pago
    fecha_pago DATE DEFAULT CURRENT_DATE, -- Fecha del pago
    metodo_pago VARCHAR(50) NOT NULL, -- Ejemplo: Tarjeta, Efectivo, Transferencia
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(dni) -- Relación con Usuarios
);

