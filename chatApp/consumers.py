import json
from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Conversation, Message, User
from asgiref.sync import sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Connect to conversation-specific channel
        self.conversation_id = self.scope["url_route"]["kwargs"]["convo_id"]
        self.room_group_name = f"chat_{str(self.conversation_id)}"
        
        # Also connect to user-specific channel for notifications
        self.user_id = self.scope["user"].id
        self.user_group_name = f"user_{self.user_id}"
        
        # Join conversation group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        # Join user's personal notification group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        
        print(f"Connected to groups: {self.room_group_name} and {self.user_group_name}")
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave both groups
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_content = data["content"]
            sender_id = data["sender_id"]
            print(f"Received message: {message_content} from {sender_id}")
            
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
                    'name': sender.get_full_name() or sender.username,
                },
                'conversation_id': str(self.conversation_id),
                'is_read': False,
            }
            
            # Update unread counts for other participants
            await self.update_unread_counts(conversation, sender)
            
            # Send to the conversation group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "new_message",
                    "message": formatted_message,
                    "conversation_id": str(self.conversation_id)
                },
            )
        except Exception as e:
            print(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))
    
    @database_sync_to_async
    def create_message(self, conversation, sender, content):
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content,
            is_read=False
        )
        
        # Update conversation timestamp
        conversation.updated_at = message.timestamp
        conversation.save()
        
        return message
    
    @database_sync_to_async
    def update_unread_counts(self, conversation, sender):
        from django.db.models import F
        from app.models import UnreadMessage
        
        # Update unread counts for other participants
        for participant in conversation.participants.exclude(pk=sender.id):
            unread, created = UnreadMessage.objects.get_or_create(
                user=participant,
                conversation=conversation
            )
            unread.unread_count = F('unread_count') + 1
            unread.save()
    
    async def new_message(self, event):
        # Handle messages coming from the conversation group
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'conversation_id': event['conversation_id']
        }, cls=DjangoJSONEncoder))
    
    async def chat_message(self, event):
        # Handle messages coming from the user's notification channel
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }, cls=DjangoJSONEncoder))