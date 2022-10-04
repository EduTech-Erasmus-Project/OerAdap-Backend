# OerAdap-Backend
Backend Adaptador de Objetos de aprendizaje

## Variables de entorno
Crear un archivo .env en la raiz del proyecto 

```.env
SECRET_KEY=<Secret Key>
DEBUG=True
PROD=False
DB_NAME=<Database name>
DB_USER=<Database user>
DB_PASSWORD=<Database password>
DB_HOST=<Database host>
DB_PORT=<Database port>
MJ_APIKEY_PUBLIC=<mailjet api key public server email>
MJ_APIKEY_PRIVATE=<email registered in mailjet server email>
API_EMAIL=<email registered in mailjet_server email>
API_NAME=EduTech
```

## Instalación de librerías

En la carpeta requirements se encuentran las librerias para desarrollo en windows y producción en linux 

```console
> pip install -r requirements/dev.txt
```

## Ejecución de proyecto 

Para la ejecucucion del proyecto situarse a la altura del archivo manage.py

```console
> python manage.py makemigrations
```

```console
> python manage.py migrate
```

```console
> python manage.py runserver
```

## wkhtmltopdf y wkhtmltoimage en windows 

Instalación de la librería wkhtmltopdf y wkhtmltoimage en windows
 
Para descargar la librería en Windows descarga del enlace https://wkhtmltopdf.org/downloads.html 

Cuando se instale agregar la ruta de instalación y la carpeta bin a las variables de entorno de Windows C:\Program Files\wkhtmltopdf\bin

## FFmpeg en windows

Para la conversión de audio a texto se usa la librería FFmpeg.

Para descargar ingres al enlace https://ffmpeg.org/download.html

Descarga los binarios de Windows y agrega la ruta de la carpeta bin a las variables de entorno Ej. C:\ffmpeg\bin
