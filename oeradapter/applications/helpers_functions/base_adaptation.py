from unipath import Path
from django.core.files.storage import FileSystemStorage
from . import beautiful_soup_data as bsd
from youtube_dl import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import Formatter
from youtube_transcript_api.formatters import JSONFormatter
from youtube_transcript_api.formatters import WebVTTFormatter

import shutil
import os

BASE_DIR = Path(__file__).ancestor(3)


def save_uploaded_file(path, file, resources_directory, request):
    """Save file on folder the learning object"""

    fs = FileSystemStorage(location=path)  # defaults to   MEDIA_ROOT
    filename = fs.save(file.name, file)
    save_path = os.path.join(request._current_scheme_host, resources_directory, 'oer_resources', filename).replace(
        "\\", "/")
    path_system = os.path.join(path, filename)
    return save_path, path_system


def remove_uploaded_file(path_system):
    """Remove and save file on folder the learning object"""
    os.remove(path_system)
    # return save_uploaded_file(path, file, resources_directory, request)


def copy_folder(path_origin, path_src):
    return shutil.copytree(path_origin, path_src)


def remove_folder(path):
    """Delete folder"""
    try:
        shutil.rmtree(path)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def add_files_adaptation(html_files, directory, button=False, paragraph_script=False, video=False):
    """Add essential files of adaptation on learning object"""

    if button or video:
        """Add button adaptability on pages of learning objects"""
        path_origin = os.path.join(BASE_DIR, 'resources', 'uiAdaptability')
        path_src = os.path.join(BASE_DIR, directory, 'oer_resources', 'uiAdaptability')
        path_save = copy_folder(path_origin, path_src)

        # print("path_save move folder", str(path_save))
    if paragraph_script:
        """Add paragraph script on pages of learning object"""
        path_origin = os.path.join(BASE_DIR, 'resources', 'text_adaptation')
        path_src = os.path.join(BASE_DIR, directory, 'oer_resources', 'text_adaptation')
        path_save = copy_folder(path_origin, path_src)
        # print("path_save move folder", str(path_save))

    for file in html_files:
        # directory_file = os.path.join(BASE_DIR, directory, file['file'])
        soup_file = bsd.generateBeautifulSoupFile(file['file'])

        if button or video:
            headInfusion = bsd.templateInfusion()
            soup_file.head.insert(len(soup_file.head) - 1, headInfusion)

        if button:
            bodyInfusion = bsd.templateBodyButtonInfusion()
            soup_file.body.insert(1, bodyInfusion)

        if video and button == False:
            bodyInfusion = bsd.templateBodyVideoInfusion()
            soup_file.body.insert(1, bodyInfusion)

        if paragraph_script:
            head_adaptation, body_adaptation = bsd.templateTextAdaptation()
            soup_file.head.insert(len(soup_file.head) - 1, head_adaptation)
            soup_file.body.insert(len(soup_file.head) - 1, body_adaptation)

        bsd.generate_new_htmlFile(soup_file, file['file'])
        # print(soup_file)


def remove_button_adaptation(html_files, directory):
    """Remove files and button of adaptation"""
    path = os.path.join(BASE_DIR, directory, 'oer_resources', 'uiAdaptability')
    remove_folder(path)

    for file in html_files:
        soup_file = bsd.generateBeautifulSoupFile(file['file'])
        bsd.generate_new_htmlFile(soup_file, file['file'])


def add_paragraph_script(html_files, directory):
    pass


def remove_paragraph_script(html_files):
    pass


def download_video(video_url, type_video, source, directory_adapted, request):
    """
    if source.find("youtube.") > -1:
        print("youtube.")
        path_system, path_preview = download_video_youtube(video_url, directory_adapted, request)
        return path_system, path_preview
    if source.find("vimeo") > -1:
        print("vimeo")
        path_system, path_preview = download_video_youtube(video_url, directory_adapted, request)
        return path_system, path_preview
    """

    path_system, path_preview, path_src, tittle = download_video_youtubedl(video_url, directory_adapted, request)
    return path_system, path_preview, path_src, tittle

    # print("source "+str(source.find("Waldo")))


def download_video_youtubedl(video_url, directory_adapted, request):
    path_system = os.path.join(BASE_DIR, directory_adapted, 'oer_resources')
    ydl_opts = {
        'outtmpl': path_system + '/%(title)s.%(ext)s'.strip(),
        'noplaylist': True,
        'extract-audio': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', None)
            path_system = os.path.join(BASE_DIR, directory_adapted, 'oer_resources', video_title + ".mp4")
            path_preview = os.path.join(request._current_scheme_host, directory_adapted, 'oer_resources',
                                        video_title + ".mp4").replace(
                "\\", "/")
            path_src = 'oer_resources/' + video_title + ".mp4"
            return path_system, path_preview, path_src, video_title
    except Exception as e:
        return None, None, None, None


def generate_transcript_youtube(video_url, video_title, path_adapted, request):
    with YoutubeDL({}) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        id_video = info_dict.get('id', None)
        transcript_list = YouTubeTranscriptApi.list_transcripts(id_video)

        transcripts = []
        captions = []

        try:
            transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
            transcripts, captions = save_transcript(transcript, path_adapted, video_title, transcripts, captions, "manual", request)
            if transcript.language_code != 'es':
                transcript_es = get_transcript_youtube(transcript_list, 'es')
            elif transcript.language_code != 'en':
                transcript_en = get_transcript_youtube(transcript_list, 'en')
        except:
            transcript_es = get_transcript_youtube(transcript_list, 'es')
            transcript_en = get_transcript_youtube(transcript_list, 'en')

        print(transcript_es)
        print(transcript_en)
        transcripts, captions = save_transcript(transcript_es, path_adapted, video_title, transcripts, captions, "automatic/youtube", request)
        transcripts, captions = save_transcript(transcript_en, path_adapted, video_title, transcripts, captions, "automatic/youtube", request)

        return transcripts, captions


def get_transcript_youtube(transcript_list, lang):
    transcript = transcript_list.find_transcript(['es', 'en'])
    return transcript.translate(lang)


def save_transcript(transcript, path_adapted,  video_title, transcripts, captions, source, request):
    json_formatted = JSONFormatter().format_transcript(transcript.fetch())
    vtt_formatterd = WebVTTFormatter().format_transcript(transcript.fetch())
    json_system = os.path.join(BASE_DIR, path_adapted, "oer_resources", video_title + "_"+transcript.language_code + ".json")
    vtt_system = os.path.join(BASE_DIR, path_adapted, "oer_resources", video_title + "_"+transcript.language_code + ".vtt")
    json_preview = os.path.join(request._current_scheme_host, path_adapted, 'oer_resources',
                                        video_title + "_"+transcript.language_code + ".json").replace(
                "\\", "/")
    json_path = 'oer_resources/' + video_title + "_"+transcript.language_code + ".json"
    vtt_path = 'oer_resources/' + video_title + "_"+transcript.language_code + ".vtt"

    with open(json_system, 'w', encoding='utf-8') as json_file:
        json_file.write(json_formatted)
    with open(vtt_system, 'w', encoding='utf-8') as json_file:
        json_file.write(vtt_formatterd)

    transcripts_obj = {
        "src": json_path,
        "type": "JSONcc",
        "srclang": transcript.language_code,
        "label": transcript.language,
        "source": source,
        "path_system": json_system,
        "path_preview": json_preview
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


def download_subtitles():
    pass
