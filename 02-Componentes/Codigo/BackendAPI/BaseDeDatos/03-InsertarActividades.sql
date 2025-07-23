-- Inicializar actividades de ejemplo (desde 2024 hasta 2026)
INSERT INTO activity (Name, Description, Type, EstimatedHours, StartOfActivity, Status, Strategy, EndOfActivity, NewEndOfActivity, IdSubject)
VALUES('Examen Final','Examen Final valorado en el 50% de la nota','Examen',40,NULL,'Asignado','Completa','2024-01-15',NULL,13869);

START TRANSACTION;

LOAD DATA INFILE '/var/lib/mysql-files/Actividades.csv'
INTO TABLE activity
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Name, Description, Type, EstimatedHours, StartOfActivity, Status, Strategy, EndOfActivity, NewEndOfActivity, IdSubject);

COMMIT;