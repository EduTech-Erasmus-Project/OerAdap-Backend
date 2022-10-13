# OerAdap-Backend
Backend Adaptador de Objetos de aprendizaje

## Pre-requisitos 📄

* Python
* PostgresSQL
* wkhtmltopdf y wkhtmltoimage
* FFmpeg


## Variables de entorno 📋
Crear un archivo .env en la raiz del proyecto 

```.env
SECRET_KEY=Secret Key
DEBUG=True
PROD=False
DB_NAME=Database name
DB_USER=Database user
DB_PASSWORD=Database password
DB_HOST=Database host
DB_PORT=Database port
MJ_APIKEY_PUBLIC=mailjet api key public server email
MJ_APIKEY_PRIVATE=email registered in mailjet server email
API_EMAIL=email registered in mailjet_server email
API_NAME=EduTech
```

## Instalación de librerías 🔧

En la carpeta requirements se encuentran las librerias para desarrollo en windows y producción en linux 

```console
> pip install -r requirements/dev.txt
```

## Ejecución de proyecto 🚀

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

## Métodos de adaptación

### Carga de archivos necesarios en el HTML

Archivos para barra de accesibilidad y videos.

```python
def templateInfusion(dir_len):
    """
    Archivos para barra de accesibilidad y videos.

    :param dir_len: Longitud del directorio "../../"
    :return: Objeto BeautifulSoup del HTML
    """
    headInfusion = """
   <!---------------------------------------Begin infusion plugin adaptability------------------------------------------------------->

    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/framework/fss/css/fss-layout.css" />
    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/framework/fss/css/fss-text.css" />
    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-bw-uio.css" />
    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-wb-uio.css" />
    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-by-uio.css" />
    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-yb-uio.css" />
    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-text-uio.css" />
    <link rel="stylesheet" type="text/css" href="uiAdaptability/lib/infusion/components/uiOptions/css/FatPanelUIOptions.css" />

    <link type="text/css" href="uiAdaptability/lib/jquery-ui/css/ui-lightness/jquery-ui-1.8.14.custom.css" rel="stylesheet" />
    <link type="text/css" href="uiAdaptability/css/VideoPlayer.css" rel="stylesheet" />
    <link type="text/css" href="uiAdaptability/lib/captionator/css/captions.css" rel="stylesheet" />


    <!-- Fluid and jQuery Dependencies -->
    <script type="text/javascript" src="uiAdaptability/lib/infusion/MyInfusion.js"></script>
    <!-- Utils -->
    <script type="text/javascript" src="uiAdaptability/lib/jquery-ui/js/jquery.ui.button.js"></script>
    <script type="text/javascript" src="uiAdaptability/lib/captionator/js/captionator.js"></script>
    <script type="text/javascript" src="uiAdaptability/lib/mediaelement/js/mediaelement.js"></script>
    <!--[if lt IE 9]>
       <script type="text/javascript" src="../lib/html5shiv/js/html5shiv.js"></script>
    <![endif]-->
    <!-- VideoPlayer dependencies -->
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_framework.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_showHide.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_html5Captionator.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_controllers.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/ToggleButton.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/MenuButton.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_media.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_transcript.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_intervalEventsConductor.js"></script>
    <script type="text/javascript" src="uiAdaptability/js/VideoPlayer_uiOptions.js"></script>

    <!---------------------------------------End infusion plugin adaptability------------------------------------------------------->
        """.format(get_directory_resource(dir_len))

    headInfusion = BeautifulSoup(headInfusion, 'html.parser')

    return headInfusion
```

Métodos y clases para la barra de accesibilidad.

```python
def templateBodyButtonInfusion(dir_len):
    """
    Métodos y clases para la barra de accesibilidad.

    :param dir_len: Longitud del directorio "../../"
    :return: Objeto BeautifulSoup del HTML
    """
    bodyInfusion = """ 
             <!---------------------------------------Begin infusion script adaptability------------------------------------------------------->
        <script>
            fluid.pageEnhancer({
                tocTemplate: "uiAdaptability/lib/infusion/components/tableOfContents/html/TableOfContents.html"
            });
        </script>

        <div class="flc-uiOptions fl-uiOptions-fatPanel">
            <div class="flc-slidingPanel-panel flc-uiOptions-iframe"></div>
            <div class="fl-panelBar">
                <button class="flc-slidingPanel-toggleButton fl-toggleButton">Show/Hide</button>
            </div>
        </div>
        <div class="flc-toc-tocContainer"> </div>
        <!---------------------------------------End infusion script adaptability------------------------------------------------------->

        <!---------------------------------------Begin infusion video script adaptability------------------------------------------------------->
           <script>
            var uiOptions = fluid.uiOptions.fatPanel.withMediaPanel(".flc-uiOptions", {
                prefix: "uiAdaptability/lib/infusion/components/uiOptions/html/",
                components: {
                    relay: {
                        type: "fluid.videoPlayer.relay"
                    }
                },
                templateLoader: {
                    options: {
                        templates: {
                            mediaControls: "uiAdaptability/html/UIOptionsTemplate-media.html"
                        }
                    }
                }
            });
           </script>
           <!---------------------------------------End infusion video script adaptability------------------------------------------------------->
        """
    bodyInfusion = BeautifulSoup(bodyInfusion, 'html.parser')
    return bodyInfusion
```

Métodos y clases para el reproductor de video accesible.

```python
def templateBodyVideoInfusion(dir_len):
    """
    Métodos y clases para el reproductor de video accesible.

    :param dir_len: Longitud del directorio "../../"
    :return: Objeto BeautifulSoup del HTML
    """
    bodyInfusion = """ 
                <!---------------------------------------Begin infusion script adaptability------------------------------------------------------->
           <script>
               fluid.pageEnhancer({
                   tocTemplate: "uiAdaptability/lib/infusion/components/tableOfContents/html/TableOfContents.html"
               });
           </script>

           <div class="flc-uiOptions fl-uiOptions-fatPanel">
               <div class="flc-slidingPanel-panel flc-uiOptions-iframe"></div>
               
           </div>
           <div class="flc-toc-tocContainer"> </div>
           <!---------------------------------------End infusion script adaptability------------------------------------------------------->

           <!---------------------------------------Begin infusion video script adaptability------------------------------------------------------->
           <script>
            var uiOptions = fluid.uiOptions.fatPanel.withMediaPanel(".flc-uiOptions", {
                prefix: "uiAdaptability/lib/infusion/components/uiOptions/html/",
                components: {
                    relay: {
                        type: "fluid.videoPlayer.relay"
                    }
                },
                templateLoader: {
                    options: {
                        templates: {
                            mediaControls: "uiAdaptability/html/UIOptionsTemplate-media.html"
                        }
                    }
                }
            });
           </script>
           <!---------------------------------------End infusion video script adaptability------------------------------------------------------->
           """
    bodyInfusion = BeautifulSoup(bodyInfusion, 'html.parser')
    return bodyInfusion
```

Archivos y métodos para la adaptación de textos y audios.

```python
def templateTextAdaptation(dir_len):
    """
    Archivos y métodos para la adaptación de textos y audios.

    :param dir_len: Longitud del directorio "../../"
    :return: Objeto BeautifulSoup del header y body HTML
    """
    head_adaptation = """ 
        <!---------------------------------------Begin text adaptability------------------------------------------------------->
        
        <link rel="stylesheet" href="%soer_resources/text_adaptation/style.css">
        
        <!---------------------------------------End text adaptability------------------------------------------------------->
    """ % get_directory_resource(dir_len)
    head_adaptation = BeautifulSoup(head_adaptation, 'html.parser')
    body_adaptation = """ 
        <!---------------------------------------Begin script text adaptability------------------------------------------------------->
    
        <script src="%soer_resources/text_adaptation/script.js"></script>
        
        <!---------------------------------------End script text adaptability------------------------------------------------------->
    """ % get_directory_resource(dir_len)

    body_adaptation = BeautifulSoup(body_adaptation, 'html.parser')

    return head_adaptation, body_adaptation
```

Archivos y métodos para la adaptación de Imagenes.

```python
def templateImageAdaptation(dir_len):
    """
    Archivos y métodos para la adaptación de Imagenes.
    
    :param dir_len: Longitud del directorio "../../"
    :return: Objeto BeautifulSoup del header y body HTML
    """
    head_adaptation = """ 
        <!---------------------------------------Begin image lightbox------------------------------------------------------->
        
        <link href="%soer_resources/lightbox/lightbox.css" rel="stylesheet" />
        
        <!---------------------------------------End image lightbox------------------------------------------------------->
    """ % get_directory_resource(dir_len)
    head_adaptation = BeautifulSoup(head_adaptation, 'html.parser')
    body_adaptation = """ 
        <!---------------------------------------Begin script image lightbox------------------------------------------------------->
        
        <script src="%soer_resources/lightbox/lightbox.js"></script>
        
        <!---------------------------------------End script image lightbox------------------------------------------------------->
    """ % get_directory_resource(dir_len)

    body_adaptation = BeautifulSoup(body_adaptation, 'html.parser')

    return head_adaptation, body_adaptation
```

### Adaptación de audios

Contenedor del botónes para convertir de audio a texto y texto a audio en el Objeto de aprendizaje.

```python
def templateAdaptationTag():
    """
    Template, contenedor HTML para el botón de audio.

    :return: (soup_data, id_ref) Instancia Beautifull de HTML y la referencia id.
    """
    id_ref = getUUID()
    tag_text_Adapted = """
                <div id="%s" class="text-adaptation">
                      
                </div>
            """ % id_ref
    soup_data = BeautifulSoup(tag_text_Adapted, 'html.parser')

    return soup_data, id_ref
```

Botón HTML para convertir de audio a texto en el Objeto de aprendizaje.

```python
def templateAudioTextButton(id_class_ref, text, dir_len):
    """
    Crear template HTML de conversion de audio a texto.

    :param id_class_ref:  id de referencia donde para encontrar del elemento en HTML.
    :param text: texto alternativo
    :param dir_len: Representación de la longitud del directorio "../../"
    :return: Instancia Beautifull de HTML.
    """
    button_tag_id = getUUID()
    tag_button = """
    <div class="tooltip text-container" id="{0}">
        <input class="text" type="image" onclick='textAdaptationEvent("{1}", "{2}", this)' src="{3}oer_resources/text_adaptation/paragraph.svg" aria-label="Convertir a texto" />
        <span class="tooltiptext">Convertir a texto</span>
     </div>
    """.format(button_tag_id, text, id_class_ref, get_directory_resource(dir_len))
    soup_data = BeautifulSoup(tag_button, 'html.parser')
    return soup_data
```

Crear un nuevo botón con el texto alternativo del audio y actualizar el HTML.

```python
    def __create_audio(self, tag_learning_object, request, div_soup_data, id_ref, page_learning_object,
                       is_webpage=False):
        """
        Crear de un texto alternativo de un audio de forma Manual

        :param tag_learning_object: Instancia de la Clase TagLearningObject
        :param request: Objecto Request
        :param div_soup_data: Template HTML
        :param id_ref: ID de referencia
        :param page_learning_object: Instancia de la Clase PageLearningObject
        :param is_webpage: Atributo booleano es una página de tipo weppage
        :return: None si es una página de tipo webpage o una instancia de la creación
        """
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('audio', tag_learning_object.id_class_ref)
        tag_aux = str(tag)
        tag.insert(1, div_soup_data)
        button_text_data = bsd.templateAudioTextButton(
            tag_learning_object.id_class_ref,
            request.data['text'], page_learning_object.dir_len)
        div_soup_data = tag.find(id=id_ref)
        div_soup_data.insert(1, button_text_data)
        tag_audio_div = bsd.templateAdaptedAudio(tag_aux, tag_learning_object.id_class_ref)
        tag_audio_div.append(div_soup_data)
        tag_container = bsd.templateContainerButtons(tag_learning_object.id_class_ref, tag_audio_div)
        tag.replace_with(copy.copy(tag_container))
        data = None
        if not is_webpage:
            data = self.__create_tag(request, request.data['text'], tag_container)

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return data
```

### Adaptación de párrafos de texto

Contenedor para el botón de mostrar el texto alternativo.

```python
def templateContainerButtons(id_class_ref, tag):
    """
     Crea un template que envuelve el tag en una DIV para adaptarla al HTML

    :param id_class_ref: Identificador del tag
    :param tag: Tag HTML
    :return: Instancia Beautifull de HTML.
    """
    tag_container = """
        <div id="{0}">
            {1}
         </div>
        """.format(id_class_ref, str(tag))
    tag_container = BeautifulSoup(tag_container, 'html.parser')
    return tag_container
```

Botón HTML para mostrar el texto alternativo.

```python
def templateAdaptedTextButton(id_class_ref, text, dir_len):
    """
    Crea el template para generar el boton de adaptabilidad de lectura facil
    
    :param id_class_ref: ID de referencia donde para encontrar el elemento en HTML
    :param text: Texto alternativo
    :param dir_len: Representacion de la logitud del directorio "../../"
    :return: Instancia Beautifull de HTML.
    """
    button_tag_id = getUUID()
    tag_button = """
     <div class="tooltip text-container" id="{0}">
        <input class="text" type="image" onclick='textAdaptationEvent("{1}", "{2}", this)' src="{3}oer_resources/text_adaptation/paragraph.svg" aria-label="Lectura fácil" />
        <span class="tooltiptext">Lectura fácil</span>
     </div>
   
    """.format(button_tag_id, text, id_class_ref, get_directory_resource(dir_len))
    soup_data = BeautifulSoup(tag_button, 'html.parser')
    return soup_data, button_tag_id
```

Crear un nuevo botón con el texto alternativo y actualizar el HTML.

```python
    def __create_text(self, request, tag_page_learning_object, id_ref, div_soup_data, page_learning_object,
                      is_webpage=False):
        """
        Crear de un texto alternativo de un parrafo de forma Manual

        :param request: Objecto Request
        :param tag_page_learning_object: Instancia de la Clase TagPageLearningObject
        :param id_ref: ID de referencia
        :param div_soup_data: Template HTML
        :param page_learning_object: Instancia de la Clase PageLearningObject
        :param is_webpage: Atributo booleano es una página de tipo weppage
        :return: None si es una página de tipo webpage o una instancia de la creación
        """

        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find(tag_page_learning_object.tag, tag_page_learning_object.id_class_ref)
        tag.append(div_soup_data)
        button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(
            tag_page_learning_object.id_class_ref,
            request.data['text'], page_learning_object.dir_len)
        div_soup = tag.find(id=id_ref)
        div_soup.insert(1, button_text_data)
        tag_container = bsd.templateContainerButtons(tag_page_learning_object.id_class_ref, tag)
        tag.replace_with(copy.copy(tag_container))
        data = None
        if not is_webpage:
            data = TagAdapted.objects.create(
                text=request.data['text'],
                html_text=str(tag_container),
                type="p",
                id_ref=id_ref,
                tag_page_learning_object=tag_page_learning_object
            )
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return data
```

### Adaptación de ALT de las imágenes

```python
    def __update_alt_image(self, request, page_learning_object, tag_class_ref, tag_adapted_learning_object):
        """
        Actualiza el ALT de una imagen y actualiza el HTML

        :param request: Objeto Request
        :param page_learning_object: Objeto de la calse PageLerningObject
        :param tag_class_ref: ID de referencia para buscar en el HTML
        :param tag_adapted_learning_object: Onjeto de la clase TagAdaptedLearningObject
        :return:
        """
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        text_update = request.data['text']

        if tag_adapted_learning_object.img_fullscreen:
            html_img_code = file_html.find('a', {"id": tag_class_ref})
            html_img_code["title"] = text_update
            html_img_code.findChild("img")["alt"] = text_update
        else:
            html_img_code = file_html.find("img", class_=tag_class_ref)
            html_img_code['alt'] = text_update

        tag_adapted_learning_object.html_text = str(html_img_code)
        tag_adapted_learning_object.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
```

### Previsualización en pantalla completa de las imágenes

Contenedor HTML para la previsualización de la imagen.

```python
def templateImagePreview(id_class_ref, src_img, alt_img, tag):
    """
    Crea el contenedor para la previsualización de imagen.

    :param id_class_ref: ID de referencia de la clase del tag.
    :param src_img: Atributo SRC de la imagen
    :param alt_img: Atributo ALT de la imagen
    :param tag: El tag de la imagen
    :return: Objeto BeautifulSoup del HTML.
    """
    tag_image_adapted = """
                    <a href="%s" id="%s"
                            title="%s"
                            class="fancybox" data-lightbox="gallery">
                    %s         
                    </a>
                """ % (src_img, id_class_ref, alt_img, str(tag))
    soup_data = BeautifulSoup(tag_image_adapted, 'html.parser')
    return soup_data
```

Método de actualización para agregar o quitar la previsualización de imágenes.

```python
    def __update_image(self, tag_adapted_learning_object, preview, page_learning_object, tag_class_ref):
        """
        Crea o quita la previsualización en pantalla completa de una imagen.

        :param tag_adapted_learning_object: Objeto de la clase TagAdaptedLearningObject.
        :param preview: Booleano para agregar o quitar la previsualización.
        :param page_learning_object: Objeto de la clase PageLearningObject.
        :param tag_class_ref: ID de referencia del tag.
        :return: Objeto de la clase TagAdaptedLearningObject actualizado.
        """
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        html_img_code = file_html.find('img', tag_class_ref)
        tag_adapted_learning_object.img_fullscreen = preview

        if preview:
            template = bsd.templateImagePreview(tag_class_ref, html_img_code.get('src', ''),
                                                html_img_code.get('alt', ''), html_img_code)
            html_img_code.replace_with(copy.copy(template))
            tag_adapted_learning_object.html_text = str(template)
            tag_adapted_learning_object.save()

        else:
            parent = file_html.find('a', {"id": tag_class_ref})
            if parent is not None:
                parent.replace_with(copy.copy(html_img_code))
                tag_adapted_learning_object.html_text = str(html_img_code)
                tag_adapted_learning_object.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return tag_adapted_learning_object
```

### Adaptación de videos

Contenedor HTML para el reproductor de video.

```python
def templateVideoAdaptation(video_src, video_type, video_title, captions, transcripts, tag_id):
    """
    Crea un el código HTM del contenedor del video y los subtítulos.

    :param video_src: Atributo SRC del video.
    :param video_type: Tipo de video.
    :param video_title: Titulo del video.
    :param captions: Subtítulos en formato STR.
    :param transcripts: Subtítulos en formato JSON.
    :param tag_id: ID de referencia del tag
    :return: Objeto BeautifulSoup del codigo HTML
    """

    player_uid = getUUID()
    video_bsd = """ 
     <div class="ui-video-adaptability" id="%s">
                                            <div class="videoPlayer fl-videoPlayer player-%s">
                                            </div>
                                            <script>
                                                
                                                var videoOptions = {
                                                    container: ".player-%s", options: {
                                                        video: {
                                                            sources: [
                                                                {
                                                                    src: "%s",
                                                                    type: "%s"
                                                                },
                                                            ],
                                                            captions: [
                                                                
    """ % (tag_id, player_uid, player_uid, video_src, video_type)

    for caption in captions:
        video_bsd = video_bsd + """ 
                                                                {
                                                                    src: "%s",
                                                                    type: "%s",
                                                                    srclang: "%s",
                                                                    label: "%s"
                                                                },
        """ % (caption['src'], caption['type'], caption['srclang'], caption['label'])

    video_bsd = video_bsd + """
                                                            ],
                                                            transcripts: [
    """
    for transcript in transcripts:
        video_bsd = video_bsd + """ 
                                                                {
                                                                    src: "%s",
                                                                    type: "%s",
                                                                    srclang: "%s",
                                                                    label: "%s"
                                                                },
        """ % (transcript['src'], transcript['type'], transcript['srclang'], transcript['label'])

    video_bsd = video_bsd + """
                                                            ]
                                                        },
                                                        videoTitle: "%s"
                                                    }
                                                };
                                                fluid.videoPlayer.makeEnhancedInstances(videoOptions, uiOptions.relay);
                                            </script>
                                        </div>
     """ % video_title

    video_bsd = BeautifulSoup(video_bsd, 'html.parser')

    return video_bsd
```

Método para la adaptación del video y actualización del HTML.

```python
def download_video(tag, data_attribute, learning_object, request):
    """
    Método para descargar el video y los subtítulos, usa channel_layer para la comunicación por Sockets.

    :param tag: Tag original del video
    :param data_attribute: Objeto de la clase DataAttribute
    :param learning_object: Objeto de la clase LearningObject
    :param request: Objeto Request

    """
    serializer = TagsVideoSerializer(tag)
    path_system = None
    path_preview = None
    captions = []
    transcripts = []

    try:
        dl = YoutubeDLThread(data_attribute.data_attribute, learning_object.path_adapted, request, tag)
        path_system, path_preview, path_src, tittle = dl.download()

        async_to_sync(channel_layer.group_send)("channel_" + str(tag.id), {"type": "send_new_data", "text": {
            "status": "process",
            "type": "video",
            "message": "Procesando video…"
        }})
        path_src = bsd.get_directory_resource(tag.page_learning_object.dir_len) + path_src
    except Exception as e:
        tag.adapting = False
        tag.save()
        async_to_sync(channel_layer.group_send)("channel_" + str(tag.id), {"type": "send_new_data", "text": {
            "status": "error",
            "type": "video",
            "message": e.__str__(),
            "data": serializer.data
        }})

    if path_system is None and path_preview is None:
        tag.adapting = False
        tag.save()
        async_to_sync(channel_layer.group_send)("channel_" + str(tag.id), {"type": "send_new_data", "text": {
            "status": "video_not_found",
            "type": "transcript",
            "message": "La fuente no permite la descarga de videos.",
            "data": serializer.data
        }})
    else:
        page_website_learning_object = None
        if tag.page_learning_object.is_webpage:
            name_filter = tag.page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=tag.page_learning_object.learning_object_id)

        try:
            tag_adapted = TagAdapted.objects.create(
                type="video",
                id_ref=tag.id_class_ref,
                text=tittle,
                path_src=path_src,
                path_preview=path_preview,
                path_system=path_system,
                tag_page_learning_object=tag,
            )
        except Exception as e:
            tag.adapting = False
            tag.save()
            async_to_sync(channel_layer.group_send)("channel_" + str(tag.id),
                                                    {"type": "send_new_data", "text": {
                                                        "status": "error",
                                                        "type": "video",
                                                        "message": e.__str__(),
                                                        "data": serializer.data
                                                    }})

        if data_attribute.source.find("youtube") > -1:

            async_to_sync(channel_layer.group_send)("channel_" + str(tag.id), {"type": "send_new_data", "text": {
                "status": "downloading",
                "type": "transcript",
                "message": "Descargando subtitulo de YouTube...",
            }})

            try:

                transcripts, captions = generate_transcript_youtube(data_attribute.data_attribute, tittle,
                                                                    learning_object.path_adapted, request,
                                                                    tag.page_learning_object.dir_len)

                for transcript in transcripts:
                    create_transcript(transcript, tag_adapted)

                for caption in captions:
                    create_transcript(caption, tag_adapted)

                save_data_attribute(data_attribute, path_src, path_system, path_preview)

                video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                             transcripts, tag.id_class_ref)
                tag_adapted.html_text = str(video_template)
                tag_adapted.save()
                # save video youtube
                save_video_on_html(tag, copy.copy(video_template), tag.page_learning_object)
                # find web page
                if page_website_learning_object is not None:
                    save_video_on_html(tag, copy.copy(video_template), page_website_learning_object)

                tag.adapting = False
                tag.save()

                if len(transcripts) > 0 and len(captions) > 0:
                    async_to_sync(channel_layer.group_send)("channel_" + str(tag.id),
                                                            {"type": "send_new_data", "text": {
                                                                "status": "finished",
                                                                "type": "transcript",
                                                                "message": "Subtítulos descargados.",
                                                                "data": serializer.data
                                                            }})
                else:
                    async_to_sync(channel_layer.group_send)("channel_" + str(tag.id),
                                                            {"type": "send_new_data", "text": {
                                                                "status": "no_supported_transcript",
                                                                "type": "transcript",
                                                                "message": "La fuente no tiene subtítulos.",
                                                                "data": serializer.data
                                                            }})

            except Exception as e:
                tag.adapting = False
                tag.save()
                async_to_sync(channel_layer.group_send)("channel_" + str(tag.id),
                                                        {"type": "send_new_data", "text": {
                                                            "status": "error",
                                                            "type": "transcript",
                                                            "message": e.__str__(),
                                                            "data": serializer.data
                                                        }})

        else:
            save_data_attribute(data_attribute, path_src, path_system, path_preview)

            video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                         transcripts, tag.id_class_ref)

            tag_adapted.html_text = str(video_template)
            tag_adapted.save()

            save_video_on_html(tag, copy.copy(video_template), tag.page_learning_object)
            if page_website_learning_object is not None:
                save_video_on_html(tag, copy.copy(video_template), page_website_learning_object)

            tag.adapting = False
            tag.save()

            async_to_sync(channel_layer.group_send)("channel_" + str(tag.id),
                                                    {"type": "send_new_data", "text": {
                                                        "status": "ready_tag_adapted",
                                                        "type": "transcript",
                                                        "message": "La fuente no tiene subtítulos.",
                                                        "data": serializer.data
                                                    }})
```
