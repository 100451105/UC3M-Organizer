# UC3M-Organizer

El repositorio de GitHub contiene todas las piezas de código y la documentación necesaria relacionada con el proyecto del Trabajo Fin de Grado. Aquí colocaremos un resumen general de todos los aspectos necesarios para replicar este proyecto y la estructura del mismo.

## 1. Estructura del Proyecto
- **01-Analisis**: contiene todo el código, documentos de Excel y datos necesarios que se han utilizado para realizar el análisis inicial del contexto y adquirir los datos necesarios para realizar una estructura básica que posteriormente se necesitará para diseñar los componentes de la aplicación.
- **02-Componentes**: contiene cada uno de los componentes individuales y las pruebas necesarias para verificar su correcto funcionamiento y su interacción dentro de la aplicación.
- **03-Documentación**: contiene la documentación completa del proyecto.

## 2. Manual de instalación
1. **Instalar dependencias**
   1. **Instalación para Análisis**
      1. **Aplicaciones previas a instalar**
         - Instalar Python 3.10.11 o mayor ([Link de la versión 3.10.11](URL "https://www.python.org/downloads/release/python-31011/"))
         - Instalar Java 8 o superior ([Link de descarga de Java](URL "https://www.java.com/es/download/manual.jsp"))
         - Instalar Excel ([Link de información sobre Excel](URL "https://www.microsoft.com/es-es/microsoft-365/excel"))
      2. Instalar `beautifulsoup4` con el comando:
         ```bash
         pip install beautifulsoup4==4.11.1
         ```
      3. Instalar `requests` con el comando:
         ```bash
         pip install requests==2.28.1
         ```
      4. Instalar `pandas` con el comando:
         ```bash
         pip install pandas==2.2.2
         ```
      5. Instalar `tabula-py` con el comando:
         ```bash
         pip install tabula-py==2.9.0
         ```
   2. **Instalación para Componentes**
      1. Instalar **WSL 2** ([Link de tutorial para descargar WSL](URL "https://learn.microsoft.com/es-es/windows/wsl/install"))
      2. Instalar entorno de Docker ([Docker Desktop en Windows](URL "https://docs.docker.com/desktop/setup/install/windows-install/"), [Docker en Linux](URL "https://docs.docker.com/desktop/setup/install/linux/"))
         - Instalar `docker-compose` en caso de no estar incluido

## 3. Manual de ejecución
1. **Ejecución del Análisis**
   1. Abrir terminal y redirigirse a la carpeta del proyecto
   2. Ejecutar en Python los 3 scripts en orden:
      1. `pruebaLectura2.py`  
         (en Windows: `python .\01-Analisis\Codigo\Final\pruebaLectura2.py`)
      2. `Recolector_de_Web.py`  
         (en Windows: `python .\01-Analisis\Codigo\Final\Recolector_de_Web.py`)
      3. `Estandarización.py`  
         (en Windows: `python .\01-Analisis\Codigo\Final\Estandarización.py`)
   3. Para el análisis realizado, abrir:
      ```
      01-Analisis\Analisis_Externo\Análisis.xlsx
      ```
2. **Ejecución de Componentes**
    **Requisitos**: debes iniciar previamente Docker Desktop o el entorno de docker a utilizar.
   1. **Componentes del sistema completo**
      1. Abrir terminal y redirigirse a la carpeta del proyecto
      2. Ir a la carpeta `02-Componentes`
      3. Para lanzar el sistema completo:
         ```bash
         docker-compose -f docker-compose-system.yml up --build -d
         ```
         - Para acceder a la página web, esperar al lanzamiento de todos los contenedores y abrir: `http://localhost:5173/`
      4. Para parar y eliminar los contenedores:
         ```bash
         docker-compose -f docker-compose-system.yml down -v
         ```
   2. **Pruebas de los componentes**
      1. Repetir pasos 2.1.1 y 2.1.2
      2. Para ejecutar los tests:
         ```bash
         docker-compose -f test-execution-docker-compose.yml up --build
         ```
         - Para visualizar los resultados, usar Docker Desktop u otra interfaz de visualización
      3. Para borrar los contenedores de los tests:
         ```bash
         docker-compose -f test-execution-docker-compose.yml down -v
         ```