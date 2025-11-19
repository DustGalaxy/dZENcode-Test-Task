from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ReplyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.coment_id = self.scope["url_route"]["kwargs"]["comment_name"]
        self.comment_name = f"comment_{self.coment_id}"

        # Присоединяемся к группе
        await self.channel_layer.group_add(self.comment_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(self.comment_name, self.channel_name)

    # Получаем сообщение от WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.comment_name, {"type": "comment_message", "message": message}
        )

    # Получаем сообщение от группы
    async def chat_message(self, event):
        message = event["message"]

        # Отправляем сообщение обратно клиенту
        await self.send(text_data=json.dumps({"message": message}))
