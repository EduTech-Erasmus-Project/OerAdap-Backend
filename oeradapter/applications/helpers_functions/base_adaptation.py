import copy
import glob
import json
import re
from zipfile import ZipFile
import environ
import webvtt
from unipath import Path
from . import beautiful_soup_data as bsd
from youtube_dl import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter
from vtt_to_srt.vtt_to_srt import vtt_to_srt
import shutil
import os
from os import remove, listdir
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import pathlib
from asgiref.sync import async_to_sync
from ..adaptation.VideoDownloader import YoutubeDLThread
from ..adaptation.serializers import TagsVideoSerializer
from ..adaptation.views import save_data_attribute
from ..learning_object.models import TagAdapted, Transcript, PageLearningObject
from channels.layers import get_channel_layer
import imgkit
from bs4 import BeautifulSoup as bs
from ..helpers_functions import base_adaptation as ba

channel_layer = get_channel_layer()
BASE_DIR = Path(__file__).ancestor(3)

env = environ.Env(
    PROD=(bool, False)
)
environ.Env.read_env(os.path.join(Path(__file__).ancestor(4), '.env'))


def save_uploaded_file(path, file, resources_directory, request):
    """Save file on folder the learning object"""
    try:
        path_system = os.path.join(path, file.name)
        with open(path_system, 'wb+', ) as file_destination:
            for chunk in file.chunks():
                file_destination.write(chunk)
    except Exception as e:
        print("Error: %s ." % e)

    path_preview = os.path.join(request._current_scheme_host, resources_directory, 'oer_resources', file.name).replace(
        "\\", "/")

    if env('PROD'):
        path_preview = path_preview.replace("http://", "https://")

    return path_preview, path_system


def remove_uploaded_file(path_system):
    """Remove and save file on folder the learning object"""
    os.remove(path_system)
    # return save_uploaded_file(path, file, resources_directory, request)


def copy_folder(path_origin, path_src):
    return shutil.copytree(path_origin, path_src)


def copy_folder_2(path_origin, path_src):
    directorio_Raiz = path_origin
    new_direction = path_src
    contenidos = os.listdir(directorio_Raiz)
    for elemento in contenidos:
        try:
            extension = pathlib.Path(elemento)
            if (extension.suffix != ".html"):
                src = os.path.join(directorio_Raiz, elemento)  # origen
                dst = os.path.join(new_direction, elemento)  # destino
                shutil.copy2(src, dst)
                # print("Correcto")
            return 'Se copio exitosamente'
        except:
            return 'Nose copiaron los datos'


def remove_folder(path):
    """Delete folder"""
    try:
        shutil.rmtree(path)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def move_folder(directory, path):
    """Add paragraph script on pages of learning object"""
    path_origin = os.path.join(BASE_DIR, 'resources', path)
    path_src = os.path.join(BASE_DIR, directory, 'oer_resources', path)
    return copy_folder(path_origin, path_src)


def add_files_adaptation(html_files, directory, button=False, paragraph_script=False, video=False, image=False,
                         root_dirs=None):
    """Add essential files of adaptation on learning object"""

    if button or video:
        """Add button adaptability on pages of learning objects"""
        for dir in root_dirs:
            path_origin = os.path.join(BASE_DIR, 'resources', 'uiAdaptability')
            path_src = os.path.join(dir, 'uiAdaptability')
            try:
                path_save = copy_folder(path_origin, path_src)
            except:
                pass

    if paragraph_script:
        move_folder(directory, 'text_adaptation')

    if image:
        move_folder(directory, 'lightbox')

    for file in html_files:
        soup_file = bsd.generateBeautifulSoupFile(file['file'])

        if button or video:
            headInfusion = bsd.templateInfusion(file['dir_len'])
            soup_file.head.insert(len(soup_file.head) - 1, headInfusion)

        if button:
            bodyInfusion = bsd.templateBodyButtonInfusion(file['dir_len'])
            soup_file.body.insert(1, bodyInfusion)

        if video and button == False:
            bodyInfusion = bsd.templateBodyVideoInfusion(file['dir_len'])
            soup_file.body.insert(1, bodyInfusion)

        if paragraph_script:
            head_adaptation, body_adaptation = bsd.templateTextAdaptation(file['dir_len'])
            soup_file.head.insert(len(soup_file.head) - 1, head_adaptation)
            soup_file.body.insert(len(soup_file.head) - 1, body_adaptation)

        if image:
            head_adaptation, body_adaptation = bsd.templateImageAdaptation(file['dir_len'])
            soup_file.head.insert(len(soup_file.head) - 1, head_adaptation)
            soup_file.body.insert(len(soup_file.head) - 1, body_adaptation)

        bsd.generate_new_htmlFile(soup_file, file['file'])


def remove_button_adaptation(html_files, directory):
    """Remove files and button of adaptation"""
    path = os.path.join(BASE_DIR, directory, 'oer_resources', 'uiAdaptability')
    remove_folder(path)

    for file in html_files:
        soup_file = bsd.generateBeautifulSoupFile(file['file'])
        bsd.generate_new_htmlFile(soup_file, file['file'])


def convertText_Audio(texo_adaptar, directory, id_ref, request):
    # Conversion de texto a audio
    s = gTTS(str(texo_adaptar), lang="es-us")
    path_src = 'oer_resources/' + id_ref + ".mp3"
    path_system = os.path.join(BASE_DIR, directory, 'oer_resources', id_ref + ".mp3")
    path_preview = os.path.join(request._current_scheme_host, directory, 'oer_resources', id_ref + ".mp3").replace(
        "\\", "/")

    if env('PROD'):
        path_preview = path_preview.replace("http://", "https://")

    s.save(path_system)

    return path_src, path_system, path_preview


def convertAudio_Text(path_init):
    root, extension = os.path.splitext(path_init)
    audio = root + ".wav"

    if extension == '.mp3':
        sound = AudioSegment.from_mp3(path_init)
        sound.export(audio, format="wav")
    elif extension == '.webm':
        sound = AudioSegment.from_file(path_init, format="webm")
        sound.export(audio, format="wav")
    elif extension == ".ogg":
        sound = AudioSegment.from_ogg(path_init)
        sound.export(audio, format="wav")
    elif extension == ".wav":
        audio = path_init
    elif extension == ".flv":
        sound = AudioSegment.from_flv(path_init)
        sound.export(audio, format="wav")
    else:
        raise Exception("Format not supported")

    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio) as source:
            info_audio = r.record(source)
            text_new = r.recognize_google(info_audio, language="es-ES")
        remove(audio)
        return text_new
    except Exception as e:
        remove(audio)
        raise e


def create_transcript(transcript, tag_adapted):
    Transcript.objects.create(
        src=transcript['src'],
        type=transcript['type'],
        srclang=transcript['srclang'],
        label=transcript['label'],
        source=transcript['source'],
        path_system=transcript['path_system'],
        tag_adapted=tag_adapted,
    )


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


def save_video_on_html(tag, video_template, page_learning_object):
    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
    tag_adaptation = file_html.find(tag.tag, tag.id_class_ref)

    tag_adaptation.replace_with(video_template)
    bsd.generate_new_htmlFile(file_html, page_learning_object.path)


def generate_transcript_youtube(video_url, video_title, path_adapted, request, dir_len):
    with YoutubeDL({}) as ydl:
        transcripts = []
        captions = []

        try:
            info_dict = ydl.extract_info(video_url, download=False)
            id_video = info_dict.get('id', None)
            transcript_list = YouTubeTranscriptApi.list_transcripts(id_video)
        except:
            # print("no supported transcriptions")
            return transcripts, captions

        try:
            transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
            transcripts, captions = save_transcript(transcript, path_adapted, video_title, transcripts, captions,
                                                    "manual", dir_len)
            if transcript.language_code != 'es':
                transcript_es = get_transcript_youtube(transcript_list, 'es')
            elif transcript.language_code != 'en':
                transcript_en = get_transcript_youtube(transcript_list, 'en')
        except:
            transcript_es = get_transcript_youtube(transcript_list, 'es')
            transcript_en = get_transcript_youtube(transcript_list, 'en')

        transcripts, captions = save_transcript(transcript_es, path_adapted, video_title, transcripts, captions,
                                                "automatic/youtube", dir_len)
        transcripts, captions = save_transcript(transcript_en, path_adapted, video_title, transcripts, captions,
                                                "automatic/youtube", dir_len)

        return transcripts, captions


def get_transcript_youtube(transcript_list, lang):
    transcript = transcript_list.find_transcript(['es', 'en'])
    return transcript.translate(lang)


def save_transcript(transcript, path_adapted, video_title, transcripts, captions, source, dir_len):
    # print("type transcript ", type(transcript))
    # print("type transcript 1", type(transcript.fetch()))

    vtt_formatterd = WebVTTFormatter().format_transcript(transcript.fetch())

    vtt_system = os.path.join(BASE_DIR, path_adapted, "oer_resources",
                              video_title + "_" + transcript.language_code + ".vtt")

    json_path = bsd.get_directory_resource(
        dir_len) + 'oer_resources/' + video_title + "_" + transcript.language_code + ".json"
    vtt_path = bsd.get_directory_resource(
        dir_len) + 'oer_resources/' + video_title + "_" + transcript.language_code + ".vtt"

    # print("path", vtt_system)

    with open(vtt_system, 'w+', encoding='utf-8') as json_file:
        json_file.write(vtt_formatterd)

    srt_file = convert_vtt_to_str(vtt_system)

    path_json = os.path.join(BASE_DIR, path_adapted, "oer_resources",
                             video_title + "_" + transcript.language_code + ".json")

    json_system = convert_str_to_json(srt_file, path_json)

    # print("json_system ", json_system)

    transcripts_obj = {
        "src": json_path,
        "type": "JSONcc",
        "srclang": transcript.language_code,
        "label": transcript.language,
        "source": source,
        "path_system": json_system,
    }
    transcripts.append(transcripts_obj)
    captions_obj = {
        "src": vtt_path,
        "type": "text/vtt",
        "srclang": transcript.language_code,
        "label": transcript.language,
        "source": source,
        "path_system": vtt_system
    }
    captions.append(captions_obj)

    return transcripts, captions


def get_object_captions_transcripts(json_src, vtt_src, language_code, language, source, json_system, vtt_system):
    transcript = {
        "src": json_src,
        "type": "JSONcc",
        "srclang": language_code,
        "label": language,
        "source": source,
        "path_system": json_system,
    }
    caption = {
        "src": vtt_src,
        "type": "text/vtt",
        "srclang": language_code,
        "label": language,
        "source": source,
        "path_system": vtt_system
    }
    return transcript, caption


def convert_str_to_vtt(path_str):
    webvttF = webvtt.from_srt(path_str)
    webvttF.save()
    return webvttF.file


def convert_vtt_to_str(path_vtt):
    vtt_to_srt(path_vtt)
    return path_vtt.replace(".vtt", ".srt")


# path_adapted, file_name
def convert_str_to_json(srt_string, path_json):
    srt_list = []

    # path_json = os.path.join(BASE_DIR, path_adapted, "oer_resources", file_name + ".json")
    srt_string = open(srt_string, 'r', encoding="utf8").read()
    idx = 1

    for line in srt_string.split('\n\n'):
        if line != '':
            try:
                index = int(re.match(r'\d+', line).group())
                if index == 0:
                    index = idx
                    idx = idx + 1
            except:
                index = idx
                idx = idx + 1
            try:
                pos = re.search(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+', line).span()
                content = re.sub('\r?\n', ' ', line[pos[1] + 1:])
            except:
                pass
            try:
                start_time_string = re.findall(r'(\d+:\d+:\d+,\d+) --> \d+:\d+:\d+,\d+', line)[0]
                end_time_string = re.findall(r'\d+:\d+:\d+,\d+ --> (\d+:\d+:\d+,\d+)', line)[0]
                start_time = start_time_string.replace(",", ".")
                end_time = end_time_string.replace(",", ".")
            except:
                pass

            srt_list.append({
                'index': index,
                'inTime': start_time,
                'outTime': end_time,
                'transcript': content
            })

    json_object = json.dumps(srt_list, indent=2, sort_keys=False, ensure_ascii=False)
    with open(path_json, "w", encoding="utf8") as outfile:
        outfile.write(json_object)

    return path_json


def save_file_on_system(file, path):
    with open(path, 'wb+', ) as file_destination:
        for chunk in file.chunks():
            file_destination.write(chunk)


def download_subtitles():
    pass


def check_files(directory_name):
    """
        Chequea si un directorio
        :param directory_name:
        :return 1 or 0:
        """
    if len(listdir(directory_name)) > 1:
        return 1
    elif len(listdir(directory_name)) == 1:
        return 0


def extract_zip_file(path, file):
    """
        Extrae un archivo zip en una ruta determinada
        :param path:
        :param file:
        :return:
        """
    try:
        file_name = file._name
        directory_extract = os.path.join(BASE_DIR, path, file_name.split('.')[0], file_name.split('.')[0] + "_origin")

        with ZipFile(file, 'r') as zip_file:
            zip_file.extractall(directory_extract)
            directory_origin = os.path.join(path, file_name.split('.')[0], file_name.split('.')[0] + "_origin")
            directory_adapted = os.path.join(path, file_name.split('.')[0], file_name.split('.')[0] + "_adapted")
            shutil.copytree(os.path.join(BASE_DIR, directory_origin), os.path.join(BASE_DIR, directory_adapted))
            zip_file.close()

        return directory_origin, directory_adapted
    except Exception as e:
        print("error in extract ", e)
        # raise Exception("Objeto de Aprendizaje aceptados por el adaptador es IMS y SCORM")


def compress_file(request, learning_object):
    path_folder = os.path.join(BASE_DIR, learning_object.path_adapted)
    archivo_zip = shutil.make_archive(path_folder, "zip", path_folder)
    path_zip_file = os.path.join(request._current_scheme_host, learning_object.path_adapted + '.zip').replace(
        "\\", "/")

    if env('PROD'):
        path_zip_file = path_zip_file.replace("http://", "https://")

    return path_zip_file


def take_screenshot(learning_object, page_learning_object):
    try:
        options = {
            'format': 'png',
            'height': '1000',
            'width': '1000',
            'encoding': "UTF-8",
        }
        imgkit.from_url(page_learning_object.preview_path,
                        os.path.join(BASE_DIR, learning_object.path_adapted, 'img-prev.png'), options=options)

    except Exception as e:
        print(e)
        pass


def get_index_imsmanisfest(filename):
    if filename is None:
        return None

    result = None
    try:
        # print("filename[:-1]", filename[:-1])
        if filename[:-1] != BASE_DIR:
            with open(filename, "r") as file:
                content = file.readlines()
                content = "".join(content)
                bs_content = bs(content, "lxml")
                resource = bs_content.find("file")
                if resource:
                    result = resource['href']
                return result
    except Exception as e:
        # print("error get_index_imsmanisfest", e)
        return None


def findXmlIMSorSCORM(path):
    try:
        files_standar_xml = ["imsmanifest.xml", "imsmanifest_nuevo.xml", "catalogacionLomes.xml"]
        os.chdir(path)
        for file in glob.glob("*.xml"):
            if file in files_standar_xml:
                return get_index_imsmanisfest(os.path.join(path, file))
        return None
    except:
        return None
