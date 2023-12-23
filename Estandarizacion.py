import pandas


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
    print(tabla.loc[tabla['Codigo_asignatura'] == 15974])
    tabla = tabla.explode('Semana_expandida', ignore_index=True)
    print(tabla)
    tabla.drop('Semana', axis=1, inplace=True)
    tabla.reset_index(drop=True, inplace=True)
    tabla.rename(columns={'Semana_expandida': 'Semana'}, inplace=True)
    tabla = tabla[['Codigo_asignatura', 'Semana', 'Actividad']]
    tabla.reset_index(drop=True, inplace=True)
    # Nota: semana sigue siendo una lista. Para convertirlo a un string, usar:
    print(tabla)
    # Comprobación de rango d-d: buscar valores del código de asignatura 13881
    print(tabla.loc[tabla['Codigo_asignatura'] == 13881])
    # Por último, eliminar filas que contengan valores nulos en la columna 'Semana'
    tabla.dropna(axis=0, inplace=True)
    tabla.reset_index(drop=True, inplace=True)

    # Segundo preprocesado: (pendiente) Asignar a cada código de asignatura el nombre de la asignatura correspondiente

    # Tercer preprocesado: (pendiente) Definir tipo de Actividad (Ejercicio, Práctica, Examen, Laboratorio, Otros)
    

    # Exportar las tablas a distintos archivos csv
    csv_path = "Dataset_Traducido/Dataset_limpio.csv"
    tabla.to_csv(csv_path, index=False)

    # [0-9][0-9][0-9][0-9][0-9]-[a-zA-Z0-9]*,[a-zA-Z0-9]*
