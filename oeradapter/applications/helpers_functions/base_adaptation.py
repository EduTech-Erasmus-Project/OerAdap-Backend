import json
import re
import threading
import time
from zipfile import ZipFile

import shortuuid
import webvtt
from unipath import Path
from . import beautiful_soup_data as bsd
from youtube_dl import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter
from vtt_to_srt.vtt_to_srt import vtt_to_srt
from geopy.geocoders import Nominatim
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
from ..learning_object.models import MetadataInfo, TagAdapted, Transcript
import pyttsx3
from queue import Queue
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

BASE_DIR = Path(__file__).ancestor(3)

PROD = None
with open(os.path.join(Path(__file__).ancestor(4), "prod.json")) as f:
    PROD = json.loads(f.read())


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

    if PROD['PROD']:
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


def add_files_adaptation(html_files, directory, button=False, paragraph_script=False, video=False, root_dirs=None):
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
        """Add paragraph script on pages of learning object"""
        path_origin = os.path.join(BASE_DIR, 'resources', 'text_adaptation')
        path_src = os.path.join(BASE_DIR, directory, 'oer_resources', 'text_adaptation')
        path_save = copy_folder(path_origin, path_src)

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

    if PROD['PROD']:
        path_preview = path_preview.replace("http://", "https://")

    s.save(path_system)
    # time.sleep(10)

    """
    path_src = 'oer_resources/' + id_ref + ".mp3"
    path_system = os.path.join(BASE_DIR, directory, 'oer_resources', id_ref + ".mp3")
    path_preview = os.path.join(request._current_scheme_host, directory, 'oer_resources', id_ref + ".mp3").replace(
        "\\", "/")

    if PROD['PROD']:
        path_preview = path_preview.replace("http://", "https://")

    engine = pyttsx3.init()
    # Control the rate. Higher rate = more speed
    engine.setProperty("rate", 150)
    text = str(texo_adaptar)
    engine.save_to_file(text, path_system)
    engine.runAndWait()
    """

    return path_src, path_system, path_preview


def convertAudio_Text(path_init):
    audioI = path_init.replace('\\\\', '\\')
    is_wav = False;

    # Verificar la extencion del archivo.

    root, extension = os.path.splitext(path_init)

    if extension == '.mp3':
        print('ES MP3')
        sound = AudioSegment.from_mp3(str(audioI))
    elif extension == '.webm':
        sound = AudioSegment.from_file(str(audioI), format="webm")
    elif extension == ".ogg":
        sound = AudioSegment.from_ogg(str(audioI))
    elif extension == ".wav":
        is_wav = True;
        pass;
    elif extension == ".flv":
        sound = AudioSegment.from_flv(str(audioI))

    if (is_wav == True):
        audio = path_init
    else:
        audio = path_init + ".wav"

    sound.export(audio, format="wav")

    r = sr.Recognizer()

    with sr.AudioFile(audio) as source:
        info_audio = r.record(source)
        text_new = r.recognize_google(info_audio, language="es-ES")

    remove(audio)
    # time.sleep(10)
    return text_new


'''
def add_paragraph_script(html_files, directory):
    pass


def remove_paragraph_script(html_files):
    pass
'''


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


def download_video1(tag, data_attribute, learning_object, request):
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

        # guardar video
        try:
            file_html = bsd.generateBeautifulSoupFile(tag.page_learning_object.path)
            tag_adaptation = file_html.find(tag.tag, tag.id_class_ref)

            uid = bsd.getUUID()
            tag_adapted = TagAdapted.objects.create(
                type="video",
                id_ref=uid,
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

                # transform html
                video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                             transcripts, uid)

                tag_adaptation.replace_with(video_template)
                bsd.generate_new_htmlFile(file_html, tag.page_learning_object.path)

                save_data_attribute(data_attribute, path_src, path_system, path_preview)

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
            # transform html
            save_data_attribute(data_attribute, path_src, path_system, path_preview)

            video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                         transcripts, uid)
            tag_adaptation.replace_with(video_template)
            bsd.generate_new_htmlFile(file_html, tag.page_learning_object.path)

            tag.adapting = False
            tag.save()

            async_to_sync(channel_layer.group_send)("channel_" + str(tag.id),
                                                    {"type": "send_new_data", "text": {
                                                        "status": "ready_tag_adapted",
                                                        "type": "transcript",
                                                        "message": "La fuente no tiene subtítulos.",
                                                        "data": serializer.data
                                                    }})


'''

        else:
                async_to_sync(channel_layer.group_send)("channel_" + str(tag.id),
                                                        {"type": "send_new_data", "text": {
                                                            "status": "no_supported_transcript",
                                                            "type": "transcript",
                                                            "message": "No se pudo descargar los subtítulos.",
                                                            "data": serializer.data
                                                        }})
                                                        
try:
    # socket_consumer = VideoConsumer
    # path_system, path_preview, path_src, tittle = download_video_youtubedl(video_url, directory_adapted, request)
    # return path_system, path_preview, path_src, tittle


    


    pass
except Exception as e:
    async_to_sync(channel_layer.group_send)("channel_" + str(tag.id), {"type": "send_new_data", "text": {
        "status": "error",
        "type": "transcript",
        "message": e.__str__(),
    }})
    raise e
'''

'''
def download_video(video_url, type_video, source, directory_adapted, request):
    try:



        # socket_consumer = VideoConsumer
        # path_system, path_preview, path_src, tittle = download_video_youtubedl(video_url, directory_adapted, request)
        # return path_system, path_preview, path_src, tittle
        dl = YoutubeDLThread(video_url, directory_adapted, request)
        path_system, path_preview, path_src, tittle = dl.download()
        print("report download", path_system, path_preview, path_src, tittle)
        return path_system, path_preview, path_src, tittle

        # return None, None, None, None
    except Exception as e:
        raise e
'''
'''
def process_bytes(progress):
    q = Queue()
    job_done = object()

    if progress["status"] == "downloading":
        # byte_chunk = progress["downloaded_bytes"]
        # q.put(byte_chunk)
        # q.join()
        # print("progress downloading", progress)

        channel_layer = get_channel_layer()
        channel_layer.send("channel_name", {
            "type": "chat.message",
            "text": "Hello there!",
        })

    elif progress["status"] == "finished":
        # q.put(job_done)
        print("progress finished", progress)
        # handle_finished(progress)


class MyLogger(object):
    def debug(self, msg):
        print("msg logger", json.dumps(msg))
        channel_layer = get_channel_layer()
        channel_layer.send("channel_name", {
            "type": "chat.message",
            "text": "Hello there!",
        })
'''
'''
def download_video_youtubedl(video_url, directory_adapted, request):
    video_id_title = str(shortuuid.ShortUUID().random(length=8))
    path_system = os.path.join(BASE_DIR, directory_adapted, 'oer_resources')

    ydl_opts = {
        'outtmpl': path_system + '/' + video_id_title + '.%(ext)s'.strip(),
        'format': '(mp4)[height<=480]',
        # 'bestvideo[height<=480]+bestaudio/best[height<=480]', #'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'noplaylist': True,
        # 'extract-audio': True,
        'logger': MyLogger(),
        'progress_hooks': [process_bytes],
        # 'audio-format': 'mp3',

    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)

            # print("in_download_archive", ydl.in_download_archive(info_dict))
            # print("info_dict", info_dict)
            filename = ydl.prepare_filename(info_dict)
            print("filename", filename)
            title = video_id_title  # re.sub("[^A-Za-z0-9]", "_", info_dict.get('title', None))
            # print("title: ", title)
            path_system = filename
            path_split = path_system.split(os.sep)

            path_preview = os.path.join(request._current_scheme_host, directory_adapted, 'oer_resources',
                                        path_split[-1]).replace("\\", "/")

            if PROD['PROD']:
                path_preview = path_preview.replace("http://", "https://")

            path_src = 'oer_resources/' + path_split[-1]

            print("path_preview: ", path_preview)

            return path_system, path_preview, path_src, title

    except Exception as e:
        print("error", e)
        raise e
'''


def generate_transcript_youtube(video_url, video_title, path_adapted, request, dir_len):
    with YoutubeDL({}) as ydl:
        transcripts = []
        captions = []

        try:
            info_dict = ydl.extract_info(video_url, download=False)
            id_video = info_dict.get('id', None)
            transcript_list = YouTubeTranscriptApi.list_transcripts(id_video)
        except:
            print("no supported transcriptions")
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
    print("type transcript ", type(transcript))
    print("type transcript 1", type(transcript.fetch()))

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

    path_json = os.path.join(BASE_DIR, path_adapted, "oer_resources", video_title + "_" + transcript.language_code + ".json")

    json_system = convert_str_to_json(srt_file, path_json)

    print("json_system ", json_system)

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


def extract_zip_file(path, file_name, file):
    """
        Extrae un archivo zip en una ruta determinada
        :param path:
        :param file_name:
        :param file:
        :return:
        """
    var_name = os.path.join(path, file_name)
    if var_name.find('.zip.zip') >= 0:
        test_file_aux = file_name.split('.')[0]
        test_file_aux = test_file_aux.rstrip(".zip")
    else:
        test_file_aux = file_name.split('.')[0]

    directory_origin = os.path.join(path, file_name.split('.')[0], test_file_aux + "_origin")

    with ZipFile(file, 'r') as zip_file:
        # zip.printdir()
        zip_file.extractall(directory_origin)

    if check_files(directory_origin) == 0:
        aux_path_o = os.path.join(directory_origin, listdir(directory_origin)[0])
        source = aux_path_o
        destination = directory_origin
        files = os.listdir(source)
        for file in files:
            new_path = shutil.move(f"{source}/{file}", destination)
            # print(new_path)
        os.rmdir(aux_path_o)
        # print("directory_name", str(directory_origin))

    directory_adapted = os.path.join(path, file_name.split('.')[0], test_file_aux + "_adapted")
    shutil.copytree(directory_origin, directory_adapted)

    return directory_origin, directory_adapted


def compress_file(request, learning_object, count_images_count, count_paragraphs_count, count_videos_count,
                  count_audios_count):
    location = "Private request Api"
    browser = "Request Api"
    try:
        browser = str(request.data['browser'])
        laltitud = str(request.data['latitude'])
        longitud = str(request.data['longitude'])
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = str(geolocator.reverse(laltitud + "," + longitud))
    except Exception as e:
        print(e)

    metadataInfo = MetadataInfo.objects.create(
        browser=browser,
        country=location,
        text_number=count_paragraphs_count,
        video_number=count_videos_count,
        audio_number=count_audios_count,
        img_number=count_images_count,
    )

    path_folder = os.path.join(BASE_DIR, learning_object.path_adapted)
    archivo_zip = shutil.make_archive(path_folder, "zip", path_folder)
    new_path = os.path.join(request._current_scheme_host, learning_object.path_adapted + '.zip').replace(
        "\\", "/")

    if PROD['PROD']:
        new_path = new_path.replace("http://", "https://")

    # print("Creado el archivo:", new_path)

    return new_path
