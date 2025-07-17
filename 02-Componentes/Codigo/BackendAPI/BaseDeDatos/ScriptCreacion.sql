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
    s.Year
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
            p_SubjectId
        );
        SET p_newId = LAST_INSERT_ID();
    END IF;
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

CREATE PROCEDURE usp_AssignSubjectToUser(
    IN p_PersonId INT, 
    IN p_SubjectId INT
)
BEGIN
    -- Verify user
    IF NOT EXISTS (SELECT 1 FROM person WHERE Id = p_PersonId) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '401';
    END IF;

    -- Verify subject
    IF NOT EXISTS (SELECT 1 FROM subject WHERE IdSubject = p_SubjectId) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '402';
    END IF;

    -- Verify if it is already assigned
    IF NOT EXISTS (
        SELECT 1 FROM personPerSubject 
        WHERE PersonId = p_PersonId AND SubjectId = p_SubjectId
    ) THEN
        INSERT INTO personPerSubject (PersonId, SubjectId) 
        VALUES (p_PersonId, p_SubjectId);
    END IF;
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
END //

DELIMITER //

CREATE PROCEDURE usp_ChangeStatusOfActivity(
    IN p_ActivityId INT, 
    IN p_Status ENUM('Organizar','Confirmar','Sin Asignar','Asignado')
)
BEGIN
    -- Verify activity
    IF NOT EXISTS (SELECT 1 FROM activity WHERE IdActivity = p_ActivityId) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '401';
    END IF;
    UPDATE activity SET 
        Status = p_Status
    WHERE IdActivity = p_ActivityId;
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
INSERT INTO person (Id, Username, Type) VALUES (1,'admin@alumnos.uc3m.es','Estudiante');
INSERT INTO subject (Credits, Semester, Year, Name, IdSubject, IdAdministrator) VALUES (6,1,3,"Test Subject",198237,NULL);
INSERT INTO personPerSubject (IdSubject, IdPerson) VALUES (198237,1);
INSERT INTO activity (Name, Description, Type, EstimatedHours, StartOfActivity, Status, Strategy, EndOfActivity, IdSubject) VALUES ('Example Name','Example Description','Examen',0,'2025-07-21','Asignado','Agresiva','2025-08-05',198237);
INSERT INTO calendar (CalendarDate, DayType, WeekDay, Status) VALUES ('2025-07-14','Normal','Lunes','Libre');
INSERT INTO schedule (CalendarDate, Hours, IdActivity) VALUES ('2025-07-14',2,1);