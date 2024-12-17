from bs4 import BeautifulSoup
import requests
import re
import csv

# Función que recibe la url de una página web y devuelve el contenido de la página (formato html)

def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content.decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    else:
        print("Error al obtener el contenido de la página. Código de error: " + str(response.status_code) + ".")
        return None
    

# Todo el formateado del html que se encuentra se debe limpiar. Para ello, esta función realiza una limpieza de texto general
def buscar_patron(texto,patron):
    # Buscamos el patrón en la lista de textos filtrada
    patron = re.compile(patron, re.UNICODE)
    resultado = patron.search(texto)
    if resultado:
        return resultado.groups()
    else:
        return -1

def format_text(texto, patron):
    texto = texto.replace("\t", "")
    # Dividir el texto por cada salto de línea
    texto = texto.split("\n")
    # Eliminar elementos vacíos de la lista
    texto = list(filter(None, texto))
    texto = list(filter(lambda x: x != " ", texto))
    # Colocar todos los textos de vuelta en un string separados por \n
    texto = "\n".join(texto)
    if patron:
        return buscar_patron(texto,patron)
    else:
        return texto
    

if __name__ == "__main__":
    page = get_html("https://aplicaciones.uc3m.es/consultaHorarios/porPlan.htm?ano=2023&centro=2&plan=489&idioma=es")
    
    # Una vez guardada la pagina se realiza un análisis de qué etiquetas nos interesan:
        # class="asignatura" --> Código de asignatura-Nombre,Créditos
        # class="cuatr" --> Cuatrimestre
        # class="tipoAsig" --> Tipo de asignatura (Obligatoria, Optativa, etc.)
        # class="curso" --> Curso de la asignatura

    # Comenzamos creando una lista con todas las etiquetas que tengan clase asignatura con el formato establecido (utilizamos expresiones regulares)
    asignaturas = page.find_all("li", {"class": "asignatura"})
    
    # Creamos un diccionario para guardar los datos de las asignaturas
    asignaturas_dict = {}
    for asignatura in asignaturas:
        # Descomponemos el texto para adquirir los textos que nos interesan (numero-nombre,créditos) utilizando expresiones regulares
        texto = asignatura.text
        # Limpiar el texto de saltos de línea y espacios
        patron = r'(\d+)-(.+?), (\d+(\.\d+)?) ECTS'
        texto = format_text(texto, patron)
        if texto == -1:
            continue
        codigo = texto[0]
        nombre = texto[1]
        creditos = texto[2]
        # 2a parte: Buscamos la correlación de dicha asignatura con sus respectivos cuatrimestres, tipo de asignatura y curso
        curso = asignatura.find_previous("li", {"class": "curso"})
        texto = curso.text
        texto = format_text(texto, None)
        # Aplicamos 3 patrones distintos para obtener los datos de cuatrimestre, tipo de asignatura y curso:
        # Curso: 1er curso, 2o Curso, 3o Curso, 4o Curso, Curso
        patron = r'(\d+)([a-z]{1,2}) Curso'
        resultado = buscar_patron(texto, patron)
        if resultado == -1:
            patron = r'(\d+)([a-z]{1,2})Curso'
            resultado = buscar_patron(texto, patron)
            if resultado == -1:
                patron = r'(Curso)'
                resultado = buscar_patron(texto, patron)
                curso_buscado = resultado[0]   
            else:
                curso_buscado = resultado[0]
        else:
            curso_buscado = resultado[0] + resultado[1]
        # Tipo de asignatura: Obligatoria, Optativa, Cursos de Humanidades, Formación Básica
        patron = r'(Obligatoria|Optativa|Cursos de Humanidades|Formación Básica)'
        resultado = buscar_patron(texto, patron)
        if resultado == -1:
            tipo_asignatura = "No especificado"
        else:
            tipo_asignatura = resultado[0]
        # Cuatrimestre: 1er cuatrimestre, 2o cuatrimestre
        cuatrimestre = asignatura.find_previous("li", {"class": "cuatr"})
        texto = cuatrimestre.text
        texto = format_text(texto, None)
        patron = r'(1erCuatrimestre|2o Cuatrimestre)'
        resultado = buscar_patron(texto, patron)
        if resultado == -1:
            cuatrimestre = "No especificado"
        else:
            cuatrimestre = resultado[0]
        # Quitar los espacios del cuatrimestre
        cuatrimestre = cuatrimestre.replace(" ", "")
        # Añadimos los datos al diccionario
        asignaturas_dict[codigo] = [curso_buscado, tipo_asignatura, cuatrimestre, nombre, creditos]

    # Una vez tenemos el diccionario con los datos de las asignaturas, procedemos a crear un archivo csv con los datos
    # Para ello, utilizamos la librería csv
    with open("01-Analisis/Datos_Procesados/Asignaturas.csv", "w", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=["Código", "Curso", "Tipo de asignatura", "Cuatrimestre", "Nombre", "Créditos"]).writeheader()
        for codigo, datos in asignaturas_dict.items():
            csv.DictWriter(file, fieldnames=["Código", "Curso", "Tipo de asignatura", "Cuatrimestre", "Nombre", "Créditos"]).writerow({"Código": codigo, "Curso": datos[0], "Tipo de asignatura": datos[1], "Cuatrimestre": datos[2], "Nombre": datos[3], "Créditos": datos[4]})
    
        
