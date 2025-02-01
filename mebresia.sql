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
