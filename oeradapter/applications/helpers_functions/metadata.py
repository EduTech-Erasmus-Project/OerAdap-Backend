import json
import os
from unipath import Path

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
    # print("areas", areas)
    # print("metadata", metadata)

    metadata_filter = list()
    for area in areas:
        # print("area", area)
        # print("area in array", metadata[area])
        metadata_filter.append({
            "area": area,
            "metadata": metadata[area]
        })
    return metadata_filter


def save_metadata_in_xml(path_directory, areas):
    pass
