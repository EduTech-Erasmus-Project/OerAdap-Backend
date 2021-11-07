from unipath import Path
from django.core.files.storage import FileSystemStorage
from . import beautiful_soup_data as bsd
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


def remove_uploaded_file(path_system, resources_directory):
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


def add_files_adaptation(html_files, directory, button=False, paragraph_script=False):
    """Add essential files of adaptation on learning object"""

    if button:
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
        print("path_save move folder", str(path_save))

    for file in html_files:
        #directory_file = os.path.join(BASE_DIR, directory, file['file'])
        soup_file = bsd.generateBeautifulSoupFile(file['file'])

        if button:
            headInfusion, bodyInfusion = bsd.templateInfusion()
            soup_file.head.insert(len(soup_file.head) - 1, headInfusion)
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


def download_video_youtube():
    pass


def download_subtitles():
    pass
