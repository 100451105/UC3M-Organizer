import tabula
import pandas as pd
import os

def extraer_tablas_desde_pdf(pdf_path):
    # Extraer tablas desde el PDF
    dataframes = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    
    # Crear un DataFrame para cada tabla
    tablas = [pd.DataFrame(tabla) for tabla in dataframes]
    # Depuramos las tablas que nos interesa
    tabla = tablas[0]
    for tabla_mala in tablas:
        if tabla_mala.shape[0] < 2 and tabla_mala.shape[0] > 0:
            #Eliminamos tablas con menos de 2 filas
            tabla_mala.reset_index(drop=True, inplace=True)
            tabla_mala.drop(tabla_mala.index,inplace=True)
    tablas = [tabla for tabla in tablas if not tabla.empty]

    # Preprocesado de las tablas

    for tabla in tablas:
        # Es posible que haya caracteres de salto de línea en las tablas (/r o /n)
        tabla.columns = tabla.columns.str.replace('\r', ' ')
        tabla.columns = tabla.columns.str.replace('\n', ' ')
        # Nos interesa las 2 primeras columnas
        tabla.drop(tabla.columns[2:], axis=1, inplace=True)
        tabla.reset_index(drop=True, inplace=True)
        #Modificar el nombre de las columnas
        if tabla.shape[1] == 2:
            tabla.columns = ["Semana", "Actividad"]
        elif tabla.shape[1] == 1:
            tabla.drop(tabla.columns[0], axis=1, inplace=True)
        # Crear una columna al inicio con el código de la asignatura (5 ultimos digitos del nombre del archivo)
        tabla.insert(0, "Codigo_asignatura", pdf_path[-9:-4])
        tabla.reset_index(drop=True, inplace=False)
    tablas = [tabla for tabla in tablas if not tabla.shape[1] == 1]
    for tabla in tablas:
        tabla.dropna(axis=0, inplace=True)
        tabla.reset_index(drop=True, inplace=True)
    
    
    return tablas

def exportar_a_excel(dataframes, excel_path):
    # Exportar los DataFrames a un archivo Excel creando la tabla dentro del excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        dataframes.to_excel(writer, sheet_name='Calendario-Continua-Asignaturas', index=False)

if __name__ == "__main__":
    # REQUISITO: debe tener instalado Java 8 o superior
    os.environ["JAVA_HOME"] = "C:\Program Files (x86)\Java\jre-1.8"
    # Ruta del archivo PDF
    pdf_path = "Dataset/"
    # Dar acceso a los datasets de prueba

    # Extraer tablas desde el PDF y almacenarlas en una lista
    tablas = []
    for file in os.listdir(pdf_path):
        if file.endswith(".pdf"):
            tablas.extend(extraer_tablas_desde_pdf(pdf_path + file))
            print("Importado el archivo: " + file)

    # Juntar todas las tablas en una sola
    for tabla in tablas:
        print(tabla)
        tabla.reset_index(drop=True, inplace=True)
    tabla = pd.concat(tablas)
    tabla.reset_index(drop=True, inplace=True)
    print(tabla)
    
    # Exportar las tablas a distintos archivos csv
    csv_path = "Dataset_Traducido/"
    tabla.to_csv(csv_path + "Dataset_completo.csv", index=False)

    # Exportar las tablas a un archivo Excel
    excel_path = "Deposito_Datasets.xlsx"
    exportar_a_excel(tabla, excel_path)
    

    
    