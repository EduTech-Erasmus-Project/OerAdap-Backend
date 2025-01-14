import threading
from django.db.models import Q
from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
from ..helpers_functions import process as process
from ..learning_object.models import TagPageLearningObject, PageLearningObject, TagAdapted, DataAttribute, Transcript


def convertAudioToText(tag_learning_object, page, learning_object, request):
    data_attribute = DataAttribute.objects.get(tag_page_learning_object_id=tag_learning_object.id)

    """Web Scraping"""
    div_soup_data, id_ref = bsd.templateAdaptationTag(tag_learning_object.id_class_ref)
    file_html = bsd.generateBeautifulSoupFile(page.path)
    tag = file_html.find('audio', tag_learning_object.id_class_ref)
    # tag['pTooltip']= 'Ver descripción visual de audio'

    tag_aux = str(tag)
    tag.insert(1, div_soup_data)
    new_text = ba.convertAudio_Text(data_attribute.path_system)
    TagAdapted.objects.create(
        tag_page_learning_object_id=tag.id,
        path_system=data_attribute.path_system,
        id_ref=tag.id_class_ref,
        type='audio',
        html_text=tag.html_text,
        path_src=data_attribute.data_attribute,
        text=new_text
    )
    button_text_data = bsd.templateAudioTextButton(
        tag.id_class_ref,
        new_text, page.dir_len)
    div_soup_data = tag.find(id=id_ref)
    div_soup_data.insert(1, button_text_data)
    tag_audio_div = bsd.templateAdaptedAudio(tag_aux, tag.id_class_ref)
    tag_audio_div.append(div_soup_data)
    tag_container = bsd.templateContainerButtons(tag_learning_object.id_class_ref, tag_audio_div)
    tag.replace_with(tag_container)
    bsd.generate_new_htmlFile(file_html, page.path)


def paragraph_adaptation(learning_object, request):
    tag_page_learning_object = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object_id=learning_object.id) & (Q(tag='p') | Q(tag='span') | Q(tag='li')))

    threads = []

    for tag in tag_page_learning_object:
        page_learning_object = tag.page_learning_object

        # threads.append(threading.Thread(target=text_to_audio, args=(tag, page_learning_object, learning_object, request)))
        # threads.append(threading.Thread(target=text_easy_reading, args=(tag, page_learning_object)))

        th1 = threading.Thread(target=text_to_audio, args=(tag, page_learning_object, learning_object, request))
        th1.start()
        th2 = threading.Thread(target=text_easy_reading, args=(tag, page_learning_object))
        th2.start()
        th1.join()
        th2.join()

    for th in threads:
        th.start()
        th.join()

    return "success"


def audio_adaptation(learning_object, request):
    tag_page_learning_object = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object_id=learning_object.id) & Q(tag='audio'))
    for tag in tag_page_learning_object:
        page_learning_object = tag.page_learning_object
        th = threading.Thread(target=convertAudioToText, args=(tag, page_learning_object, learning_object, request))
        th.start()
        th.join()
    # print("audio method")

    return "success"


def alt_Image_adapted(tag, page, learning_object, request):
    tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object=tag.id);

    file_html = bsd.generateBeautifulSoupFile(page.path)
    tag_class_ref = tag_adapted_learning_object.id_ref

    html_img_code = file_html.find_all(class_=tag_class_ref)
    alt_description = html_img_code[0].get('alt', [])
    if (alt_description):
        if (html_img_code[0].get('alt', []).isspace() == False):
            pass
        else:
            # print("No tiene texto", "\n")
            img_description = process.image_description('img_resourse')
            text_update = img_description
            alt_db_aux = bsd.convertElementBeautifulSoup(str(tag.html_text))
            alt_db_aux = alt_db_aux.img
            alt_db_aux['alt'] = text_update
            tag.html_text = str(alt_db_aux)
            tag.save()
            html_img_code[0]['alt'] = text_update;

            bsd.generate_new_htmlFile(file_html, page.path)
    else:
        # print("No tiene alt", "\n")
        img_description = process.image_description('img_resourse')
        text_update = img_description
        alt_db_aux = bsd.convertElementBeautifulSoup(str(tag.html_text))
        alt_db_aux = alt_db_aux.img
        alt_db_aux['alt'] = text_update
        tag.html_text = str(alt_db_aux)
        tag.save()
        html_img_code[0]['alt'] = text_update;

        bsd.generate_new_htmlFile(file_html, page.path)

    pass


def image_adaptation(learning_object, request):
    tag_page_learning_object = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object_id=learning_object.id) & Q(tag='img'))
    for tag in tag_page_learning_object:
        page_learning_object = tag.page_learning_object
        th = threading.Thread(target=alt_Image_adapted, args=(tag, page_learning_object, learning_object, request))
        th.start()
        th.join()

    # print("image method")
    return "success"


def save_transcript(transcript, tag_adapted):
    Transcript.objects.create(
        src=transcript['src'],
        type=transcript['type'],
        srclang=transcript['srclang'],
        label=transcript['label'],
        source=transcript['source'],
        path_system=transcript['path_system'],
        tag_adapted=tag_adapted,
    )


def save_tag_adapted(uid, tittle, path_src, path_preview, path_system, tag):
    tag_adapted = TagAdapted.objects.create(
        type="video",
        id_ref=uid,
        text=tittle,
        path_src=path_src,
        path_preview=path_preview,
        path_system=path_system,
        tag_page_learning_object=tag,
    )
    return tag_adapted


def convert_video(tag, learning_object, request):
    page_learning_object = tag.page_learning_object
    data_attribute = DataAttribute.objects.get(tag_page_learning_object_id=tag.id)
    uid = bsd.getUUID()
    transcripts = []
    captions = []
    tittle = data_attribute.data_attribute.split(".")[-2]
    path_src = data_attribute.data_attribute
    path_preview = data_attribute.path_system
    path_system = data_attribute.path_preview
    tag_adapted = None

    if data_attribute.source == 'local':
        # Traducir automaticamnete
        tag_adapted = save_tag_adapted(uid, tittle, path_src, path_preview, path_system, tag)
        transcripts, captions = process.video_transcript(path_system)
        for transcript in transcripts:
            save_transcript(transcript, tag_adapted)
        for caption in captions:
            save_transcript(caption, tag_adapted)
        # return

    else:
        # descargar el video
        path_system, path_preview, path_src, tittle = ba.download_video(data_attribute.data_attribute,
                                                                        data_attribute.type,
                                                                        data_attribute.source,
                                                                        learning_object.path_adapted, request)

        if path_system is None and path_preview is None:
            return

        path_src = bsd.get_directory_resource(page_learning_object.dir_len) + path_src

        # guardar el video como adaptado
        tag_adapted = save_tag_adapted(uid, tittle, path_src, path_preview, path_system, tag)

        if data_attribute.source.find("youtube") > -1:
            # descargar subtitulos de youtube
            transcripts, captions = ba.generate_transcript_youtube(data_attribute.data_attribute, tittle,
                                                                   learning_object.path_adapted, request,
                                                                   page_learning_object.dir_len)

            for transcript in transcripts:
                save_transcript(transcript, tag_adapted)

            for caption in captions:
                save_transcript(caption, tag_adapted)

        else:
            # traducir automaticamente
            transcripts, captions = process.video_transcript(path_system)
            for transcript in transcripts:
                save_transcript(transcript, tag_adapted)
            for caption in captions:
                save_transcript(caption, tag_adapted)
            # return
            pass

        data_attribute.source = "local"
        data_attribute.data_attribute = path_src
        data_attribute.path_system = path_system
        data_attribute.path_preview = path_preview
        data_attribute.save()

    # gurdar el html
    video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                 transcripts, uid)

    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
    tag_adaptation = file_html.find(tag.tag, tag.id_class_ref)
    tag_adaptation.replace_with(video_template)
    bsd.generate_new_htmlFile(file_html, page_learning_object.path)
    return 'success'


def video_adaptation(learning_object, request):
    tag_page_learning_object = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object_id=learning_object.id) & (Q(tag='iframe') | Q(tag='video')))

    threads = list()
    for tag in tag_page_learning_object:
        # th = threads.append(threading.Thread(target=convert_video, args=(tag, learning_object, request)))

        th = threading.Thread(target=convert_video, args=(tag, learning_object, request))
        # threads.append(th)
        th.start()
        th.join()

    for th in threads:
        th.join()

    return "success"


def text_easy_reading(tag_page_learning_object, page_learning_object):
    text_content = process.easy_reading(tag_page_learning_object.html_text)
    text_content_bsd = bsd.convertElementBeautifulSoup(text_content)

    div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)

    button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(tag_page_learning_object.id_class_ref,
                                                                         text_content, page_learning_object.dir_len)

    tag_adapted, created = TagAdapted.objects.get_or_create(tag_page_learning_object_id=tag_page_learning_object.id,
                                                            defaults={
                                                                "text": text_content_bsd.get_text(),
                                                                "html_text": str(text_content_bsd),
                                                                "type": "p",
                                                                "id_ref": id_ref,
                                                                "tag_page_learning_object": tag_page_learning_object
                                                            })
    tag_adapted.text = text_content_bsd.get_text()
    tag_adapted.html_text = str(text_content_bsd)
    tag_adapted.save()

    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
    tag = file_html.find(tag_page_learning_object.tag, tag_page_learning_object.id_class_ref)
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

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


def text_to_audio(tag_page_learning_object, page_learning_object, learning_object, request):
    path_src, path_system, path_preview = ba.convertText_Audio(tag_page_learning_object.text,
                                                               learning_object.path_adapted,
                                                               tag_page_learning_object.id_class_ref, request)

    div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)

    button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
        tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)

    tag_adapted, created = TagAdapted.objects.get_or_create(tag_page_learning_object_id=tag_page_learning_object.id,
                                                            defaults={
                                                                "type": "p",
                                                                "path_src": path_src,
                                                                "path_preview": path_preview,
                                                                "path_system": path_system,
                                                                "id_ref": id_ref,
                                                                "tag_page_learning_object": tag_page_learning_object
                                                            })

    tag_adapted.path_src = path_src,
    tag_adapted.path_preview = path_preview,
    tag_adapted.path_system = path_system,
    tag_adapted.save()

    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
    tag = file_html.find('p', tag_page_learning_object.id_class_ref)
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

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


def paragraph_convert():
    pass


def adaptationAPI(areas=None, request=None):
    pass
