import json
from channels.generic.websocket import AsyncWebsocketConsumer


class VideoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        idTag = self.scope["url_route"]["kwargs"]["pk"]
        print("idTag", idTag)
        print("request to connect socket tag", str(idTag))

        await self.channel_layer.group_add("channel_"+str(idTag), self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        idTag = self.scope["url_route"]["kwargs"]["pk"]
        print("request to disconnect socket tag", str(idTag))
        await self.channel_layer.group_discard("channel_"+str(idTag), self.channel_name)
        #await self.close()

    async def send_new_data(self, event):
        new_data = event["text"]
        await self.send(json.dumps(new_data))

    async def disconnect_download(self, event):
        #await self.disconnect()
        await self.close()

'''
class VideoConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("websocket_connect", self.scope)

        idTag = self.scope["url_route"]["kwargs"]["pk"]
        await self.send({
            "type": "websocket.accept"
        })
        await self.channel_layer.group_add("channel_" + str(idTag), self.channel_name)

    async def websocket_receive(self, event):
        print("websocket_receive", event)

    async def websocket_disconnect(self, event):
        print("websocket_disconnect", event)
        idTag = self.scope["url_route"]["kwargs"]["pk"]
        print("request to disconnect socket tag", str(idTag))
        await self.channel_layer.group_discard("channel_" + str(idTag), self.channel_name)

    async def send_new_data(self, event):
        new_data = event["text"]
        self.send({
            "type": "websocket.send",
            "text": json.dumps(new_data)
        })
'''