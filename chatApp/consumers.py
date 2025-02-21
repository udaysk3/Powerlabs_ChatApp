import json
from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Conversation, Message, User
from asgiref.sync import sync_to_async
from django.core.serializers.json import DjangoJSONEncoder

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["convo_id"]
        self.room_group_name = f"chat_{str(self.conversation_id)}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data["content"]
        sender_id = data["sender_id"]
        
        # Get sender and conversation objects
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        conversation = await sync_to_async(Conversation.objects.get)(id=self.conversation_id)
        
        # Create message in database
        new_message = await self.create_message(conversation, sender, message_content)
        
        # Format message in the structure expected by frontend
        formatted_message = {
            'id': new_message.id,
            'content': new_message.content,
            'timestamp': new_message.timestamp.isoformat(),
            'sender': {
                'id': sender.id,
                'name': sender.username
            },
            'conversation_id': str(self.conversation_id)
        }
        
        # Send to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "new_message",
                "message": formatted_message,
                "conversation_id": str(self.conversation_id)
            },
        )
    
    
    @sync_to_async
    def create_message(self, conversation, sender, content):
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )
    
    async def new_message(self, event):
        # Send the properly formatted message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'conversation_id': event['conversation_id']
        }, cls=DjangoJSONEncoder))