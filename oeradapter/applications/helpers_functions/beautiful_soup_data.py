from unipath import Path
from bs4 import BeautifulSoup
import os
import shortuuid

from ..learning_object.models import PageLearningObject, TagPageLearningObject, DataAttribute

BASE_DIR = Path(__file__).ancestor(3)


def getUUID():
    """genera un id identificador"""
    return str(shortuuid.ShortUUID().random(length=8))


def generateBeautifulSoupFile(html_doc):
    """
    Genera un objeto de BeautifulSoup para realizar web scraping
    :param html_doc:
    :return BeautifulSoup Data:
    """
    with open(html_doc, encoding='utf8') as file:
        soup_data = BeautifulSoup(file, "html.parser")
        file.close()
        return soup_data


def save_filesHTML_db(files, learningObject, directory):
    """Lectura de archivos html,
    guardamos cada directorio
    de cada archivo en la base
    de datos
    """
    pages_convert = []

    for file in files:
        page = PageLearningObject(path=file, learning_object=learningObject)
        page.save()

        page_object = PageLearningObject.objects.get(
            pk=page.id)  # refactirizar sin hacer peticion a la base de datos
        # print("Objeto"+str(Page_object))

        directory_file = os.path.join(BASE_DIR, directory, file)
        soup_data = generateBeautifulSoupFile(directory_file)
        pages_convert.append(soup_data)

        # Se procesa las etiquetas html
        web_scraping_p(soup_data, page_object, file)
        webs_craping_img(soup_data, page_object, file)
        webs_craping_video_and_audio(soup_data, page_object, file, 'audio')
        webs_craping_video_and_audio(soup_data, page_object, file, 'video')
        webs_craping_iframe(soup_data, page_object, file)


def web_scraping_p(aux_text, page_id, file):
    """ Exatraccion de los parrafos de cada pagina html,
    se crea un ID unico, para identificar cada elemento
    """
    # print(aux_text)
    tag_identify = "p"

    # Reducir la lista con el criterio de que la longitud de texto sea > 2 para evitar que recorra todos los
    for p_text in aux_text.find_all(tag_identify):
        if p_text.string:
            if len(p_text.string) >= 50:
                # uuid = str(shortuuid.ShortUUID().random(length=8))
                class_uuid = tag_identify + '-' + getUUID()
                if len(p_text.get('class', [])) > 0:
                    p_text['class'].append(class_uuid)
                else:
                    p_text['class'] = class_uuid

                tag_page = TagPageLearningObject(tag=tag_identify,
                                                 text=str(p_text.string),
                                                 html_text=str(p_text),
                                                 page_learning_object=page_id,
                                                 id_class_ref=class_uuid)
                tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
        elif not p_text.string:
            print("Parrafo vacio")
    generate_new_htmlFile(aux_text, file)


def webs_craping_img(aux_text, page_id, file):
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

        tag_page = TagPageLearningObject(
            tag=tag_identify, text=str(text_alt),
            html_text=str(tag), page_learning_object=page_id, id_class_ref=class_uuid
        )
        tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

        tag_page_object = TagPageLearningObject.objects.get(pk=tag_page.id)  # refactirizar sin hacer
        # peticion a la base de datos

        data_attribute = DataAttribute(
            atribute=attribute_img,
            data_atribute=str(tag.get('src', [])),
            tag_page_learning_object=tag_page_object
        )
        data_attribute.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
    generate_new_htmlFile(aux_text, file)


def webs_craping_video_and_audio(aux_text, page_id, file, tag_identify):
    """Vamos a extraer el el src de los videos y audios"""
    attribute_src = "src"

    for tag in aux_text.find_all(tag_identify):

        class_uuid = tag_identify + '-' + getUUID()
        if len(tag.get('class', [])) > 0:
            tag['class'].append(class_uuid)
        else:
            tag['class'] = class_uuid

        tag_page = TagPageLearningObject(
            tag=tag_identify,
            html_text=str(tag),
            page_learning_object=page_id,
            id_class_ref=class_uuid
        )
        tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

        tag_page_object = TagPageLearningObject.objects.get(pk=tag_page.id)  # refactirizar sin hacer
        # peticion a la base de datos

        for subtag in tag.find_all('source'):
            # print(tag.find_all('source'))
            data_attribute = DataAttribute(
                atribute=attribute_src,
                data_atribute=str(subtag.get('src')),
                type=str(subtag.get('type')),
                tag_page_learning_object=tag_page_object
            )
            data_attribute.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
    generate_new_htmlFile(aux_text, file)


def webs_craping_iframe(aux_text, page_id, file):
    """Vamos a extraer el src de los iframses incrustados de videos"""
    tag_identify = "iframe"
    attribute_src = "src"
    text_title = ""

    for tag in aux_text.find_all(tag_identify):

        class_uuid = tag_identify + '-' + getUUID()

        if len(tag.get('class', [])) > 0:
            tag['class'].append(class_uuid)
        else:
            tag['class'] = class_uuid

        if tag.get('title') is not None:
            text_title = tag.get('title')
        else:
            tag['title'] = text_title

        tag_page = TagPageLearningObject(
            tag=tag_identify,
            text=str(text_title),
            html_text=str(tag),
            page_learning_object=page_id,
            id_class_ref=class_uuid
        )
        tag_page.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

        tag_page_object = TagPageLearningObject.objects.get(pk=tag_page.id)  # refactirizar sin hacer
        # peticion a la base de datos

        data_atribute = DataAttribute(
            atribute=attribute_src,
            data_atribute=str(tag.get('src')),
            tag_page_learning_object=tag_page_object
        )
        data_atribute.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos
    generate_new_htmlFile(aux_text, file)


def generate_new_htmlFile(aux_text, path):
    """Genera un nuevo archivo con los atributos editados"""
    html = aux_text.prettify('utf-8')
    # print("utf:", html)
    new_direction = path
    if os.path.exists(new_direction):
        with open(new_direction, "wb") as file:
            file.write(html)
    else:
        os.mkdir(new_direction)
        with open(new_direction, "wb") as file:
            file.write(html)
