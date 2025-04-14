-- Script de creación de todas las tablas al iniciar la base de datos

-- Creating user, database and access

CREATE DATABASE IF NOT EXISTS central_database;
CREATE USER 'data_admin'@'%' IDENTIFIED BY 'q30Gw1nnq560qOlVrWnJ';
GRANT ALL PRIVILEGES on central_database.* TO 'data_admin'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
USE central_database;


-- user_authorization
CREATE TABLE user_authorization (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Username NVARCHAR(100) NOT NULL,
    Password NVARCHAR(100) NOT NULL
);

-- person
CREATE TABLE person (
    Id INT PRIMARY KEY,
    Username NVARCHAR(100) NOT NULL,
    Type ENUM('Profesor','Estudiante','Administrador','Otros') NOT NULL
);
ALTER TABLE person ADD CONSTRAINT fk_person_id FOREIGN KEY (Id) REFERENCES user_authorization(Id) ON DELETE CASCADE;

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
    EstimatedHours INT NOT NULL CHECK(EstimatedHours >= 0),
    EndOfActivity DATE,
    IdSubject INT NOT NULL
);
ALTER TABLE activity ADD CONSTRAINT fk_activity_subjectId FOREIGN KEY (IdSubject) REFERENCES subject(IdSubject) ON DELETE CASCADE;

-- calendar
CREATE TABLE calendar (
    Day INT PRIMARY KEY,
    DayType ENUM('Festivo','Normal') NOT NULL,
    FreeHours INT NOT NULL CHECK(FreeHours >= 0)
);

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
    sai.EndOfActivity,
    sai.SubjectID as FromSubjectID
FROM vPersonSubjectInfo psi
JOIN vSubjectActivityInfo sai ON psi.SubjectID = sai.SubjectID;

-- Store Procedures for create/update operations
DELIMITER //
CREATE PROCEDURE usp_CreateOrUpdateUser(
    IN p_Username NVARCHAR(100), 
    IN p_Type ENUM('Profesor','Estudiante','Administrador','Otros'),
    IN p_Password NVARCHAR(255),
    IN p_Id INT,
    OUT p_newId INT
)
BEGIN
    DECLARE new_Id INT;
    IF p_Id IS NOT NULL AND EXISTS (SELECT 1 FROM user_authorization WHERE Id = p_Id) THEN
        UPDATE user_authorization SET 
            Password = p_Password,
            Username = p_Username
        WHERE Id = p_Id;

        UPDATE person SET 
            Username = p_Username, 
            Type = p_Type 
        WHERE Id = p_Id;
        SET p_newId = p_Id;
    ELSE
        INSERT INTO user_authorization (
            Username, 
            Password
        ) VALUES (
            p_Username, 
            p_Password
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
            EndOfActivity,
            IdSubject
        ) VALUES (
            p_Name, 
            p_Description,
            p_Type,
            p_Hours,
            p_End,
            p_SubjectId
        );
        SET p_newId = LAST_INSERT_ID();
    END IF;
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

    -- Verificar if it is already assigned
    IF NOT EXISTS (
        SELECT 1 FROM personPerSubject 
        WHERE PersonId = p_PersonId AND SubjectId = p_SubjectId
    ) THEN
        INSERT INTO personPerSubject (PersonId, SubjectId) 
        VALUES (p_PersonId, p_SubjectId);
    END IF;
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
DELIMITER ;

-- Examples to test
INSERT INTO user_authorization (Username, Password) VALUES ('admin','password');
INSERT INTO person (Id, Username, Type) VALUES (1,'admin@alumnos.uc3m.es','Estudiante');
INSERT INTO subject (Credits, Semester, Year, Name, IdSubject, IdAdministrator) VALUES (6,1,3,"Test Subject",198237,NULL);
INSERT INTO personPerSubject (IdSubject, IdPerson) VALUES (198237,1);
INSERT INTO activity (Name, Description, Type, EstimatedHours, EndOfActivity, IdSubject) VALUES ('Example Name','Example Description','Examen',0,'2025-01-12',198237);
INSERT INTO calendar (Day, DayType, FreeHours) VALUES (1,'Normal',0);