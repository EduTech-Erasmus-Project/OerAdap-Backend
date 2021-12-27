import threading

from django.db.models import Q
from pytz import unicode

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

    threads = []

    for tag in tag_page_learning_object:
        page_learning_object = tag.page_learning_object
        # text_to_audio(tag, page_learning_object, learning_object, request)
        #threading.Thread(target=text_to_audio, args=(tag, page_learning_object, learning_object, request)).start()
        #threading.Thread(target=text_easy_reading, args=(tag, page_learning_object)).start()
        threads.append(threading.Thread(target=text_to_audio, args=(tag, page_learning_object, learning_object, request)))
        threads.append(threading.Thread(target=text_easy_reading, args=(tag, page_learning_object)))


        # print(page_learning_object)

    print("paragraph method")
    print(threads)
    for th in threads:
        th.start()
        th.join()

    return "success"


def audio_adaptation(learning_object, request):
    print("audio method")


def image_adaptation(learning_object, request):
    print("image method")


def video_adaptation(learning_object, request):
    print("video method")


def text_easy_reading(tag_page_learning_object, page_learning_object):
    print("adapted text")
    print(tag_page_learning_object.id)
    text_content = process.easy_reading(tag_page_learning_object.html_text)
    text_content_bsd = bsd.convertElementBeautifulSoup(text_content)

    print(str(text_content_bsd.get_text()))

    div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)
    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
    tag = file_html.find('p', tag_page_learning_object.id_class_ref)

    button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(tag_page_learning_object.id_class_ref,
                                                                         text_content)

    tag_adapted, created = TagAdapted.objects.get_or_create(tag_page_learning_object_id=tag_page_learning_object.id,
                                                            defaults={
                                                                "text": unicode(text_content_bsd.get_text()),
                                                                "html_text": unicode(str(text_content_bsd)),
                                                                "type": "p",
                                                                "id_ref": id_ref,
                                                                "tag_page_learning_object": tag_page_learning_object
                                                            })

    if created:
        tag.append(div_soup_data)
        div_soup_data = tag.find(id=id_ref)
        div_soup_data.insert(1, button_text_data)
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
    else:
        tag_adaptation = file_html.find(id=tag_adapted.id_ref)
        if tag_adaptation is None:
            tag.append(div_soup_data)
            div_soup_data = tag.find(id=id_ref)
            div_soup_data.insert(1, button_text_data)
            bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        else:
            tag_text = tag_adaptation.find('div', class_="tooltip text-container")
            if tag_text is not None:
                tag_text.decompose()
            tag_adaptation.insert(1, button_text_data)

        tag_adapted.text = unicode(text_content_bsd.get_text())
        tag_adapted.html_text = unicode(str(text_content_bsd))
        tag_adapted.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


def text_to_audio(tag_page_learning_object, page_learning_object, learning_object, request):
    print("adapted audio")
    print(tag_page_learning_object.id)
    path_src, path_system, path_preview = ba.convertText_Audio(tag_page_learning_object.text,
                                                               learning_object.path_adapted,
                                                               tag_page_learning_object.id_class_ref, request)

    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

    tag = file_html.find('p', tag_page_learning_object.id_class_ref)
    div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)

    button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
        tag_page_learning_object.id_class_ref, path_src)

    tag_adapted, created = TagAdapted.objects.get_or_create(tag_page_learning_object_id=tag_page_learning_object.id,
                                                            defaults={
                                                                "type": "p",
                                                                "path_src": path_src,
                                                                "path_preview": path_preview,
                                                                "path_system": path_system,
                                                                "id_ref": id_ref,
                                                                "tag_page_learning_object": tag_page_learning_object
                                                            })

    if created:
        tag.append(div_soup_data)
        div_soup_data = tag.find(id=id_ref)
        div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
    else:
        tag_adaptation = file_html.find(id=tag_adapted.id_ref)
        if tag_adaptation is None:
            tag.append(div_soup_data)
            div_soup_data = tag.find(id=id_ref)
            div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)
            bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        else:
            tag_audio = tag_adaptation.find('div', class_="tooltip audio-container")
            if tag_audio is not None:
                tag_audio.decompose()
            tag_adaptation.insert(len(tag_adaptation) - 1, button_audio_data)

        tag_adapted.path_src = path_src,
        tag_adapted.path_preview = path_preview,
        tag_adapted.path_system = path_system,
        tag_adapted.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


def paragraph_convert():
    pass


def adaptationAPI(areas=None, request=None):
    pass
