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


def find_xml_in_directory(directory):
    print(directory)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file);
                file_name = file_path.replace(directory, '')
                file_name = file_name[1:]
                print("file_path", file_path)
                print("file_name", file_name)




def get_metadata(areas):
    metadata_filter = list()
    for area in areas:
        metadata_filter.append({
            area: metadata[area]
        })
    #print(metadata_filter)



def save_metadata_in_xml(path_directory, areas):
    pass
