import pandas
import re


# Función para expandir rangos en la columna 'Semanas'. 
    # Si la semana es un número, se devuelve una lista con ese número
    # Si la semana es un rango (1-3), se devuelve una lista con todos los números del rango
    # Si la semana es un enumerado (1,3,5), se devuelve una lista con todos los números del enumerado
    # Si la semana es una fecha (?) (1: 1/10/2020), se devuelve una lista con el primer número (indicativo de la semana)
    # Si la semana no es un número ni un rango, se devuelve una lista vacía (valor no válido)
def expandir_rangos(semana):
    if '-' in semana and semana.replace('-', '').isdigit():
        inicio, fin = map(int, semana.split('-'))
        return list(range(inicio, fin + 1))
    elif ',' in semana and all(map(lambda x: x.isdigit(), semana.split(', '))):
        return list(map(int, semana.split(', ')))
    elif ':' in semana and semana.split(':')[0].isdigit():
        return [int(semana.split(':')[0])]
    elif semana.isdigit():
        return [int(semana)]
    else:
        return []

if __name__ == "__main__":
    # Ruta del csv
    csv_path = "Dataset_Traducido/Dataset_completo.csv"
    # Leer el csv
    tabla = pandas.read_csv(csv_path)
    
    # Primer preprocesado: depuramos el valor de la columna 'Semana'
    tabla['Semana_expandida'] = tabla['Semana'].apply(expandir_rangos)
    tabla = tabla.explode('Semana_expandida', ignore_index=True)
    tabla.drop('Semana', axis=1, inplace=True)
    tabla.reset_index(drop=True, inplace=True)
    tabla.rename(columns={'Semana_expandida': 'Semana'}, inplace=True)
    tabla = tabla[['Codigo_asignatura', 'Semana', 'Actividad']]
    tabla.reset_index(drop=True, inplace=True)
    # Por último, eliminar filas que contengan valores nulos en la columna 'Semana'
    tabla.dropna(axis=0, inplace=True)
    tabla.reset_index(drop=True, inplace=True)
    print("Cleaned the Semana column")

    # Segundo preprocesado: Asignar a cada código de asignatura distintas características (nombre, créditos, etc.)
    asignaturas = pandas.read_csv("Dataset_Traducido/Asignaturas.csv")
    # Juntamos la tabla con la de asignaturas en base al código de asignatura
    asignaturas.rename(columns={'Código': 'Codigo_asignatura'}, inplace=True)
    asignaturas.reset_index(drop=True, inplace=True)
    print("Read the Asignaturas table.")
    tabla = tabla.merge(asignaturas, on='Codigo_asignatura')
    tabla = tabla[['Codigo_asignatura', 'Nombre', 'Créditos', 'Curso', 'Cuatrimestre', 'Tipo de asignatura', 'Semana', 'Actividad']]
    tabla.reset_index(drop=True, inplace=True)
    print("Added the columns from the Asignaturas table to the main table.")

    # Tercer preprocesado: Definir tipo de Actividad (Ejercicio, Práctica, Examen, Laboratorio, Otros)
    # Buscamos dentro de la columna 'Actividad' distintos patrones que nos permitan clasificar las actividades:
        # - Ejercicio: Contiene la palabra 'Ejercicio' o variantes (Ejercicios, Ejercicios de clase, etc.)
        # - Práctica: Contiene la palabra 'Práctica' o variantes (Prácticas, P1,  etc.)
        # - Examen: Contiene la palabra 'Examen' o variantes (Examen, Examen final, etc.)
        # - Laboratorio: Contiene la palabra 'Laboratorio' o variantes (Laboratorio, Laboratorio de prácticas, etc.)
        # - Otros: No contiene ninguna de las palabras anteriores
    # Para ello, primero convertimos todas las actividades a minúsculas y luego aplicamos patrones con expresiones regulares
    tabla_copia = tabla.copy()
    tabla_copia['Actividad'] = tabla_copia['Actividad'].str.lower()
    # Ejercicio
    patron = r'.*ejercicio.*'
    tabla_copia['Actividad'] = tabla_copia['Actividad'].apply(lambda x: 'Ejercicio' if re.match(patron, x) else x)
    # Práctica
    patron = r'.*práctica.*|.*p\d+.*|.*prácticas.*|.*práctico.*|.*proyecto.*'
    tabla_copia['Actividad'] = tabla_copia['Actividad'].apply(lambda x: 'Práctica' if re.match(patron, x) else x)
    # Laboratorio
    patron = r'.*laboratorio.*|.*lab.*'
    tabla_copia['Actividad'] = tabla_copia['Actividad'].apply(lambda x: 'Laboratorio' if re.match(patron, x) else x)
    # Examen
    patron = r'.*examen.*|.*test.*|.*prueba.*|.*control.*'
    tabla_copia['Actividad'] = tabla_copia['Actividad'].apply(lambda x: 'Examen' if re.match(patron, x) else x)
    # Otros
    tabla_copia['Actividad'] = tabla_copia['Actividad'].apply(lambda x: 'Otros' if x not in ['Ejercicio', 'Práctica', 'Laboratorio', 'Examen'] else x)
    # Creamos una columna nueva en la tabla original con los valores de la tabla copia
    tabla['Tipo de actividad'] = tabla_copia['Actividad']
    tabla.reset_index(drop=True, inplace=True)
    print("Categorized the activities.")
    
    # Exportar las tablas a distintos archivos csv
    csv_path = "Dataset_Traducido/Dataset_limpio.csv"
    tabla.to_csv(csv_path, index=False)
    print("Exported the table to the csv file: " + csv_path)

    # [0-9][0-9][0-9][0-9][0-9]-[a-zA-Z0-9]*,[a-zA-Z0-9]*
