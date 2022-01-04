import json
from urllib.parse import urlparse
from unipath import Path
from bs4 import BeautifulSoup
import os
import shortuuid
import magic
from ..learning_object.models import PageLearningObject, TagPageLearningObject, DataAttribute, TagAdapted

BASE_DIR = Path(__file__).ancestor(3)

PROD = None
with open(os.path.join(Path(__file__).ancestor(4), "prod.json")) as f:
    PROD = json.loads(f.read())


def read_html_files(directory):
    """Lectura de archivos html
    return :
    """
    files = []
    for entry in os.scandir(directory):
        if entry.path.endswith(".html"):
            # print(entry.name)
            files.append({
                "file": entry.path,
                "file_name": entry.name
            })
    return files


def getUUID():
    """genera un id identificador"""
    return str(shortuuid.ShortUUID().random(length=8))


def generateBeautifulSoupFile(html_doc):
    """
    Genera un objeto de BeautifulSoup para realizar web scraping
    :param html_doc:
    :return BeautifulSoup Data:
    """

    blob = open(html_doc, 'rb').read()
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_buffer(blob)
    if encoding == 'binary':
        encoding = 'utf-8'

    with open(html_doc, encoding=encoding) as file:
        #try:
        soup_data = BeautifulSoup(file, "html.parser")
        file.close()
        return soup_data
        #except Exception as e:
            #print(e)
            #return None



def save_filesHTML_db(files, learningObject, directory, directory_origin, request_host):
    """Lectura de archivos html,
    guardamos cada directorio
    de cada archivo en la base
    de datos
    """
    pages_convert = []

    # print(files_name)

    for file in files:
        # page_object = PageLearningObject.objects.get(
        # pk=page.id)  # refactirizar sin hacer peticion a la base de datos
        # print("Objeto"+str(Page_object))
        # print(file['file'])

        directory_file = os.path.join(BASE_DIR, directory, file['file'])
        preview_path = os.path.join(request_host, directory, file['file_name']).replace("\\", "/")
        if PROD['PROD']:
            preview_path = preview_path.replace("http://", "https://")

        soup_data = generateBeautifulSoupFile(directory_file)
        pages_convert.append(soup_data)

        page_adapted = PageLearningObject.objects.create(
            type="adapted",
            title=soup_data.find('title').text,
            path=directory_file,
            preview_path=preview_path,
            learning_object=learningObject)

        directory_file_origin = os.path.join(BASE_DIR, directory_origin, file['file'])
        preview_path_origin = os.path.join(request_host, directory_origin, file['file_name']).replace("\\", "/")
        if PROD['PROD']:
            preview_path_origin = preview_path_origin.replace("http://", "https://")

        PageLearningObject.objects.create(
            type="origin",
            title=soup_data.find('title').text,
            path=directory_file_origin,
            preview_path=preview_path_origin,
            learning_object=learningObject)

        # Se procesa las etiquetas html
        web_scraping_p(soup_data, page_adapted, file['file'])
        webs_craping_img(soup_data, page_adapted, file['file'], directory, request_host)
        webs_craping_audio(soup_data, page_adapted, file['file'], 'audio', request_host, directory)

        webs_craping_video(soup_data, page_adapted, file['file'], 'video', request_host, directory)
        webs_craping_iframe(soup_data, page_adapted, file['file'])


def save_paragraph(tag_identify, p_text, page_id, class_uuid):
    if len(p_text.get('class', [])) > 0:
        p_text['class'].append(class_uuid)
    else:
        p_text['class'] = class_uuid

    tag_page = TagPageLearningObject.objects.create(tag=tag_identify,
                                                    text=str(p_text.string),
                                                    html_text=str(p_text),
                                                    page_learning_object=page_id,
                                                    id_class_ref=class_uuid)
    # tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

def web_scraping_p(aux_text, page_id, file):
    """ Exatraccion de los parrafos de cada pagina html,
    se crea un ID unico, para identificar cada elemento
    """

    length_text = 300
    for p_text in aux_text.find_all("p"):
        if p_text.string:
            if len(p_text.string) >= length_text:
                class_uuid = "p-" + getUUID()
                save_paragraph("p", p_text, page_id, class_uuid)

    for p_text in aux_text.find_all('span'):
        if p_text.string:
            if len(p_text.string) >= length_text:
                class_uuid = 'span-' + getUUID()
                save_paragraph("span", p_text, page_id, class_uuid)

    for p_text in aux_text.find_all('li'):
        if p_text.string:
            if len(p_text.string) >= length_text:
                class_uuid = 'li-' + getUUID()
                save_paragraph("li", p_text, page_id, class_uuid)

    generate_new_htmlFile(aux_text, file)


def webs_craping_img(aux_text, page_id, file, directory, request_host):
    """Vamos a extraer el alt de las imagenes y crear clases en las imagenes"""
    tag_identify = "img"
    attribute_img = "src"
    text_alt = ""

    for tag in aux_text.find_all(tag_identify):

        class_uuid = tag_identify + '-' + getUUID()
        if len(tag.get('class', [])) > 0:
            tag['class'].append(class_uuid)
        else:
            tag['class'] = class_uuid

        if tag.get('alt') is not None:
            text_alt = tag.get('alt')
        else:
            tag['alt'] = text_alt

        tag_page = TagPageLearningObject.objects.create(
            tag=tag_identify,
            text=str(text_alt),
            html_text=str(tag),
            page_learning_object=page_id,
            id_class_ref=class_uuid
        )

        # tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
        # tag_page_object = TagPageLearningObject.objects.get(pk=tag_page.id)  # refactirizar sin hacer
        # peticion a la base de datos

        data_attribute = DataAttribute(
            attribute=attribute_img,
            data_attribute=str(os.path.join(request_host, directory, tag.get('src', []))),
            tag_page_learning_object=tag_page,
            type=tag_identify
        )
        data_attribute.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

        tag_adapted = TagAdapted.objects.create(
            type=tag_identify,
            text=str(text_alt),
            html_text=str(tag),
            id_ref=class_uuid,
            path_src=str(os.path.join(request_host, directory, tag.get('src', []))),
            tag_page_learning_object=tag_page
        )

    generate_new_htmlFile(aux_text, file)


def webs_craping_video(aux_text, page_id, file, tag_identify, request_host, directory):
    """Vamos a extraer el el src de los videos y audios"""
    attribute_src = "src"

    for tag in aux_text.find_all(tag_identify):
        class_uuid = tag_identify + '-' + getUUID()
        if len(tag.get('class', [])) > 0:
            tag['class'].append(class_uuid)
        else:
            tag['class'] = class_uuid

        # directory_file_origin = os.path.join(BASE_DIR, directory_origin, file['file'])
        # preview_path_origin = os.path.join(request_host, directory_origin, file['file_name']).replace("\\", "/")

        tag_page = TagPageLearningObject.objects.create(
            tag=tag_identify,
            html_text=str(tag),
            page_learning_object=page_id,
            id_class_ref=class_uuid
        )
        # tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

        # tag_page_object = TagPageLearningObject.objects.get(pk=tag_page.id)  # refactirizar sin hacer
        # peticion a la base de datos
        subtag = tag.find_all('source')
        subtag = subtag[0]
        # print(tag.find_all('source'))
        path_preview = os.path.join(request_host, directory, str(subtag.get('src'))).replace("\\", "/")

        if PROD['PROD']:
            path_preview = path_preview.replace("http://", "https://")

        path_system = os.path.join(BASE_DIR, directory, str(subtag.get('src')))

        data_attribute = DataAttribute(
            attribute=attribute_src,
            data_attribute=str(subtag.get('src')),
            type=str(subtag.get('type')),
            tag_page_learning_object=tag_page,
            path_preview=path_preview,
            path_system=path_system,
            source="local"
        )

        data_attribute.save()
        # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
    generate_new_htmlFile(aux_text, file)


def webs_craping_audio(aux_text, page_id, file, tag_identify, request_host, directory):
    """Vamos a extraer el el src de los videos y audios"""
    attribute_src = "src"

    for tag in aux_text.find_all(tag_identify):

        class_uuid = tag_identify + '-' + getUUID()

        if len(tag.get('class', [])) > 0:
            tag['class'].append(class_uuid)
        else:
            tag['class'] = class_uuid

        tag_page = TagPageLearningObject.objects.create(
            tag=tag_identify,
            html_text=str(tag),
            page_learning_object=page_id,
            id_class_ref=class_uuid
        )

        # tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

        # tag_page_object = TagPageLearningObject.objects.get(pk=tag_page.id)  # refactirizar sin hacer
        # peticion a la base de datos

        data_attribute = DataAttribute(
            attribute=attribute_src,
            data_attribute=str(os.path.join(request_host, directory, tag.get('src', []))),
            tag_page_learning_object=tag_page,
            type=tag_identify,
            path_system=str(os.path.join(BASE_DIR, directory, tag.get('src', []))),
        )
        data_attribute.save()

        # tag_adapted = TagAdapted.objects.create(
        #   type=tag_identify,
        #  html_text=str(tag),
        # id_ref=class_uuid,
        # path_src=str(os.path.join(request_host, directory, tag.get('src', []))),
        # tag_page_learning_object=tag_page
    # )

    # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
    generate_new_htmlFile(aux_text, file)


def webs_craping_iframe(file_beautiful_soup, page_id, file):
    """Vamos a extraer el src de los iframses incrustados de videos"""
    tag_identify = "iframe"
    attribute_src = "src"
    text_title = ""

    for tag in file_beautiful_soup.find_all(tag_identify):

        # print(tag)
        if '.com' not in str(tag.get('src')):
            continue

        class_uuid = tag_identify + '-' + getUUID()

        if len(tag.get('class', [])) > 0:
            tag['class'].append(class_uuid)
        else:
            tag['class'] = class_uuid

        if tag.get('title') is not None:
            text_title = tag.get('title')
        else:
            tag['title'] = text_title

        tag_page = TagPageLearningObject.objects.create(
            tag=tag_identify,
            text=str(text_title),
            html_text=str(tag),
            page_learning_object=page_id,
            id_class_ref=class_uuid
        )

        # tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
        # tag_page_object = TagPageLearningObject.objects.get(pk=tag_page.id)  # refactirizar sin hacer
        # peticion a la base de datos

        domain = urlparse(str(tag.get('src'))).netloc

        data_attribute = DataAttribute(
            attribute=attribute_src,
            data_attribute=str(tag.get('src')),
            tag_page_learning_object=tag_page,
            path_preview=str(tag.get('src')),
            source=domain
        )
        data_attribute.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
    generate_new_htmlFile(file_beautiful_soup, file)


def generate_new_htmlFile(file_beautiful_soup, path):
    """Genera un nuevo archivo con los atributos editados"""
    html = file_beautiful_soup.prettify('utf-8')
    # print("utf:", html)
    new_direction = path
    if os.path.exists(new_direction):
        with open(new_direction, "wb") as file:
            file.write(html)
    else:
        os.mkdir(new_direction)
        with open(new_direction, "wb") as file:
            file.write(html)


def templateInfusion():
    headInfusion = BeautifulSoup("""
   <!---------------------------------------Begin infusion plugin adaptability------------------------------------------------------->

    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/framework/fss/css/fss-layout.css" />
    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/framework/fss/css/fss-text.css" />
    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-bw-uio.css" />
    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-wb-uio.css" />
    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-by-uio.css" />
    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-theme-yb-uio.css" />
    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/components/uiOptions/css/fss/fss-text-uio.css" />
    <link rel="stylesheet" type="text/css" href="oer_resources/uiAdaptability/lib/infusion/components/uiOptions/css/FatPanelUIOptions.css" />

    <link type="text/css" href="oer_resources/uiAdaptability/lib/jquery-ui/css/ui-lightness/jquery-ui-1.8.14.custom.css" rel="stylesheet" />
    <link type="text/css" href="oer_resources/uiAdaptability/css/VideoPlayer.css" rel="stylesheet" />
    <link type="text/css" href="oer_resources/uiAdaptability/lib/captionator/css/captions.css" rel="stylesheet" />


    <!-- Fluid and jQuery Dependencies -->
    <script type="text/javascript" src="oer_resources/uiAdaptability/lib/infusion/MyInfusion.js"></script>
    <!-- Utils -->
    <script type="text/javascript" src="oer_resources/uiAdaptability/lib/jquery-ui/js/jquery.ui.button.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/lib/captionator/js/captionator.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/lib/mediaelement/js/mediaelement.js"></script>
    <!--[if lt IE 9]>
       <script type="text/javascript" src="../lib/html5shiv/js/html5shiv.js"></script>
    <![endif]-->
    <!-- VideoPlayer dependencies -->
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_framework.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_showHide.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_html5Captionator.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_controllers.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/ToggleButton.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/MenuButton.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_media.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_transcript.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_intervalEventsConductor.js"></script>
    <script type="text/javascript" src="oer_resources/uiAdaptability/js/VideoPlayer_uiOptions.js"></script>

    <!---------------------------------------End infusion plugin adaptability------------------------------------------------------->
        """, 'html.parser')

    return headInfusion


def templateBodyButtonInfusion():
    bodyInfusion = BeautifulSoup(""" 
             <!---------------------------------------Begin infusion script adaptability------------------------------------------------------->
        <script>
            fluid.pageEnhancer({
                tocTemplate: "oer_resources/uiAdaptability/lib/infusion/components/tableOfContents/html/TableOfContents.html"
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
                prefix: "oer_resources/uiAdaptability/lib/infusion/components/uiOptions/html/",
                components: {
                    relay: {
                        type: "fluid.videoPlayer.relay"
                    }
                },
                templateLoader: {
                    options: {
                        templates: {
                            mediaControls: "oer_resources/uiAdaptability/html/UIOptionsTemplate-media.html"
                        }
                    }
                }
            });
           </script>
           <!---------------------------------------End infusion video script adaptability------------------------------------------------------->
        """, 'html.parser')
    return bodyInfusion


def templateBodyVideoInfusion():
    bodyInfusion = BeautifulSoup(""" 
                <!---------------------------------------Begin infusion script adaptability------------------------------------------------------->
           <script>
               fluid.pageEnhancer({
                   tocTemplate: "oer_resources/uiAdaptability/lib/infusion/components/tableOfContents/html/TableOfContents.html"
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
                prefix: "oer_resources/uiAdaptability/lib/infusion/components/uiOptions/html/",
                components: {
                    relay: {
                        type: "fluid.videoPlayer.relay"
                    }
                },
                templateLoader: {
                    options: {
                        templates: {
                            mediaControls: "oer_resources/uiAdaptability/html/UIOptionsTemplate-media.html"
                        }
                    }
                }
            });
           </script>
           <!---------------------------------------End infusion video script adaptability------------------------------------------------------->
           """, 'html.parser')
    return bodyInfusion


def templateTextAdaptation():
    head_adaptation = BeautifulSoup(""" 
        <!---------------------------------------Begin text adaptability------------------------------------------------------->
        
        <link rel="stylesheet" href="oer_resources/text_adaptation/style.css">
        
        <!---------------------------------------End text adaptability------------------------------------------------------->
    """, 'html.parser')
    body_adaptation = BeautifulSoup(""" 
        <!---------------------------------------Begin script text adaptability------------------------------------------------------->
    
        <script src="oer_resources/text_adaptation/script.js"></script>
        
        <!---------------------------------------End script text adaptability------------------------------------------------------->
    """, 'html.parser')

    return head_adaptation, body_adaptation


def templateAdaptationTag(id_class_ref):
    id_ref = getUUID()
    tag_text_Adapted = """
                <div id="%s" class="text-adaptation">
                      
                </div>
            """ % id_ref
    soup_data = BeautifulSoup(tag_text_Adapted, 'html.parser')

    return soup_data, id_ref


def templateAdaptionImage(original_tag, id_class_ref):
    tag_figure_new = """<figure class="exe-figure exe-image float-left" style="margin: 0; padding: 10px;text-align: center;"> 

      </figure>"""
    tag_figure_caption = """ <figcaption class="figcaption" style="text-align : center"><span class="title"><em>

        </em></span></figcaption>"""
    tag_figure_caption = BeautifulSoup(tag_figure_caption, "html.parser")
    aux = tag_figure_caption.em
    aux.append(original_tag[0].get('alt', []))

    tag_figure_new = BeautifulSoup(tag_figure_new, "html.parser")
    originaltag_new = tag_figure_new.figure
    new_tag = tag_figure_new.new_tag('img', style=original_tag[0].get('style', []),
                                     **{'class': original_tag[0].get('class', [])}, alt=original_tag[0].get('alt', []),
                                     src=original_tag[0].get('src', []))
    originaltag_new.append(new_tag);
    originaltag_new.insert(2, tag_figure_caption)
    return originaltag_new


def templateAdaptedTextButton(id_class_ref, text):
    button_tag_id = getUUID()
    tag_button = """
     <div class="tooltip text-container" id="%s">
        <input class="text" type="image" onclick='textAdaptationEvent("%s", "%s", this)' src="oer_resources/text_adaptation/paragraph.svg" aria-label="Lectura fácil" />
        <span class="tooltiptext">Lectura fácil</span>
     </div>
   
    """ % (button_tag_id, text, id_class_ref)
    soup_data = BeautifulSoup(tag_button, 'html.parser')
    return soup_data, button_tag_id


def templateAudioTextButton(id_class_ref, text):
    button_tag_id = getUUID()
    tag_button = """
    <div class="tooltip text-container" id="%s">
        <input class="text" type="image" onclick='textAdaptationEvent("%s", "%s", this)' src="oer_resources/text_adaptation/paragraph.svg" aria-label="Convertir a texto" />
        <span class="tooltiptext">Convertir a texto</span>
     </div>
    """ % (id_class_ref, text, id_class_ref)
    soup_data = BeautifulSoup(tag_button, 'html.parser')
    return soup_data


def templateAdaptedAudio(original_tag_audio, id_class_ref):
    class_aux = 'class="' + id_class_ref + '"'
    tag_figure_new = """<div """ + class_aux + """id="ref_adapted" style="text-align: justify;">""" + str(
        original_tag_audio) + """
       </div>"""
    tag_figure_new = BeautifulSoup(tag_figure_new, 'html.parser')
    return tag_figure_new


def templateAdaptedAudioButton(id_class_ref, audio_src):
    button_tag_id = getUUID()
    tag_audio = """
    <div class="tooltip audio-container" id="%s">
        <input class="audio" type="image" onclick='audioAdaptationEvent("%s", "%s", this)' src="oer_resources/text_adaptation/audio-on.svg" aria-label="Convertir a audio" />
        <span class="tooltiptext">Convertir a audio</span>
     </div>   
    """ % (button_tag_id, audio_src, id_class_ref,)
    soup_data = BeautifulSoup(tag_audio, 'html.parser')
    return soup_data, button_tag_id


def convertElementBeautifulSoup(html_code):
    return BeautifulSoup(html_code, 'html.parser')


def templateVideoAdaptation(video_src, video_type, video_title, captions, transcripts, tag_id):
    player_uid = getUUID()
    video_bsd = """ 
     <div class="ui-video-adaptability %s">
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
        # print(transcript['src'])
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
