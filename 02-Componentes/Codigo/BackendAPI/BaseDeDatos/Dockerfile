FROM mysql:8.0
COPY my.cnf /etc/mysql/conf.d/my.cnf
# Insertar los scripts iniciales
ADD 01-ScriptCreacion.sql /docker-entrypoint-initdb.d/
ADD 02-InsertarAsignaturas.sql /docker-entrypoint-initdb.d/
ADD 03-InsertarActividades.sql /docker-entrypoint-initdb.d/
ADD 04-InsertarCalendario.sql /docker-entrypoint-initdb.d/
# Copia los CSV dentro del contenedor
ADD TestData/*.csv /var/lib/mysql-files/
