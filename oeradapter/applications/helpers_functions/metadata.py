import json
import os
from xml.dom import minidom
from unipath import Path
from .beautiful_soup_data import generateBeautifulSoupFile

BASE_DIR = Path(__file__).ancestor(3)

metadata = None

try:
    with open(os.path.join(Path(__file__).ancestor(4), "metadata.json")) as f:
        metadata = json.loads(f.read())
        f.close()
except Exception as e:
    print("Error", e)


def get_metadata(areas):
    """ Obtener metadatos segun las areas

    :param str[] areas: Array de areas
    :return:
        - object[] metadata_filter - Array de metadatos filtrados
    """
    metadata_filter = list()
    for area in areas:
        metadata_filter.append({
            "area": area,
            "metadata": metadata[area]
        })
    return metadata_filter


def exist_property(values, type_metadata):
    for value in values:
        try:
            if type_metadata == value.firstChild.nodeValue.strip():
                return True
        except:
            return False
    return False


def append_metadata(xml_path, metadata_tag):
    if xml_path is None:
        return

    xml = minidom.parse(xml_path)
    lom = xml.getElementsByTagName("lomes:lom")
    if len(lom) == 0:
        lom = xml.getElementsByTagName("lom")[0]

    accesibility = lom.getElementsByTagName("accesibility")[0]
    for metadata in metadata_tag:
        properties = lom.getElementsByTagName(metadata.get("property").lower())
        if len(properties) > 0:
            values = properties[0].getElementsByTagName("value")
            if not exist_property(values, metadata.get("type")):
                value = xml.createElement('value')
                value.setAttribute("uniqueElementName", "value")
                value.appendChild(xml.createTextNode(metadata.get("type")))
                properties[0].appendChild(value)
        else:
            property = xml.createElement(metadata.get("property").lower())
            accesibility.appendChild(property)

            value = xml.createElement('value')
            value.setAttribute("uniqueElementName", "value")
            value.appendChild(xml.createTextNode(metadata.get("type")))
            property.appendChild(value)
    save_xml(xml_path, xml)


def save_metadata_img(xml_path):
    print("metadata image", metadata.get("image"))
    append_metadata(xml_path, metadata.get("image"))


def save_metadata_video(xml_path):
    print("metadata video", metadata.get("video"))
    append_metadata(xml_path, metadata.get("video"))


def save_metadata_audio(xml_path):
    print("metadata audio", metadata.get("audio"))
    append_metadata(xml_path, metadata.get("audio"))


def save_metadata_button(xml_path):
    print("metadata button", metadata.get("button"))
    append_metadata(xml_path, metadata.get("button"))


def save_metadata_paragraph(xml_path):
    print("metadata paragraph", metadata.get("paragraph"))
    append_metadata(xml_path, metadata.get("paragraph"))


def tag_accesibility(xml_path):
    xml = minidom.parse(xml_path)
    lom = xml.getElementsByTagName("lomes:lom")
    if len(lom) == 0:
        lom = xml.getElementsByTagName("lom")[0]
    accesibility = lom.getElementsByTagName("accesibility")
    if len(accesibility) == 0:
        accesibility = xml.createElement('accesibility')
        lom.appendChild(accesibility)
        save_xml(xml_path, xml)


def save_xml(path, xml):
    with open(path, 'w', encoding="utf-8") as f:
        f.write(xml.toxml())
        f.close()


def find_xml_in_directory(directory):
    file_xml = None
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, directory)):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                bs_data = generateBeautifulSoupFile(file_path)
                data = bs_data.find("lom")
                if data is not None:
                    file_xml = file_path
                elif bs_data.find("lomes:lom"):
                    file_xml = file_path
    return file_xml
