import os
import threading
import environ
from asgiref.sync import async_to_sync
from unipath import Path
import shortuuid
from youtube_dl import YoutubeDL
from channels.layers import get_channel_layer

BASE_DIR = Path(__file__).ancestor(3)
channel_layer = get_channel_layer()

env = environ.Env(
    PROD=(bool, False)
)
environ.Env.read_env(os.path.join(Path(__file__).ancestor(4), '.env'))


class YoutubeDLThread(threading.Thread):

    def __init__(self, video_url, directory_adapted, request, tag):
        threading.Thread.__init__(self)

        self.tag = tag
        self.request = request
        self.directory_adapted = directory_adapted
        self.video_id_title = str(shortuuid.ShortUUID().random(length=8))
        self.path_system = os.path.join(BASE_DIR, self.directory_adapted, 'oer_resources')

        self.ydl_opts = {
            'outtmpl': self.path_system + '/' + self.video_id_title + '.%(ext)s'.strip(),
            'format': '(mp4)[height<=480]',
            # 'bestvideo[height<=480]+bestaudio/best[height<=480]', #'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[
            # ext=mp4]/best', 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            'noplaylist': True,
            # 'extract-audio': True,
            # 'logger': MyLogger(),
            # 'progress_hooks': [process_bytes],
            # 'audio-format': 'mp3',
        }

        self.scram_dl = YoutubeDL(self.ydl_opts)
        self.scram_dl.add_progress_hook(self.hook_progress)
        self.scram_dl.add_default_info_extractors()
        self.is_finished = False
        self.urls = video_url
        # self.download()

    def hook_progress(self, status):
        if status['status'] == 'finished':
            #print("finished", status)
            self.is_finished = True
            async_to_sync(channel_layer.group_send)("channel_" + str(self.tag.id), {"type": "send_new_data", "text": {
                "status": "video_finished",
                "type": "video",
                "message": "Video descargado."
            }})

        else:
            self.is_finished = False
            # Report progress
            async_to_sync(channel_layer.group_send)("channel_" + str(self.tag.id), {"type": "send_new_data", "text": {
                "status": "downloading",
                "type": "video",
                "message": "Descargando video…",
                "data": {
                    "eta_str": status["_eta_str"].strip(),
                    "percent_str": status["_percent_str"].strip(),
                    "percent": round((float(status["downloaded_bytes"]) / float(status["total_bytes"])) * 100, 2)
                }
            }})

    def download(self):
        try:
            info_dict = self.scram_dl.extract_info(self.urls, download=True)
            filename = self.scram_dl.prepare_filename(info_dict)
            #print("filename", filename)
            title = self.video_id_title  # re.sub("[^A-Za-z0-9]", "_", info_dict.get('title', None))
            # print("title: ", title)
            path_system = filename
            path_split = path_system.split(os.sep)
            path_preview = os.path.join(self.request._current_scheme_host, self.directory_adapted, 'oer_resources',
                                        path_split[-1]).replace("\\", "/")
            if env('PROD'):
                path_preview = path_preview.replace("http://", "https://")
            path_src = 'oer_resources/' + path_split[-1]
            # print("path_preview: ", path_preview)
            return path_system, path_preview, path_src, title
        except Exception as e:
            raise e
