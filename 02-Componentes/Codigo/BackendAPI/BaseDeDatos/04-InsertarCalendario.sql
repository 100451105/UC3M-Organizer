-- Procedimiento para inicializar el calendario
DELIMITER //

CREATE PROCEDURE usp_InitializeCalendar()
BEGIN
    DECLARE v_date DATE DEFAULT '2024-01-01';
    DECLARE v_end DATE DEFAULT '2026-12-31';
    DECLARE v_weekday VARCHAR(20);
    DECLARE v_daytype ENUM('Festivo', 'Normal');

    WHILE v_date <= v_end DO
        -- Día de la semana
        SET v_weekday = CASE DAYOFWEEK(v_date)
            WHEN 1 THEN 'Domingo'
            WHEN 2 THEN 'Lunes'
            WHEN 3 THEN 'Martes'
            WHEN 4 THEN 'Miercoles'
            WHEN 5 THEN 'Jueves'
            WHEN 6 THEN 'Viernes'
            WHEN 7 THEN 'Sabado'
        END;

        -- Tipo de día (sábado y domingo son festivo por defecto)
        SET v_daytype = CASE DAYOFWEEK(v_date)
            WHEN 1 THEN 'Festivo'  -- Domingo
            WHEN 7 THEN 'Festivo'  -- Sábado
            ELSE 'Normal'
        END;

        -- Inserción
        INSERT INTO calendar (CalendarDate, DayType, WeekDay, Status)
        VALUES (v_date, v_daytype, v_weekday, 'Libre');

        SET v_date = DATE_ADD(v_date, INTERVAL 1 DAY);
    END WHILE;
END //

DELIMITER ;

-- Ejecutar el procedimiento y borrarlo
CALL usp_InitializeCalendar();
DROP PROCEDURE usp_InitializeCalendar;


-- Inserción de la organización de las actividades de ejemplo del script 01
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-14',2,1);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-21',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-22',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-23',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-24',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-25',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-26',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-27',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-28',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-29',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-30',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-31',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-08-01',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-08-02',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-08-03',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-08-04',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-08-05',2,2);
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-08-06',2,2);