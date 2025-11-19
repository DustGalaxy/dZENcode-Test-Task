import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ReplyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope.get("user"):
            await self.close(code=4001)  # Unauthorized
            return

        self.comment_id = self.scope["url_route"]["kwargs"]["comment_name"]
        self.comment_name = f"comment_{self.comment_id}"

        await self.channel_layer.group_add(self.comment_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.comment_name, self.channel_name)

    async def new_reply(self, event):
        """
        Отправляет новый ответ всем подключенным клиентам
        """
        reply_data = event["reply"]

        await self.send(text_data=json.dumps({"type": "new_reply", "data": reply_data}))
