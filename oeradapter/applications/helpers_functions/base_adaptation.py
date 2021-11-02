from django.core.files.storage import FileSystemStorage
import os


def save_uploaded_file(path, file, resources_directory, request):
    """Save file on folder the learning object"""

    fs = FileSystemStorage(location=path)  # defaults to   MEDIA_ROOT
    filename = fs.save(file.name, file)
    save_path = os.path.join(request._current_scheme_host, resources_directory, 'oer_resouces', filename).replace(
        "\\", "/")
    path_system = os.path.join(path, filename)
    return save_path, path_system


def remove_uploaded_file(path_system):
    """Remove and save file on folder the learning object"""
    os.remove(path_system)
    #return save_uploaded_file(path, file, resources_directory, request)


def add_button_adaptation(html_files):
    pass


def remove_button_adaptation(html_files):
    pass


def add_paragraph_script(html_files):
    pass


def remove_paragraph_script(html_files):
    pass


def download_video_youtube():
    pass


def download_subtitles():
    pass
