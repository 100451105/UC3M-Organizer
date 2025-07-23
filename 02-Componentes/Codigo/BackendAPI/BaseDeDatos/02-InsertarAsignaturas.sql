-- Inicializar asignaturas
START TRANSACTION;

LOAD DATA INFILE '/var/lib/mysql-files/Asignaturas.csv'
INTO TABLE subject
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(IdSubject, Year, Semester, Name, Credits, IdAdministrator);

COMMIT;