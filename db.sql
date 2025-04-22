CREATE DATABASE IF NOT EXISTS PEPS;
CREATE USER 'user'@'%' IDENTIFIED BY 'userpw';
GRANT ALL PRIVILEGES ON PEPS.* TO 'user'@'%';
FLUSH PRIVILEGES;
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
    perfil BOOLEAN DEFAULT FALSE,
    password VARCHAR(255) NOT NULL,
    foto VARCHAR(255) NULL,
    num_tarjeta VARCHAR(100),
    fechaUltimoAcceso DATE,
    fechaBloqueo DATE,
    numeroAccesosErroneo INTEGER,
    debeCambiarClave BOOLEAN,
    estado VARCHAR (20) DEFAULT 'activo'
);

-- Tabla Clases
CREATE TABLE clases (
    id_clase INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL, 
    id_entrenador VARCHAR(100), 
    capacidad INT NOT NULL, 
    horario DATETIME NOT NULL, 
    duracion_minutos INT NOT NULL, 
    FOREIGN KEY (id_entrenador) REFERENCES usuarios(dni) 
);

-- Tabla Pagos
CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario VARCHAR(100) NOT NULL,
    monto DECIMAL(10, 2) NOT NULL, 
    fecha_pago DATE DEFAULT CURRENT_DATE, 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(dni) 
);


--TRIGGERS
-- SI UN USUARIO AL REGISTRARSE AÑADE UNA TARJETA, SE CREAR UN REGISTRO EN PAGOS
DELIMITER //

CREATE TRIGGER after_insert_update_num_tarjeta
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    -- Verificamos si el nuevo usuario tiene num_tarjeta
    IF NEW.num_tarjeta IS NOT NULL THEN
        INSERT INTO pagos (id_usuario, monto, fecha_pago)
        VALUES (NEW.dni, 0.00, CURRENT_DATE);
    END IF;
END;
//

DELIMITER ;

-- SI UN USUARIO NO PONE LA TARJETA Y DESPUES CUANDO MODIFICA LOS DATOS AÑADE TARJETA, SE CREA REGISTROS EN PAGOS
DELIMITER //

CREATE TRIGGER after_update_num_tarjeta
AFTER UPDATE ON usuarios
FOR EACH ROW
BEGIN
    -- Si antes no tenía tarjeta y ahora sí, se inserta en pagos
    IF OLD.num_tarjeta IS NULL AND NEW.num_tarjeta IS NOT NULL THEN
        INSERT INTO pagos (id_usuario, monto, fecha_pago)
        VALUES (NEW.dni, 0.00, CURRENT_DATE);
    END IF;
END;
//

DELIMITER ;


--INSERT DE UN USUARIO QUE ES TRABAJADOR

INSERT INTO usuarios (dni, nombre, apellido1, apellido2, email, telefono, fecha_nacimiento, password, perfil,estado) 
VALUES ('12345678A', 'Juan', 'Pérez', 'Gómez', 'trabajador1@gmail.com', '600123456', '1990-05-15', '$2b$12$W75ocsoaN8eC62n4rljG4e2L9qwqYhmcxuJbGzvfZ5EfW8CcNISLm', TRUE,'activo');

--la contraseña del usuario es '12345'
