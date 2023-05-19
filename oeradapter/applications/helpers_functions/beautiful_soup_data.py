from urllib.parse import urlparse
import environ
from unipath import Path
from . import metadata as meta, metadata
from bs4 import BeautifulSoup, Comment
import os
import shortuuid
import magic
from ..learning_object.models import PageLearningObject, TagPageLearningObject, DataAttribute, TagAdapted

BASE_DIR = Path(__file__).ancestor(3)

env = environ.Env(
    PROD=(bool, False)
)
environ.Env.read_env(os.path.join(Path(__file__).ancestor(4), '.env'))


def split_path(preview_path):
    path = os.path.normpath(preview_path)
    path_split = path.split(os.sep)
    path_split = path_split[:-1]
    return path_split


def get_path_preview(src, path_split):
    attribute_src_text = str(src)
    attribute_src_split = attribute_src_text.split("/")
    vec_filter = list(filter(lambda x: '..' in x, attribute_src_split))
    if len(vec_filter) > 0:
        path_split = path_split[:-len(vec_filter)]
    path_preview = ("/".join(path_split) + "/" + attribute_src_split[-1]).replace("http://", "https://")
    return path_preview


def get_directory_resource(dir_len):
    dir_path = ""
    if dir_len > 0:
        for i in range(dir_len):
            dir_path += dir_path + '../'
    return dir_path


def read_html_files(directory):
    """Lectura de archivos html del objeto de aprendizaje

    :param srt directory: Directorio raiz donde se encuentra los archivos del objeto de aprendizaje

    :return : tuple(str[], str[], boolean)

    """

    files_vect = []
    """for entry in os.scandir(directory):
        if entry.path.endswith(".html"):
            # print(entry.name)
            files.append({
                "file": entry.path,
                "file_name": entry.name
            })"""
    root_dirs = list()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                root_dirs.append(root)
                aux = os.path.join(root, file);

                tag = generateBeautifulSoupFile(aux)
                if "oeradapter-edutech" in tag.body.get('class', []):
                    return files_vect, root_dirs, True
                elif (tag.body.get('class', []) == []):
                    tag.body['class'] = "oeradapter-edutech"
                else:
                    tag.body['class'].append("oeradapter-edutech")

                generate_new_htmlFile(tag, aux)

                aux_path = aux.replace(directory, '')
                aux_path = aux_path[1:]

                aux_path_len = root.replace(directory, '')
                aux_path_len = os.path.normpath(aux_path_len)
                aux_path_len_vec = aux_path_len.split(os.sep)
                aux_path_len_vec = aux_path_len_vec[1:]

                files_vect.append({
                    "file": aux,
                    "file_name": aux_path,
                    "dir_len": len(aux_path_len_vec),
                })

    return files_vect, root_dirs, False


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
        # try:
        soup_data = BeautifulSoup(file, "html.parser")
        file.close()
        return soup_data


def save_filesHTML_db(files, learning_object, directory, directory_origin, request_host, files_website):
    """
    Lectura de archivos html, guardamos cada directorio
    de cada archivo en la base de datos

    :param files_website:
    :param object files: contiene informacion de los nombre de archivos y directorios
    :param object learning_object: objeto de aprendizaje
    :param path directory: directorio raiz
    :param path directory_origin: directorio de origin donde se encuentra el objeto de aprendizaje
    :param request_host: direccion del host

    """
    # pages_convert = []

    for file in files:

        # print("origin file", file['file_name'])

        soup_data_website = None
        page_adapted_website = None
        file_website = None

        soup_data, page_adapted = create_page_learning_object(learning_object, directory, directory_origin,
                                                              request_host,
                                                              file)

        find_website = [file_w for file_w in files_website if file['file_name'] in file_w['file_name']]

        # print("find_website ", find_website)

        # print("file_website", find_website)
        if len(find_website) > 0:
            file_website = find_website[0]
            soup_data_website, page_adapted_website = create_page_learning_object(learning_object, directory,
                                                                                  directory_origin,
                                                                                  request_host, file_website, True)

        # Se procesa las etiquetas html
        web_scraping_paragraph(soup_data, page_adapted, file['file'], soup_data_website, page_adapted_website,
                               file_website)

        # print("Data enter in section --", file)

        webs_scraping_img(soup_data, page_adapted, file['file'], directory, request_host, soup_data_website,
                          page_adapted_website, file_website, learning_object.path_xml)

        webs_scraping_audio(soup_data, page_adapted, file['file'], 'audio', directory, request_host,
                            soup_data_website,
                            page_adapted_website, file_website)

        webs_scraping_video(soup_data, page_adapted, file['file'], 'video', directory, request_host,
                            soup_data_website,
                            page_adapted_website, file_website)

        webs_scraping_iframe(soup_data, page_adapted, file['file'], soup_data_website, page_adapted_website,
                             file_website)


def create_page_learning_object(learningObject, directory, directory_origin, request_host, file, is_webpage=False):
    directory_file = os.path.join(BASE_DIR, directory, file['file'])
    preview_path = os.path.join(request_host, directory, file['file_name']).replace("\\", "/")

    if env('PROD'):
        preview_path = preview_path.replace("http://", "https://")

    soup_data = generateBeautifulSoupFile(directory_file)

    comment = Comment("""
            This learning object has been adapted with the OerAdap tool from the EduTech group.
            License: MIT license
            Attribution to EduTech Project: https://edutech-project.org/
            Created by: 
            Claudio Maldonado - https://www.linkedin.com/in/claudiomldo/
            Edwin Márquez - https://www.linkedin.com/in/edwinFernandoMarquez/
            """)

    soup_data.insert(0, comment)
    soup_data.insert(0, "")

    # pages_convert.append(soup_data)

    page_adapted = PageLearningObject.objects.create(
        type="adapted",
        title=soup_data.find('title').text,
        path=directory_file,
        preview_path=preview_path,
        learning_object=learningObject,
        dir_len=file['dir_len'],
        file_name=file['file_name'],
        is_webpage=is_webpage
    )

    directory_file_origin = os.path.join(BASE_DIR, directory_origin, file['file'])
    preview_path_origin = os.path.join(request_host, directory_origin, file['file_name']).replace("\\", "/")
    if env('PROD'):
        preview_path_origin = preview_path_origin.replace("http://", "https://")

    PageLearningObject.objects.create(
        type="origin",
        title=soup_data.find('title').text,
        path=directory_file_origin,
        preview_path=preview_path_origin,
        learning_object=learningObject
    )

    return soup_data, page_adapted


def save_paragraph(tag_identify, tag, page_id, class_uuid):
    '''
    if len(tag.get('class', [])) > 0:
        tag['class'].append(class_uuid)
    else:
        tag['class'] = class_uuid
    '''

    tag['class'] = tag.get('class', []) + [class_uuid]

    TagPageLearningObject.objects.create(tag=tag_identify,
                                         text=str(tag.string),
                                         html_text=str(tag),
                                         page_learning_object=page_id,
                                         id_class_ref=class_uuid)


def __find_register_paragraph(soup_data, soup_data_website, page_adapted, page_adapted_website, tag_identify,
                              length_text):
    for tag in soup_data.find_all(tag_identify):
        if tag.string is not None:
            if len(tag.string) >= length_text:
                class_uuid = tag_identify + '-' + getUUID()
                parent = tag.find_parent(class_='UDLcontentIdevice')
                if parent is not None:
                    content_block = tag.find_parent(class_='exe-udlContent-block')
                    udl_facilitada = content_block.find(class_='exe-udlContent-content-simplified')
                    if udl_facilitada is not None:
                        metadata.save_metadata_paragraph(page_adapted.learning_object.path_xml)
                    else:
                        if soup_data_website is not None:
                            tag_webdata = soup_data_website.find(lambda
                                                                     tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())
                            if tag_webdata is not None:
                                save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                        save_paragraph(tag_identify, tag, page_adapted, class_uuid)
                else:
                    if soup_data_website is not None:
                        tag_webdata = soup_data_website.find(lambda
                                                                 tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())
                        if tag_webdata is not None:
                            save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                    save_paragraph(tag_identify, tag, page_adapted, class_uuid)


def web_scraping_paragraph(soup_data, page_adapted, file, soup_data_website, page_adapted_website, file_website):
    """
    Exatraccion de los parrafos de cada pagina html,
    se crea un ID unico, para identificar cada elemento

    :param file_website:
    :param page_adapted_website:
    :param soup_data_website:
    :param str soup_data: contiene el codigo html de la pagina
    :param int page_adapted: id de la pagina
    :param str file: directorio de la pagina

    """
    tag_identify = "p"
    length_text = 200
    ''' 
    for tag in soup_data.find_all(tag_identify):
        if tag.string is not None:
            if len(tag.string) >= length_text:
                class_uuid = tag_identify + '-' + getUUID()
                parent = tag.find_parent(class_='UDLcontentIdevice')
                if parent is not None:
                    udl_facilitada = parent.find(class_='exe-udlContent-content-simplified')
                    if udl_facilitada is not None:
                        metadata.save_metadata_paragraph(page_adapted.learning_object.path_xml)
                        #print(udl_facilitada)
                    else:
                        # enmetodo a parte
                        if soup_data_website is not None:
                            tag_webdata = soup_data_website.find(lambda
                                                                     tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())
                            if tag_webdata is not None:
                                save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                        save_paragraph(tag_identify, tag, page_adapted, class_uuid)
                else:
                    # enmetodo a parte
                    if soup_data_website is not None:
                        tag_webdata = soup_data_website.find(lambda 
                                                                tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())
                        if tag_webdata is not None:
                            save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                    save_paragraph(tag_identify, tag, page_adapted, class_uuid)
    '''
    __find_register_paragraph(soup_data, soup_data_website, page_adapted, page_adapted_website, tag_identify,
                              length_text)
    tag_identify = "span"
    '''
    for tag in soup_data.find_all(tag_identify):
        if tag.string is not None:
            if len(tag.string) >= length_text:
                class_uuid = tag_identify + '-' + getUUID()

                parent = tag.find_parent(class_='UDLcontentIdevice')
                if parent is not None:
                    udl_facilitada = parent.find(class_='exe-udlContent-content-simplified')
                    if udl_facilitada is not None:
                        metadata.save_metadata_paragraph(page_adapted.learning_object.path_xml)

                    else:
                        # enmetodo a parte
                        if soup_data_website is not None:
                            tag_webdata = soup_data_website.find(
                                lambda
                                    tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())

                            if tag_webdata is not None:
                                save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                        save_paragraph(tag_identify, tag, page_adapted, class_uuid)
                else:
                    # enmetodo a parte
                    if soup_data_website is not None:
                        tag_webdata = soup_data_website.find(
                            lambda
                                tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())

                        if tag_webdata is not None:
                            save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                    save_paragraph(tag_identify, tag, page_adapted, class_uuid)

    '''
    __find_register_paragraph(soup_data, soup_data_website, page_adapted, page_adapted_website, tag_identify,
                              length_text)
    tag_identify = "li"
    '''
    for tag in soup_data.find_all(tag_identify):
        if tag.string is not None:
            if len(tag.string) >= length_text:
                class_uuid = tag_identify + '-' + getUUID()

                parent = tag.find_parent(class_='UDLcontentIdevice')
                if parent is not None:
                    udl_facilitada = parent.find(class_='exe-udlContent-content-simplified')
                    if udl_facilitada is not None:
                        metadata.save_metadata_paragraph(page_adapted.learning_object.path_xml)
                        # print(udl_facilitada)

                    else:
                        # enmetodo a parte
                        if soup_data_website is not None:
                            tag_webdata = soup_data_website.find(
                                lambda
                                    tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())

                            if tag_webdata is not None:
                                save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                        save_paragraph(tag_identify, tag, page_adapted, class_uuid)
                else:
                    # enmetodo a parte
                    if soup_data_website is not None:
                        tag_webdata = soup_data_website.find(
                            lambda
                                tag_find: tag_find.name == tag_identify and tag.get_text().strip() in tag_find.get_text().strip())

                        if tag_webdata is not None:
                            save_paragraph(tag_identify, tag_webdata, page_adapted_website, class_uuid)

                    save_paragraph(tag_identify, tag, page_adapted, class_uuid)
    '''
    __find_register_paragraph(soup_data, soup_data_website, page_adapted, page_adapted_website, tag_identify,
                              length_text)

    generate_new_htmlFile(soup_data, file)
    if soup_data_website is not None:
        generate_new_htmlFile(soup_data_website, file_website['file'])


def webs_scraping_img(soup_data, page_adapted, file, directory, request_host, soup_data_website, page_adapted_website,
                      file_website, path_xml):
    """
    Vamos a extraer el alt de las imagenes y crear clases en las imagenes


    :param file_website:
    :param page_adapted_website:
    :param soup_data_website:
    :param soup_data: contiene el texto html generado por BeautifulSoup
    :param page_adapted: id de la pagina
    :param file: nombre del archivo
    :param directory:  directorio del archivo
    :param request_host: direccion del host
    :param path_xml: archivo xml de metadatos.
    """

    tag_identify = "img"
    attribute_img = "src"

    for tag in soup_data.find_all(tag_identify):
        # save metadata image

        metadata.save_metadata_img(path_xml)

        class_uuid = tag_identify + '-' + getUUID()
        # agregar a la etiqueta website

        if soup_data_website is not None:
            tag_webdata = soup_data_website.find("img", {"src": tag.get('src', []), "alt": tag.get('alt', [])})

            if tag_webdata is not None:
                save_tag_img(tag_webdata, class_uuid, tag_identify, attribute_img, page_adapted_website, directory,
                             request_host)

        save_tag_img(tag, class_uuid, tag_identify, attribute_img, page_adapted, directory, request_host)

    generate_new_htmlFile(soup_data, file)
    if soup_data_website is not None:
        generate_new_htmlFile(soup_data_website, file_website['file'])


def save_tag_img(tag, class_uuid, tag_identify, attribute_img, page_adapted, directory, request_host):
    path_split = split_path(page_adapted.preview_path)
    tag['class'] = tag.get('class', []) + [class_uuid]
    text_alt = tag.get('alt', '')
    tag['alt'] = text_alt
    tag['tabindex'] = "1"

    tag_page = TagPageLearningObject.objects.create(
        tag=tag_identify,
        text=str(text_alt),
        html_text=str(tag),
        page_learning_object=page_adapted,
        id_class_ref=class_uuid
    )

    link_img = tag.get('src', '')
    if "https://" in str(link_img) or "http://" in str(link_img):
        data_attribute_path = str(tag.get('src', ''))
    else:
        data_attribute_path = str(os.path.join(request_host, directory, tag.get('src', '')))

    path_preview = get_path_preview(tag.get('src', ''), path_split)

    data_attribute = DataAttribute(
        attribute=attribute_img,
        data_attribute=path_preview,
        tag_page_learning_object=tag_page,
        type=tag_identify
    )
    data_attribute.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos

    TagAdapted.objects.create(
        type=tag_identify,
        text=str(text_alt),
        html_text=str(tag),
        id_ref=class_uuid,
        path_src=data_attribute_path,
        tag_page_learning_object=tag_page
    )


def webs_scraping_video(soup_data, page_adapted, file, tag_identify, directory, request_host, soup_data_website,
                        page_adapted_website, file_website):
    """
    Vamos a extraer el el src de los videos y audios

    :param file_website:
    :param page_adapted_website:
    :param soup_data_website:
    :param soup_data: contiene el texto html generado por BeautifulSoup
    :param page_adapted: id de la pagina
    :param file: nombre del archivo
    :param tag_identify: identificador para los elementos html
    :param request_host: direccion del host
    :param directory: directorio del archivo
    """

    attribute_src = "src"

    for tag in soup_data.find_all(tag_identify):
        class_uuid = tag_identify + '-' + getUUID()

        if soup_data_website is not None:
            tag_webdata = soup_data_website.find(
                lambda tag_find: tag_find.name == "video" and tag.findChild("source").get("src",
                                                                                          '') in tag_find.findChild(
                    "source").get("src", '') and tag.findChild("source").get("type", '') in tag_find.findChild(
                    "source").get("type", ''))

            if tag_webdata is not None:
                save_video_tag(tag_webdata, class_uuid, tag_identify, attribute_src, page_adapted_website, directory)

        save_video_tag(tag, class_uuid, tag_identify, attribute_src, page_adapted, directory)

    generate_new_htmlFile(soup_data, file)
    if soup_data_website is not None:
        generate_new_htmlFile(soup_data_website, file_website['file'])


def save_video_tag(tag, class_uuid, tag_identify, attribute_src, page_adapted, directory):
    path_split = split_path(page_adapted.preview_path)
    tag['class'] = tag.get('class', []) + [class_uuid]

    tag_page = TagPageLearningObject.objects.create(
        tag=tag_identify,
        html_text=str(tag),
        page_learning_object=page_adapted,
        id_class_ref=class_uuid
    )

    # subtag = tag.find_all('source')
    subtag = tag.findChild('source')

    path_preview = get_path_preview(subtag.get('src', ''), path_split)

    # path_preview = os.path.join(request_host, directory, str(subtag.get('src'))).replace("\\", "/")

    if env('PROD'):
        path_preview = path_preview.replace("http://", "https://")

    path_system = os.path.join(BASE_DIR, directory, str(subtag.get('src', '')))

    data_attribute = DataAttribute(
        attribute=attribute_src,
        data_attribute=str(subtag.get('src', '')),
        type=str(subtag.get('type', '')),
        tag_page_learning_object=tag_page,
        path_preview=path_preview,
        path_system=path_system,
        source="local"
    )

    data_attribute.save()
    # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos


def webs_scraping_audio(soup_data, page_adapted, file, tag_identify, directory, request_host, soup_data_website,
                        page_adapted_website, file_website):
    """
    Vamos a extraer el el src de los videos y audios

    :param file_website:
    :param page_adapted_website:
    :param soup_data_website:
    :param soup_data: contiene el texto html generado por BeautifulSoup
    :param page_adapted: id de la pagina
    :param file: nombre del archivo
    :param tag_identify: identificador para los elementos html
    :param request_host: direccion del host
    :param directory: directorio del archivo

    """

    for tag in soup_data.find_all(tag_identify):
        class_uuid = tag_identify + '-' + getUUID()
        if soup_data_website is not None:
            tag_webdata = find_tag_in_webpage(tag, soup_data_website)

            if tag_webdata is not None:
                save_tag_audio(tag_webdata, class_uuid, tag_identify, page_adapted_website, directory)

        save_tag_audio(tag, class_uuid, tag_identify, page_adapted, directory)

    generate_new_htmlFile(soup_data, file)
    if soup_data_website is not None:
        generate_new_htmlFile(soup_data_website, file_website['file'])


def find_tag_in_webpage(tag, soup_data_website):
    src = tag.get('src', None)
    if src is None:
        tag_webdata = soup_data_website.find(
            lambda tag_find: tag_find.name == "audio" and
                             tag.findChild("source").get("src", '') == tag_find.findChild("source").get("src", '') and
                             tag.findChild("source").get("type", '') == tag_find.findChild("source").get("type", '') and
                             tag.findChild("source").get("class", []) == tag_find.findChild("source").get("class", []))
    else:
        tag_webdata = soup_data_website.find(
            lambda tag_find: tag_find.name == "audio" and
                             tag.get("src", '') == tag_find.get("src", '') and
                             tag.get("type", '') == tag_find.get("type", '') and
                             tag.get("class", []) == tag_find.get("class", []))
    return tag_webdata


def save_tag_audio(tag, class_uuid, tag_identify, page_adapted, directory):
    src = tag.get('src', '')
    path_split = split_path(page_adapted.preview_path)
    tag['class'] = tag.get('class', []) + [class_uuid]
    tag_page = TagPageLearningObject.objects.create(
        tag=tag_identify,
        html_text=str(tag),
        page_learning_object=page_adapted,
        id_class_ref=class_uuid
    )

    if src is not None:
        path_preview = get_path_preview(tag.get('src', ''), path_split)
    else:
        child_src = tag.findChild("source").get("src", '')
        if child_src is None:
            return
        path_preview = get_path_preview(child_src, path_split)

    data_attribute = DataAttribute.objects.create(
        attribute='src',
        data_attribute=path_preview,
        tag_page_learning_object=tag_page,
        type=tag_identify,
        path_system=str(os.path.join(BASE_DIR, directory, tag.get('src', ''))),
    )


def webs_scraping_iframe(file_beautiful_soup, page_adapted, file, soup_data_website, page_adapted_website,
                         file_website):
    """
    Vamos a extraer el src de los iframses incrustados de videos

    :param file_website:
    :param page_adapted_website:
    :param soup_data_website:
    :param file_beautiful_soup: contiene el texto html generado por BeautifulSoup
    :param page_adapted: id de la pagina
    :param file: directorio del archivo

    """

    tag_identify = "iframe"
    attribute_src = "src"

    for tag in file_beautiful_soup.find_all(tag_identify):
        if '.com' not in str(tag.get('src', '')):
            continue

        class_uuid = tag_identify + '-' + getUUID()

        if soup_data_website is not None:
            tag_webdata = soup_data_website.find(tag_identify, {"src": tag.get('src', []), "alt": tag.get('alt', [])})

            if tag_webdata is not None:
                save_tag_iframe(tag_webdata, class_uuid, tag_identify, attribute_src, page_adapted_website)

        save_tag_iframe(tag, class_uuid, tag_identify, attribute_src, page_adapted)

    generate_new_htmlFile(file_beautiful_soup, file)
    if soup_data_website is not None:
        generate_new_htmlFile(soup_data_website, file_website['file'])


def save_tag_iframe(tag, class_uuid, tag_identify, attribute_src, page_adapted):
    """

    :param tag:
    :param class_uuid:
    :param tag_identify:
    :param attribute_src:
    :param page_adapted:
    :return:
    """

    tag['class'] = tag.get('class', []) + [class_uuid]
    text_title = tag.get('title', '')
    tag['title'] = text_title

    tag_page = TagPageLearningObject.objects.create(
        tag=tag_identify,
        text=str(text_title),
        html_text=str(tag),
        page_learning_object=page_adapted,
        id_class_ref=class_uuid
    )

    domain = urlparse(str(tag.get('src', ''))).netloc

    data_attribute = DataAttribute(
        attribute=attribute_src,
        data_attribute=str(tag.get('src', '')),
        tag_page_learning_object=tag_page,
        path_preview=str(tag.get('src', '')),
        source=domain
    )
    data_attribute.save()  # Aplicar bulck create para evitar hacer peticiones constantes a la base de datos


def generate_new_htmlFile(file_beautiful_soup, path):
    """
    Genera un nuevo archivo con los atributos editados

    :param file_beautiful_soup: archivo generado por BeautifulSoup
    :param path: directorio en donde se encuentra ubicado el archivo
    """
    '''
    html = file_beautiful_soup.prettify('utf-8')
    new_direction = path
    if os.path.exists(new_direction):
        with open(new_direction, "wb") as file:
            file.write(html)
    else:
        os.mkdir(new_direction)
        with open(new_direction, "wb") as file:
            file.write(html)
    '''

    new_direction = path
    if os.path.exists(new_direction):
        if file_beautiful_soup is not None:
            with open(new_direction, "w", encoding="utf-8") as file:
                file.write(str(file_beautiful_soup))
    else:
        os.mkdir(new_direction)
        if file_beautiful_soup is not None:
            with open(new_direction, "w", encoding="utf-8") as file:
                file.write(str(file_beautiful_soup))


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


def templateAdaptationTag():
    """
    Template del contenedor HTML para el botón de audio.

    :return: (soup_data, id_ref) Instancia Beautifull de HTML y la referencia id.
    """
    id_ref = getUUID()
    tag_text_Adapted = """
                <div id="%s" class="text-adaptation">
                      
                </div>
            """ % id_ref
    soup_data = BeautifulSoup(tag_text_Adapted, 'html.parser')

    return soup_data, id_ref


def templateAdaptionImage(original_tag, id_class_ref):
    """
    Crea un nuevo template de la adapatacion de imagenes

    :param original_tag: html obtenido por una filtracion con webscraping
    :param id_class_ref: id de referencia donde para encontrar el elemento en HTML

    """
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


def templateAdaptedAudio(original_tag_audio, id_class_ref):
    """
    Crea un template que envuelve el codigo de audio en una DIV para adaptarla al HTML

    :param original_tag_audio: texto HTLM que contiene la etiqueta audio <audio>...</audio>
    :param id_class_ref: id de referencia donde para encontrar el elemento en HTML

    """
    tag_figure_new = """
            <div class="{0}" style="text-align: justify;">
                {1}
             </div>
            """.format(id_class_ref, str(original_tag_audio))
    tag_figure_new = BeautifulSoup(tag_figure_new, 'html.parser')
    return tag_figure_new


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


def templateAdaptedAudioButton(id_class_ref, audio_src, dir_len):
    """
    Se crea un template para generar el boton de texto a audio

    :param id_class_ref: id de referencia donde para encontrar el elemento en HTML
    :param audio_src: path src donde se encuentra ubicado el audio
    :param dir_len:  representacion de la logitud del directorio "../../"

    """
    audio_src = get_directory_resource(dir_len) + audio_src
    button_tag_id = getUUID()
    tag_audio = """
    <div class="tooltip audio-container" id="{0}">
        <input class="audio" type="image" onclick='audioAdaptationEvent("{1}", "{2}", this)' src="{3}oer_resources/text_adaptation/audio-on.svg" aria-label="Convertir a audio" />
        <span class="tooltiptext">Convertir a audio</span>
     </div>   
    """.format(button_tag_id, audio_src, id_class_ref, get_directory_resource(dir_len))
    soup_data = BeautifulSoup(tag_audio, 'html.parser')
    return soup_data, button_tag_id


def convertElementBeautifulSoup(html_code):
    """
    Pasar codigo HTML con BeautifulSoup

    :param html_code: texto en HTML para convertirlo con BeautifulSoup

    """
    return BeautifulSoup(html_code, 'html.parser')


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


''' 
def find_xml_in_directory(directory):
    print("find_xml_in_directory")
    file_xml = None
    bs_data_xml = None
    type_standard = ""
    print("directory", directory)
    print("os.walk(directory)", os.walk(os.path.join(BASE_DIR, directory)))
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, directory)):
        print("files", files)
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                print("file_path", file_path)
                bs_data = generateBeautifulSoupFile(file_path)
                data = bs_data.find("lom")
                print("data", data)
                if data is not None:
                    file_xml = file_path
                    bs_data_xml = bs_data
                    type_standard = "lom"
                elif bs_data.find("lomes:lom"):
                    file_xml = file_path
                    bs_data_xml = bs_data
                    type_standard = "lomes:lom"
    return file_xml, bs_data_xml, type_standard
'''

'''
def save_metadata_in_xml(path_directory, areas):
    print("save_metadata_in_xml")
    file_xml, bs_data_xml, type_standard = find_xml_in_directory(path_directory)
    print("file_xml", file_xml)
    print("bs_data_xml", bs_data_xml)
    print("type_standard", type_standard)
    if file_xml is None and bs_data_xml is None:
        return
    metadata_filter = meta.get_metadata(areas)

    if type_standard == "lom" or type_standard == "lomes:lom":
        if type_standard == "lom":
            lom_data = bs_data_xml.find("lom")
        elif type_standard == "lomes:lom":
            lom_data = bs_data_xml.find("lomes:lom")

        for metadata in metadata_filter:
            print("metadata", metadata)
            for data in metadata["metadata"]:
                print("data", data)

                bs_data = lom_data.find("accesibility")
                if bs_data is None and (data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):

                    lom_data.insert(-1, BeautifulSoup("<accesibility></accesibility>", 'html.parser'))
                    bs_data = lom_data.find("accesibility")

                    # Creacion de la descripcion de accesibilidad
                    bs_data_descripcion = bs_data.find("description")
                    if bs_data_descripcion is None:
                        # Insertar la descripcion para la etiqueta de accesibilidad
                        bs_data.insert(0, BeautifulSoup(
                            "<description language='es'> Adaptado para accesibilidad </description>", "html.parser"))

                elif not bs_data == None and (
                        data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                    # Creacion de la descripcion de accesibilidad
                    bs_data_descripcion = bs_data.find("description")
                    if bs_data_descripcion is None:
                        # Insertar la descripcion para la etiqueta de accesibilidad
                        bs_data.insert(0, BeautifulSoup(
                            "<description language='es'> Adaptado para accesibilidad </description>", "html.parser"))

                property_data = bs_data.find(data["property"].lower())
                if property_data is None and (
                        data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                    bs_data.append(
                        BeautifulSoup("<" + data["property"].lower() + "></" + data["property"].lower() + ">",
                                      'html.parser'))
                elif not property_data == None and (
                        data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                    pass

                try:
                    feature_data = property_data.find(data["property"])
                    if data["type"] not in str(feature_data) and (
                            data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                        feature_data.append(
                            BeautifulSoup(""" <value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser'))
                except:
                    if data["type"] not in str(property_data) and property_data is not None and (
                            data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                        property_data.append(
                            BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser'))

                # Etiqueta classification
                bs_data_descripcion = lom_data.find("classification")
                if bs_data_descripcion is None and data["property"].lower() == "alignmenttype":
                    lom_data.insert(-1, BeautifulSoup("<classification></classification>", 'html.parser'))
                    bs_data_classification = lom_data.find("classification")
                    bs_data_classification.insert(0, BeautifulSoup(" <purpose uniqueElementName='purpose'></purpose>",
                                                                   'html.parser'))
                    bs_data_purpose = bs_data_classification.find("purpose")
                    bs_data_purpose.append(
                        BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                      'html.parser'))
                elif not bs_data_descripcion == None and data["property"].lower() == "alignmenttype":
                    bs_data_descripcion_ux = bs_data_descripcion.find("purpose")
                    if bs_data_descripcion_ux is None:
                        bs_data_classification.insert(0,
                                                      BeautifulSoup("<purpose uniqueElementName='purpose'></purpose>",
                                                                    'html.parser'))
                        bs_data_descripcion = bs_data_classification
                        bs_data_descripcion.append("purpose")
                        bs_data_descripcion.append(
                            BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser'))
                    else:
                        bs_data_descripcion.append(
                            BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser'))

                # etiqueta annotation ?
                bs_annotation = lom_data.find("annotation")
                if bs_annotation is None and data["property"].lower() == "accessmode":
                    lom_data.insert(-1, BeautifulSoup("<annotation></annotation>", 'html.parser'))
                    bs_accessmode = lom_data.find("annotation")
                    bs_accessmode_aux = bs_accessmode.find("accessmode")
                    if bs_accessmode_aux is None:
                        bs_accessmode.append(BeautifulSoup("<accessmode></accessmode>", 'html.parser'))
                        bs_accessmode_ux = bs_accessmode.find("accessmode")
                        bs_accessmode_ux.append(
                            BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser')
                        );
                    else:
                        bs_accessmode_ux.append(
                            BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser')
                        );
                elif not bs_annotation == None and data["property"].lower() == "accessmode":
                    bs_accessmode = bs_annotation.find("accessmode")
                    if bs_accessmode is None:
                        bs_annotation.append(BeautifulSoup("  <accessmode></accessmode>", 'html.parser'))
                        bs_accessmode_ux = bs_annotation.find("accessmode")
                        bs_accessmode_ux.append(
                            BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser')
                        );
                    else:
                        bs_accessmode_ux.append(
                            BeautifulSoup("""<value uniqueElementName="value">%s</value>""" % data["type"],
                                          'html.parser')
                        );

        generate_new_htmlFile(bs_data_xml, file_xml)
        return True
'''


def codeAxuliarLomesRespla():
    # elif type_standard == "lomes:lom":
    bs_data_xml = ""
    metadata_filter = ""
    lom_data = bs_data_xml.find("lomes:lom")
    for metadata in metadata_filter:
        for data in metadata["metadata"]:

            # Etoqueta accesibility
            bs_data = lom_data.find("lomes:accesibility")
            if bs_data is None and (
                    data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                lom_data.insert(-1, BeautifulSoup("<lomes:accesibility></lomes:accesibility>", 'html.parser'))
                bs_data = lom_data.find("lomes:accesibility")

                # Creacion de la descripcion de accesibilidad
                bs_data_descripcion = bs_data.find("lomes:description")
                if bs_data_descripcion is None:
                    # Insertar la descripcion para la etiqueta de accesibilidad
                    bs_data.insert(0, BeautifulSoup(
                        "<lomes:description language='es'> Adaptado para accesibilidad </lomes:description>",
                        "html.parser"))

            elif not bs_data == None and (
                    data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                # Creacion de la descripcion de accesibilidad
                bs_data_descripcion = bs_data.find("lomes:description")
                if bs_data_descripcion is None:
                    # Insertar la descripcion para la etiqueta de accesibilidad
                    bs_data.insert(0, BeautifulSoup(
                        "<lomes:description language='es'> Adaptado para accesibilidad </lomes:description>",
                        "html.parser"))

            property_data = bs_data.find(data["property"].lower())
            if property_data is None and (
                    data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                bs_data.append(
                    BeautifulSoup(
                        "<lomes:" + data["property"].lower() + "></lomes:" + data["property"].lower() + ">",
                        'html.parser'))
            elif not property_data == None and (
                    data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                pass

            try:
                feature_data = property_data.find(data["property"])
                if data["type"] not in str(feature_data) and (
                        data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                    feature_data.append(
                        BeautifulSoup(""" <lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser'))
            except:
                if data["type"] not in str(property_data) and property_data is not None and (
                        data["property"].lower() != "alignmenttype" and data["property"].lower() != "accessmode"):
                    property_data.append(
                        BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser'))

            # Etiqueta classification
            bs_data_descripcion = lom_data.find("lomes:classification")
            if bs_data_descripcion is None and data["property"].lower() == "alignmenttype":
                lom_data.insert(-1, BeautifulSoup("<lomes:classification></lomes:classification>", 'html.parser'))
                bs_data_classification = lom_data.find("lomes:classification")
                bs_data_classification.insert(0, BeautifulSoup(
                    " <lomes:purpose uniqueElementName='purpose'></lomes:purpose>", 'html.parser'))
                bs_data_purpose = bs_data_classification.find("lomes:purpose")
                bs_data_purpose.append(
                    BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                  'html.parser'))
            elif not bs_data_descripcion == None and data["property"].lower() == "alignmenttype":
                bs_data_descripcion_ux = bs_data_descripcion.find("lomes:purpose")
                if bs_data_descripcion_ux is None:
                    bs_data_classification.insert(0, BeautifulSoup(
                        "<lomes:purpose uniqueElementName='purpose'></lomes:purpose>", 'html.parser'))
                    bs_data_descripcion = bs_data_classification
                    bs_data_descripcion.append("lomes:purpose")
                    bs_data_descripcion.append(
                        BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser'))
                else:
                    bs_data_descripcion.append(
                        BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser'))

            # etiqueta annotation ?
            bs_annotation = lom_data.find("lomes:annotation")
            if bs_annotation is None and data["property"].lower() == "accessmode":
                lom_data.insert(-1, BeautifulSoup("<lomes:annotation></lomes:annotation>", 'html.parser'))
                bs_accessmode = lom_data.find("lomes:annotation")
                bs_accessmode_aux = bs_accessmode.find("lomes:accessmode")
                if bs_accessmode_aux is None:
                    bs_accessmode.append(BeautifulSoup("<lomes:accessmode></lomes:accessmode>", 'html.parser'))
                    bs_accessmode_ux = bs_accessmode.find("lomes:accessmode")
                    bs_accessmode_ux.append(
                        BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser')
                    );
                else:
                    bs_accessmode_ux.append(
                        BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser')
                    );
            elif not bs_annotation == None and data["property"].lower() == "accessmode":
                bs_accessmode = bs_annotation.find("lomes:accessmode")
                if bs_accessmode is None:
                    bs_annotation.append(BeautifulSoup("<lomes:accessmode></lomes:accessmode>", 'html.parser'))
                    bs_accessmode_ux = bs_annotation.find("lomes:accessmode")
                    bs_accessmode_ux.append(
                        BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser')
                    );
                else:
                    bs_accessmode_ux.append(
                        BeautifulSoup("""<lomes:value uniqueElementName="value">%s</lomes:value>""" % data["type"],
                                      'html.parser')
                    );
    file_xml = ""
    generate_new_htmlFile(bs_data_xml, file_xml)
    return True
