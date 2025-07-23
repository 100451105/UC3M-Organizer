-- Script de creación de todas las tablas al iniciar la base de datos

-- Creating user, database and access

CREATE DATABASE IF NOT EXISTS central_database;
CREATE USER 'data_admin'@'%' IDENTIFIED BY 'q30Gw1nnq560qOlVrWnJ';
GRANT ALL PRIVILEGES on central_database.* TO 'data_admin'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
USE central_database;

-- Set UTC timezone
SET time_zone = '+00:00';


-- user_authorization
CREATE TABLE user_authorization (
    Id INT AUTO_INCREMENT,
    Username NVARCHAR(100),
    Password NVARCHAR(100) NOT NULL,
    SeeAllSubjects BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_user_auth PRIMARY KEY (Id, Username)
);

-- person
CREATE TABLE person (
    Id INT,
    Username NVARCHAR(100),
    Type ENUM('Profesor','Estudiante','Administrador','Otros') NOT NULL,
    CONSTRAINT pk_person PRIMARY KEY (Id, Username)
);
ALTER TABLE person ADD CONSTRAINT fk_person_id_username FOREIGN KEY (Id, Username) REFERENCES user_authorization(Id, Username) ON DELETE CASCADE;

-- subject
CREATE TABLE subject (
    IdSubject INT PRIMARY KEY,
    Name NVARCHAR(1024) NOT NULL,
    Credits INT NOT NULL,
    Semester INT NOT NULL CHECK(Semester IN (1,2)),
    Year INT NOT NULL CHECK(Year > 0),
    IdAdministrator INT
);
ALTER TABLE subject ADD CONSTRAINT fk_subject_adminId FOREIGN KEY (IdAdministrator) REFERENCES person(Id) ON DELETE SET NULL;

-- personPerSubject
CREATE TABLE personPerSubject (
    IdSubject INT,
    IdPerson INT,
    CONSTRAINT pk_pps PRIMARY KEY (IdSubject,IdPerson)
);
ALTER TABLE personPerSubject ADD CONSTRAINT fk_pps_subjectId FOREIGN KEY (IdSubject) REFERENCES subject(IdSubject) ON DELETE CASCADE;
ALTER TABLE personPerSubject ADD CONSTRAINT fk_pps_personId FOREIGN KEY (IdPerson) REFERENCES person(Id) ON DELETE CASCADE;

-- activity
CREATE TABLE activity (
    IdActivity INT AUTO_INCREMENT PRIMARY KEY,
    Name NVARCHAR(1024) NOT NULL,
    Description NVARCHAR(1024) NOT NULL,
    Type ENUM('Examen','Actividad','Laboratorio','Clase','Otros') NOT NULL,
    StartOfActivity DATE,
    Status ENUM('Organizar','Confirmar','Sin Asignar','Asignado') NOT NULL,
    Strategy ENUM('Agresiva','Calmada','Completa'),
    EstimatedHours INT NOT NULL CHECK(EstimatedHours >= 0),
    EndOfActivity DATE,
    NewEndOfActivity DATE,
    IdSubject INT NOT NULL
);
ALTER TABLE activity ADD CONSTRAINT fk_activity_subjectId FOREIGN KEY (IdSubject) REFERENCES subject(IdSubject) ON DELETE CASCADE;

-- calendar
CREATE TABLE calendar (
    CalendarDate DATE PRIMARY KEY,
    DayType ENUM('Festivo','Normal') NOT NULL,
    WeekDay ENUM('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo') NOT NULL,
    Status ENUM('Ocupado','Libre') NOT NULL
);

-- schedule
CREATE TABLE schedule (
    CalendarDate DATE,
    Hours INT NOT NULL CHECK(Hours >= 1),
    IdActivity INT,
    CONSTRAINT pk_pps PRIMARY KEY (CalendarDate,IdActivity)
);
ALTER TABLE schedule ADD CONSTRAINT fk_schedule_activityId FOREIGN KEY (IdActivity) REFERENCES activity(IdActivity) ON DELETE CASCADE;
ALTER TABLE schedule ADD CONSTRAINT fk_schedule_calendarDate FOREIGN KEY (CalendarDate) REFERENCES calendar(CalendarDate) ON DELETE CASCADE;

-- Views for different optimized searchs
CREATE VIEW vPersonSubjectInfo AS
SELECT 
    p.Id AS UserID, 
    p.Username, 
    p.Type AS UserType, 
    s.IdSubject AS SubjectID,
    s.Name AS SubjectName, 
    s.Credits AS SubjectCredits, 
    s.Semester,
    s.Year,
    s.IdAdministrator as AdministratorID
FROM personPerSubject pps
JOIN person p ON pps.IdPerson = p.Id
JOIN subject s ON pps.IdSubject = s.IdSubject;

CREATE VIEW vSubjectActivityInfo AS
SELECT 
    a.IdActivity AS ActivityID, 
    a.Name AS ActivityName,
    a.Type AS ActivityType,
    a.Description,
    a.EstimatedHours,
    a.StartOfActivity,
    a.Status,
    a.Strategy,
    a.EndOfActivity,
    a.NewEndOfActivity,
    a.IdSubject AS SubjectID,
    s.Name AS SubjectName, 
    s.Credits AS SubjectCredits, 
    s.Semester,
    s.Year
FROM activity a
JOIN subject s ON a.IdSubject = s.IdSubject;

CREATE VIEW vUserInterestedActivities AS
SELECT 
    psi.UserID, 
    psi.Username, 
    sai.ActivityID, 
    sai.ActivityName, 
    sai.ActivityType,
    sai.Description, 
    sai.EstimatedHours,
    sai.StartOfActivity,
    sai.EndOfActivity,
    sai.SubjectID as SubjectID,
    sai.SubjectName as SubjectName
FROM vPersonSubjectInfo psi
JOIN vSubjectActivityInfo sai ON psi.SubjectID = sai.SubjectID;

CREATE VIEW vActivitiesPerDay AS
SELECT
    c.CalendarDate,
    c.DayType,
    c.WeekDay,
    c.Status,
    CONCAT('[',
        GROUP_CONCAT(
            JSON_OBJECT(
                'Activity', s.IdActivity,
                'ActivityName', a.ActivityName,
                'Hours', s.Hours,
                'Subject', a.SubjectID,
                'SubjectName', a.SubjectName
            )
        ),
    ']') AS Activities
FROM
    calendar c
LEFT JOIN schedule s ON c.CalendarDate = s.CalendarDate
LEFT JOIN vSubjectActivityInfo a ON s.IdActivity = a.ActivityID AND a.Status = 'Asignado'
GROUP BY
    c.CalendarDate, c.DayType, c.WeekDay, c.Status;

CREATE VIEW vPendingActivitiesInformation AS
SELECT
    a.IdActivity AS ActivityID,
    a.Name AS ActivityName,
    a.StartOfActivity,
    a.EndOfActivity,
    a.NewEndOfActivity,
    s.IdSubject AS SubjectID,
    s.Name AS SubjectName,
    s.IdAdministrator AS CoordinatorId,
    (
        SELECT 
            CONCAT('[', GROUP_CONCAT(
                JSON_OBJECT(
                    'day', sc.CalendarDate,
                    'hours', sc.Hours,
                    'dayType', c.DayType
                )
                ORDER BY sc.CalendarDate
            ), ']')
        FROM schedule sc
        JOIN calendar c ON sc.CalendarDate = c.CalendarDate
        WHERE sc.IdActivity = a.IdActivity
    ) AS ScheduleJSON
FROM subject s
JOIN activity a ON s.IdSubject = a.IdSubject
WHERE a.Status = 'Confirmar';



-- Store Procedures for create/update operations
DELIMITER //
CREATE PROCEDURE usp_CreateOrUpdateUser(
    IN p_Username NVARCHAR(100), 
    IN p_Type ENUM('Profesor','Estudiante','Administrador','Otros'),
    IN p_Password NVARCHAR(255),
    IN p_SeeAllSubjects BOOLEAN,
    IN p_Id INT,
    OUT p_newId INT
)
BEGIN
    DECLARE new_Id INT;
    IF p_Id IS NOT NULL AND EXISTS (SELECT 1 FROM user_authorization WHERE Id = p_Id) THEN
        UPDATE user_authorization SET 
            Password = p_Password,
            SeeAllSubjects = p_SeeAllSubjects
        WHERE Id = p_Id;

        UPDATE person SET
            Type = p_Type
        WHERE Id = p_Id;
        SET p_newId = p_Id;
    ELSE
        -- Check if the username already exists
        IF EXISTS (SELECT 1 FROM user_authorization WHERE Username = p_Username) THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = '401';
        END IF;
        INSERT INTO user_authorization (
            Username, 
            Password,
            SeeAllSubjects
        ) VALUES (
            p_Username, 
            p_Password,
            0
        );
        SET p_newId = LAST_INSERT_ID();
        INSERT INTO person (
            Id, 
            Username, 
            Type
        ) VALUES (
            p_newId, 
            p_Username, 
            p_Type
        );
    END IF;
END //


CREATE PROCEDURE usp_CreateOrUpdateSubject(
    IN p_Credits INT, 
    IN p_Semester INT,
    IN p_Year INT,
    IN p_Name NVARCHAR(1024),
    IN p_IdSubject INT,
    OUT p_newIdSubject INT
)
BEGIN
    IF p_IdSubject IS NOT NULL AND EXISTS (SELECT 1 FROM subject WHERE IdSubject = p_IdSubject) THEN
        UPDATE subject SET 
            Credits = p_Credits, 
            Semester = p_Semester,
            Year = p_Year,
            Name = p_Name
        WHERE IdSubject = p_IdSubject;
        SET p_newIdSubject = p_IdSubject;
    ELSE
        INSERT INTO subject (
            Credits, 
            Semester,
            Year,
            IdSubject,
            Name,
            IdAdministrator
        ) VALUES (
            p_Credits, 
            p_Semester,
            p_Year,
            p_IdSubject,
            p_Name,
            NULL
        );
        SET p_newIdSubject = p_IdSubject;
    END IF;
END //

CREATE PROCEDURE usp_CreateOrUpdateActivity(
    IN p_Name NVARCHAR(100), 
    IN p_Description NVARCHAR(1024),
    IN p_Type ENUM('Examen','Actividad','Laboratorio','Clase','Otros'),
    IN p_Hours INT,
    IN p_SubjectId INT,
    IN p_End DATE,
    IN p_Start DATE,
    IN p_Strategy ENUM('Agresiva','Calmada','Completa'),
    IN p_Id INT,
    OUT p_newId INT
)
BEGIN
    IF p_Id IS NOT NULL AND EXISTS (SELECT 1 FROM activity WHERE IdActivity = p_Id) THEN
        UPDATE activity SET 
            Name = p_Name, 
            Description = p_Description,
            Type = p_Type,
            EstimatedHours = p_Hours,
            StartOfActivity = p_Start,
            Strategy = p_Strategy,
            EndOfActivity = p_End,
            IdSubject = p_SubjectId
        WHERE IdActivity = p_Id;
        SET p_newId = p_Id;
    ELSE
        INSERT INTO activity (
            Name, 
            Description, 
            Type,
            EstimatedHours,
            StartOfActivity,
            Status,
            Strategy,
            EndOfActivity,
            NewEndOfActivity,
            IdSubject
        ) VALUES (
            p_Name, 
            p_Description,
            p_Type,
            p_Hours,
            p_Start,
            'Organizar',
            p_Strategy,
            p_End,
            NULL,
            p_SubjectId
        );
        SET p_newId = LAST_INSERT_ID();
    END IF;

    DELETE FROM schedule WHERE IdActivity = p_newId;
END //

DELIMITER //

CREATE PROCEDURE usp_CreateOrUpdateCalendarDays(
    IN p_Calendar JSON
)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_CalendarDate DATE;
    DECLARE v_DayType ENUM('Festivo','Normal');
    DECLARE v_WeekDay ENUM('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo');
    DECLARE v_Status ENUM('Ocupado','Libre');
    -- Collection of JSON input
    DECLARE cur CURSOR FOR 
        SELECT 
            CAST(JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.calendarDate')) AS DATE) AS CalendarDate,
            JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.dayType')) AS DayType,
            JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.weekDay')) AS WeekDay,
            JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.status')) AS Status
        FROM JSON_TABLE(p_Calendar, "$[*]"
            COLUMNS (
                value JSON PATH "$"
            )
        ) u;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_CalendarDate, v_DayType, v_WeekDay, v_Status;
        IF done THEN
            LEAVE read_loop;
        END IF;
        -- Insertion of day in the calendar
        INSERT INTO calendar (CalendarDate, DayType, WeekDay, Status)
        VALUES (v_CalendarDate, v_DayType, v_WeekDay, v_Status)
        ON DUPLICATE KEY UPDATE
            CalendarDate = VALUES(CalendarDate),
            DayType = VALUES(DayType),
            WeekDay = VALUES(WeekDay),
            Status = VALUES(Status);

    END LOOP;

    CLOSE cur;
END //

DELIMITER //

CREATE PROCEDURE usp_AssignOrUnassignUsersToSubject(
    IN p_SubjectId INT,
    IN p_Users JSON
)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_UserId INT;
    DECLARE v_Assigned BOOLEAN;
    DECLARE v_AssignedStr NVARCHAR(10);

    DECLARE cur CURSOR FOR 
        SELECT 
            CAST(JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.userId')) AS UNSIGNED) AS UserId,
            JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.assigned')) AS AssignedStr
        FROM JSON_TABLE(p_Users, "$[*]"
            COLUMNS (
                value JSON PATH "$"
            )
        ) u;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    IF NOT EXISTS (SELECT 1 FROM subject WHERE IdSubject = p_SubjectId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '401'; -- Subject not found
    END IF;

    -- Verificar existencia de todos los usuarios
    IF (
        SELECT COUNT(*) FROM (
            SELECT JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.userId')) AS UserId
            FROM JSON_TABLE(p_Users, "$.users[*]"
                COLUMNS (
                    value JSON PATH "$"
                )
            ) u
            LEFT JOIN person p ON p.Id = JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.userId'))
            WHERE p.Id IS NULL
        ) AS MissingUsers
    ) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '402'; -- Some users not found
    END IF;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_UserId, v_AssignedStr;
        SET v_Assigned = (v_AssignedStr = 'true');
        IF done THEN
            LEAVE read_loop;
        END IF;

        IF v_Assigned THEN
            -- Insert only if not exists
            INSERT IGNORE INTO personPerSubject (IdSubject, IdPerson)
            VALUES (p_SubjectId, v_UserId);
        ELSE
            -- Remove the assignment if exists
            DELETE FROM personPerSubject
            WHERE IdSubject = p_SubjectId AND IdPerson = v_UserId;
        END IF;

    END LOOP;
    CLOSE cur;
END //

DELIMITER //

CREATE PROCEDURE usp_ChangeSubjectVisionOfUser(
    IN p_Username INT, 
    IN p_SeeAllSubjects BOOLEAN
)
BEGIN
    -- Verify user
    IF NOT EXISTS (SELECT 1 FROM person WHERE Username = p_Username) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '401';
    END IF;
    UPDATE user_authorization SET 
        SeeAllSubjects = p_SeeAllSubjects
    WHERE Username = p_Username;
END //

DELIMITER //

CREATE PROCEDURE usp_AssignCoordinatorToSubject(
    IN p_SubjectId INT, 
    IN p_CoordinatorId INT
)
BEGIN
    -- Verify subject
    IF NOT EXISTS (SELECT 1 FROM subject WHERE IdSubject = p_SubjectId) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '401';
    END IF;
    UPDATE subject SET 
        IdAdministrator = p_CoordinatorId 
    WHERE IdSubject = p_SubjectId;
    IF NOT EXISTS (SELECT 1 FROM personPerSubject WHERE IdSubject = p_SubjectId AND IdPerson = p_CoordinatorId) THEN
        INSERT INTO personPerSubject (IdPerson, IdSubject) 
        VALUES (p_CoordinatorId, p_SubjectId);
    END IF;
END //

DELIMITER //

CREATE PROCEDURE usp_ChangeStatusOfActivity(
    IN p_ActivityId INT, 
    IN p_Status ENUM('Organizar','Confirmar','Sin Asignar','Asignado'),
    IN p_NewEndDate DATE
)
BEGIN
    DECLARE current_status VARCHAR(20);
    -- Verify activity
    IF NOT EXISTS (SELECT 1 FROM activity WHERE IdActivity = p_ActivityId) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '401';
    END IF;
    IF p_Status = 'Asignado' THEN
        
        SELECT Status INTO current_status 
        FROM activity 
        WHERE IdActivity = p_ActivityId;

        IF current_status != 'Confirmar' THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = '402';
        END IF;
        UPDATE activity SET 
            Status = p_Status,
            EndOfActivity = NewEndOfActivity,
            NewEndOfActivity = NULL
        WHERE IdActivity = p_ActivityId;
    END IF;
    IF p_Status = 'Confirmar' THEN
        UPDATE activity SET 
            Status = p_Status,
            NewEndOfActivity = p_NewEndDate
        WHERE IdActivity = p_ActivityId;
    ELSE
        UPDATE activity SET 
            Status = p_Status
        WHERE IdActivity = p_ActivityId;
    END IF;
END //

CREATE PROCEDURE usp_AssignActivityToDay(
    IN p_Schedule JSON
)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_CalendarDate DATE;
    DECLARE v_Hours INT;
    DECLARE v_IdActivity INT;
    -- Collection of JSON input
    DECLARE cur CURSOR FOR 
        SELECT 
            CAST(JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.calendarDate')) AS DATE) AS CalendarDate,
            CAST(JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.hours')) AS UNSIGNED) AS Hours,
            CAST(JSON_UNQUOTE(JSON_EXTRACT(u.value, '$.activityId')) AS UNSIGNED) AS IdActivity
        FROM JSON_TABLE(p_Schedule, "$[*]"
            COLUMNS (
                value JSON PATH "$"
            )
        ) u;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_CalendarDate, v_Hours, v_IdActivity;
        IF done THEN
            LEAVE read_loop;
        END IF;
        -- Verify activity
        IF NOT EXISTS (SELECT 1 FROM activity WHERE IdActivity = v_IdActivity) THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = '401';
        END IF;
        -- Verify activity
        IF NOT EXISTS (SELECT 1 FROM calendar WHERE CalendarDate = v_CalendarDate) THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = '402';
        END IF;
        -- Insertion of day in the calendar
        INSERT INTO schedule (CalendarDate, Hours, IdActivity)
        VALUES (v_CalendarDate, v_Hours, v_IdActivity)
        ON DUPLICATE KEY UPDATE
            Hours = VALUES(Hours);

    END LOOP;

    CLOSE cur;
END //
DELIMITER ;

-- Examples to test
INSERT INTO user_authorization (Username, Password) VALUES ('admin@alumnos.uc3m.es','password');
INSERT INTO person (Id, Username, Type) VALUES (1,'admin@alumnos.uc3m.es','Administrador');
INSERT INTO user_authorization (Username, Password) VALUES ('test@profesor.uc3m.es','password');
INSERT INTO person (Id, Username, Type) VALUES (2,'test@profesor.uc3m.es','Profesor');
INSERT INTO subject (Credits, Semester, Year, Name, IdSubject, IdAdministrator) VALUES (6,1,3,"Test Subject",198237,1);
INSERT INTO personPerSubject (IdSubject, IdPerson) VALUES (198237,1);
INSERT INTO personPerSubject (IdSubject, IdPerson) VALUES (198237,2);
INSERT INTO activity (Name, Description, Type, EstimatedHours, StartOfActivity, Status, Strategy, EndOfActivity, NewEndOfActivity, IdSubject) VALUES ('Example Name','Example Description','Examen',16,'2025-07-01','Asignado','Agresiva','2025-07-15',NULL,198237);
INSERT INTO activity (Name, Description, Type, EstimatedHours, StartOfActivity, Status, Strategy, EndOfActivity, NewEndOfActivity, IdSubject) VALUES ('Example Name','Example Description','Examen',34,'2025-07-21','Confirmar','Agresiva','2025-08-05','2025-08-06',198237);


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

        -- Tipo de día (sábado y domingo = Festivo)
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

-- Ejecutar el procedimiento
CALL usp_InitializeCalendar();
DROP PROCEDURE usp_InitializeCalendar;

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
