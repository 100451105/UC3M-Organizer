# Analisis: estructura de carpetas
- Analisis_Externo: contiene el excel del analisis final utilizando los datos procesados.
- Codigo: contiene el código utilizado para extraer y procesar la información recolectada. Esto a su vez se divide en:
    - Pruebas: contiene el código utilizado anteriormente y probado.
    - Final: contiene el código utilizado como versión final para el análisis.
- Datos_De_Prueba: contiene una batería de archivos pdf con los datos utilizados como ejemplo. Estos datos son los calendarios de evaluación continua de multiples asignaturas recolectados de las páginas web oficiales de la UC3M.
- Datos_Procesados: contiene los datos procesados durante y después de ejecutar el código.

## Ejecución
- Requiere tener instalado Java 8 o superior al igual que las librerías de Python indicadas en el código
- Orden de ejecución es el siguiente:
    - Recolector_de_Web.py recoge la información de las distintas asignaturas de la pagina web oficial de la UC3M.
    - pruebaLectura2.py analiza los calendarios de evaluación continua colocados en Datos_De_Prueba para recoger todas las actividades de evaluación continua disponibles para cada codigo de asignatura.
    - Estandarizacion.py junta los dos archivos creados en base a los procesos anteriores, limpia la información y coloca la versión limpia de los datos que se utiliza posteriormente en el Excel de Análisis_Externo.