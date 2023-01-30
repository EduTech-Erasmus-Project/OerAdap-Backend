import json
from channels.generic.websocket import AsyncWebsocketConsumer


class VideoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        idTag = self.scope["url_route"]["kwargs"]["pk"]
        await self.channel_layer.group_add("channel_"+str(idTag), self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        idTag = self.scope["url_route"]["kwargs"]["pk"]
        await self.channel_layer.group_discard("channel_"+str(idTag), self.channel_name)

    async def send_new_data(self, event):
        new_data = event["text"]
        await self.send(json.dumps(new_data))

    async def disconnect_download(self, event):
        await self.close()
