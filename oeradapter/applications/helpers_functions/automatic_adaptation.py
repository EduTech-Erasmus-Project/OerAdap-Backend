from django.db.models import Q

from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
from ..helpers_functions import process as process
from ..learning_object.models import TagPageLearningObject, PageLearningObject, TagAdapted


def adaptation(areas=None, files=None, request=None):
    print(areas)
    print(request)


def paragraph_adaptation(learning_object, request):
    tag_page_learning_object = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object_id=learning_object.id) & Q(tag='p'))

    for tag in tag_page_learning_object:
        page_learning_object = tag.page_learning_object
        #text_to_audio(tag, page_learning_object, learning_object, request)
        print(page_learning_object)

    print("paragraph method")
    return "success"


def audio_adaptation(learning_object):
    print("audio method")


def image_adaptation(learning_object):
    print("image method")


def video_adaptation(learning_object):
    print("video method")


def text_to_audio(tag_page_learning_object, page_learning_object, learning_object, request):
    path_src, path_system, path_preview = ba.convertText_Audio(tag_page_learning_object.text, learning_object.path_adapted, request)

    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
    div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)
    tag = file_html.find('p', tag_page_learning_object.id_class_ref)
    tag.append(div_soup_data)

    button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
        tag_page_learning_object.id_class_ref, path_src)
    div_soup_data = tag.find(id=id_ref)
    div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)

    data = TagAdapted.objects.create(
        type="p",
        id_ref=id_ref,
        path_src=path_src,
        path_preview=path_preview,
        path_system=path_system,
        tag_page_learning_object=tag_page_learning_object
    )

    bsd.generate_new_htmlFile(file_html, page_learning_object.path)

def paragraph_convert():
    pass


def adaptationAPI(areas=None, request=None):
    pass



