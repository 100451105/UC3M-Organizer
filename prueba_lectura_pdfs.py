# Read PDFs from a file and extract text from them
from pdfreader import PDFDocument, SimplePDFViewer
import PyPDF2
import os
import re
import pandas as pd
import numpy as np

"""
def get_pdf_text_pdfreader(path):
    fd = open(path, "rb")
    doc = PDFDocument(fd)

    #Caracteristicas del documento
    print(doc.header.version)
    print(doc.metadata)
    print(doc.root.Type)

    #Longitud del documento
    all_pages = [p for p in doc.pages()]


    # Contenido de la primera pagina
    first_page = all_pages[0]
    viewer = SimplePDFViewer(fd)
    viewer.navigate(1)
    viewer.render()
    page_1_canvas = viewer.canvas

    # Parseo de texto
    page_1_split = page_1_canvas.strings

    # Juntar todos los strings en un solo string
    page_1_text = ''.join(page_1_split)
    
    # Buscar un string en el texto
    pos = page_1_text.find('column ')+len('column ')

    # Crear un dataframe vacío
    df = pd.DataFrame(columns=['Semana','Descripcion'])

    # Recoger los datos a partir de la posición del string
    page_1_text = page_1_text[pos:]
    print(page_1_text)


    # Formatear el texto
    while page_1_text.find('  ') != -1:
        page_1_text = page_1_text.replace('  ',' ')
        page_1_text = page_1_text.replace('\n',' ')
        page_1_text = page_1_text.strip()
        print(page_1_text)

    # Asignar los datos al dataframe vacío
    texto = page_1_text.split(' ')
    texto = [x for x in texto if x != ' ']
    print(texto)

    # Ignorar los future warnings de pandas
    pd.options.mode.chained_assignment = None

    i = 0
    while i < len(texto):
        if texto[i].isdigit():
            j = i+1
            while j < len(texto)-1:
                if (texto[j].isdigit() and texto[j+1].isdigit()):
                    break
                elif (texto[j].isdigit() and texto[j+1].isalpha() and texto[j+1][0].isupper()):
                    break
                else:
                    j = j+1
            df = df.append({'Semana': texto[i], 'Descripcion': ' '.join(texto[i+1:j+1])}, ignore_index=True)
            i = j+1
        else:
            i = i+1
    print(df)

"""
def isSemana(texto):
    if texto.isdigit():
        return True
    else:
        return False


def get_pdf_text_pypdf2(path):
    fd = open(path, "rb")
    doc = PyPDF2.PdfReader(fd)
    print(doc.metadata)

    # Crear un dataframe vacío
    df = pd.DataFrame(columns=['Semana','Descripcion'])
    for (i,page) in enumerate(doc.pages):
        #Página 1
        page_i = doc.pages[i]
        page_i_text = page_i.extract_text()[page_i.extract_text().find('column ')+len('column '):]
        print(page_i_text.encode('utf-8'))

        #Formatear el texto
        while page_i_text.find('  ') != -1:
            page_i_text = page_i_text.replace('  ',' ')
            page_i_text = page_i_text.replace('\n','.')
            page_i_text = page_i_text.strip()
            print(page_i_text.encode('utf-8'))

        # Asignar los datos al dataframe vacío
        texto = page_i_text.split(' ')
        texto = [x.replace('.','') for x in texto if x != ' ']
        texto = [x for x in texto if x != '']
        print(texto)

        # Ignorar los future warnings de pandas
        pd.options.mode.chained_assignment = None

        i = 0
        j = 0
        while i < len(texto)-1:
            registration_type_pattern = re.compile(r'[0-9]*-[0-9]*')
            res = registration_type_pattern.fullmatch(texto[i])
            if texto[i].isdigit() or res:
                j = i+1
                while j < len(texto)-1:
                    # Caso de ejemplo 1: dos números seguidos suponen el final de la descripción
                    if (texto[j].isdigit() and texto[j+1].isdigit()):
                        break
                    # Caso de ejemplo 3: un número seguido de una palabra que empieza por mayúscula supone el final de la descripción
                    elif (texto[j].isdigit() and texto[j+1].isalpha() and texto[j+1][0].isupper()):
                        j = j-2
                        break
                    else:
                        j = j+1
                df = df.append({'Semana': texto[i], 'Descripcion': ' '.join(texto[i+1:j+1])}, ignore_index=True)
                i = j+1
            else:
                i = i+1
            
    print(df)
    

if __name__ == '__main__':
    get_pdf_text_pypdf2(os.getcwd() + '\ejemplo.pdf')
    get_pdf_text_pypdf2(os.getcwd() + '\ejemplo3.pdf')
    get_pdf_text_pypdf2(os.getcwd() + '\ejemplo4.pdf')
    get_pdf_text_pypdf2(os.getcwd() + '\ejemplo5.pdf')
    #Ejemplo que explota
    #get_pdf_text_pypdf2(os.getcwd() + '\ejemplo_corrupto.pdf')









