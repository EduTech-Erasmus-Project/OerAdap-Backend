import json
import os
from unipath import Path

metadata = None

try:
    with open(os.path.join(Path(__file__).ancestor(4), "metadata.json")) as f:
        metadata = json.loads(f.read())
        f.close()
except:
    print("file metadata.json not found")


def get_metadata(areas):
    metadata_filter = list()
    for area in areas:
        metadata_filter.append({
            "area": area,
            "metadata": metadata[area]
        })
    return metadata_filter


def save_metadata_in_xml(path_directory, areas):
    pass
