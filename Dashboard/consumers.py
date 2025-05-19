from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Add this connection to the 'notifications' group
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove this connection from the 'notifications' group
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def notify(self, event):
        # Send the notification message to the WebSocket client
        await self.send(text_data=json.dumps(event["message"]))
