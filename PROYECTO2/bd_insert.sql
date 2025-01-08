-- Insertar en Usuarios
INSERT INTO Usuarios (dni, nombre, apellido, email, telefono, fecha_nacimiento, membresia, es_trabajador, descuento_trabajador)
VALUES
(12345, 'Juan', 'Pérez', 'juan.perez@gmail.com', '555-1234', '1990-01-15', TRUE, FALSE, 0.00),
(67890, 'María', 'Gómez', 'maria.gomez@gmail.com', '555-5678', '1985-07-22', TRUE, TRUE, 20.00),
(54321, 'Carlos', 'López', 'carlos.lopez@gmail.com', '555-8765', '1992-03-10', FALSE, TRUE, 15.00),
(98765, 'Ana', 'Martínez', 'ana.martinez@gmail.com', '555-4321', '1995-11-05', TRUE, FALSE, 0.00),
(11223, 'Lucía', 'Fernández', 'lucia.fernandez@gmail.com', '555-6789', '1988-05-30', FALSE, FALSE, 0.00);

-- Insertar en Clases
INSERT INTO Clases (nombre, id_entrenador, capacidad, horario, duracion_minutos)
VALUES
('Yoga', 54321, 20, '2024-01-10 09:00:00', 60),
('Spinning', 67890, 15, '2024-01-10 10:00:00', 45),
('Pilates', 54321, 10, '2024-01-11 08:30:00', 50),
('Zumba', 12345, 25, '2024-01-12 11:00:00', 60),
('Boxeo', 98765, 12, '2024-01-13 18:00:00', 75);

-- Insertar en Pagos
INSERT INTO Pagos (id_usuario, monto, fecha_pago, metodo_pago)
VALUES
(12345, 50.00, '2024-01-01', 'Tarjeta'),
(67890, 40.00, '2024-01-02', 'Efectivo'),
(54321, 30.00, '2024-01-03', 'Transferencia'),
(98765, 60.00, '2024-01-04', 'Tarjeta'),
(11223, 20.00, '2024-01-05', 'Efectivo');

