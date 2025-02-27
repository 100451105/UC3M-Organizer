-- Script de creación de todas las tablas al iniciar la base de datos

-- Creating user, database and access
CREATE DATABASE central_database;
GRANT ALL PRIVILEGES on central_database.* TO 'data_admin'@'%' identified by 'data_password';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY 't2jMtVJOpIxf0Xl47i9ImpwxvXV7U1HM' WITH GRANT OPTION;
FLUSH PRIVILEGES;
USE central_database;


-- user_authorization
CREATE TABLE user_authorization (
    Id INT PRIMARY KEY,
    User NVARCHAR2(100) NOT NULL,
    Password NVARCHAR2(100) NOT NULL
);

-- person
CREATE TABLE person (
    Id INT PRIMARY KEY,
    User NVARCHAR2(100) NOT NULL,
    Type NVARCHAR2(50) NOT NULL CHECK(Type IN ('Profesor','Estudiante','Administrador','Otros')),

    FOREIGN KEY Id REFERENCES user_authorization(Id)
    ON DELETE CASCADE
);

-- subject
CREATE TABLE subject (
    IdSubject INT PRIMARY KEY,
    Credits INT NOT NULL,
    Semester INT NOT NULL CHECK(Semester IN (1,2)),
    Year INT CHECK(Year > 0) NOT NULL,
    IdAdministrator INT,
    FOREIGN KEY IdAdministrator REFERENCES person(Id)
    ON DELETE SET NULL
);

-- personPerSubject
CREATE TABLE personPerSubject (
    IdSubject INT,
    IdPerson INT,
    PRIMARY KEY (IdSubject,IdPerson),
    FOREIGN KEY IdSubject REFERENCES subject(IdSubject)
    ON DELETE CASCADE,
    FOREIGN KEY IdPerson REFERENCES person(IdPerson)
    ON DELETE CASCADE
);

-- activity
CREATE TABLE activity (
    IdActivity INT PRIMARY KEY,
    Description NVARCHAR2(MAX) NOT NULL,
    Type NVARCHAR2(50) CHECK(Type IN ('Examen','Actividad','Laboratorio','Clase','Otros')),
    EstimatedHours INT CHECK(EstimatedHours >= 0) NOT NULL,
    EndOfActivity DATE,
    IdSubject INT NOT NULL,
    FOREIGN KEY IdSubject REFERENCES subject(IdSubject)
    ON DELETE CASCADE
);

-- calendar
CREATE TABLE calendar (
    Day INT PRIMARY KEY,
    DayType NVARCHAR2(50) NOT NULL CHECK(DayType IN ('Festivo','Normal')),
    FreeHours INT NOT NULL CHECK(FreeHours >= 0)
);

-- Examples to test
INSERT INTO user_authorization VALUES (1,'admin','password')
INSERT INTO person VALUES (1,'admin@alumnos.uc3m.es','Estudiante')
INSERT INTO subject VALUES (1,6,1,3,NULL)
INSERT INTO personPerSubject VALUES (1,1)
INSERT INTO activity VALUES (1,'Example Description','Examen',0,'2025-01-12',1)
INSERT INTO calendar VALUES (1,'Normal',0)