# views.py additions
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Max, Count, F, Value, CharField
from django.db.models.functions import Concat
from .models import Conversation, Message, UnreadMessage
from user.models import SupplierQuoteEntry  # Assuming you have a Quote model
import json 
from asgiref.sync import sync_to_async, async_to_sync
from channels.layers import get_channel_layer
from user.models import ExtendedUser

def get_user_role(user):
    """Determines the role of the user (client or supplier)"""
    # Based on the USER_* constants from user.models
    if user.role == 1:  # USER_CLIENT
        return 'client'
    elif user.role == 2:  # USER_COMPANY
        return 'supplier'
    elif user.role in (4, 8):  # USER_MANAGER or USER_GENERAL_MANAGER
        return 'manager'
    else:
        return 'unknown'

def get_supplier_profile(user):
    """Gets the supplier profile data for a user"""
    # Return company info if the user has a company association
    if hasattr(user, 'company') and user.company:
        return {
            'company_name': user.company.name,
            'rating': 4.5,  # Placeholder - implement actual rating calculation
            'review_count': 10,  # Placeholder - implement actual review count
        }
    return {
        'company_name': 'Independent Supplier',
        'rating': 0,
        'review_count': 0,
    }

def get_client_profile(user):
    """Gets the client profile data for a user"""
    return {
        'location': f"{user.city}, {user.region}" if user.city and user.region else "Unknown Location",
    }

def send_message_notification(message):
    """Send WebSocket notification for new messages"""
    channel_layer = get_channel_layer()
    
    # Prepare message data
    message_data = {
        'id': message.id,
        'conversation_id': message.conversation.id,
        'sender': {
            'id': message.sender.id,
            'name': message.sender.get_full_name() or message.sender.username,
        },
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'is_read': message.is_read,
    }
    
    # Send to conversation-specific group channel
    conversation_group = f"chat_{message.conversation.id}"
    print(f"Sending message to group: {conversation_group}")
    
    async_to_sync(channel_layer.group_send)(
        conversation_group,
        {
            'type': 'new_message',
            'message': message_data,
            'conversation_id': str(message.conversation.id)
        }
    )
    
    # Also send to each recipient's personal channel for notifications
    recipients = message.conversation.participants.exclude(pk=message.sender.id)
    for recipient in recipients:
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}",
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
        
def create_conversation_for_quote(quote, client, supplier):
    """Create a new conversation between a client and supplier for a quote"""
    conversation = Conversation.objects.create()
    conversation.participants.add(client, supplier)
    conversation.quote = quote
    conversation.save()
    
    # Create initial system message
    Message.objects.create(
        conversation=conversation,
        sender=supplier,  # System message appears as from the supplier
        content=f"New quote #{quote.id} has been created. The estimated price is {quote.offer_price} {client.currency}.",
        is_read=False
    )
    
    # Set unread count for client
    UnreadMessage.objects.create(
        user=client,
        conversation=conversation,
        unread_count=1
    )
    
    return conversation



@login_required
def api_create_conversation(request):
    """API endpoint to create a new conversation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        participant_id = data.get('participant_id')
        quote_id = data.get('quote_id', None)
        
        if not participant_id:
            return JsonResponse({'error': 'Missing participant ID'}, status=400)
        
        # Get the other participant
        try:
            participant = ExtendedUser.objects.get(id=participant_id)
        except ExtendedUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Check if a conversation already exists between these users
        existing_conversations = Conversation.objects.filter(participants=request.user).filter(participants=participant)
        
        if existing_conversations.exists():
            # Return the existing conversation
            conversation = existing_conversations.first()
        else:
            # Create a new conversation
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, participant)
            
            # Add quote if provided
            if quote_id:
                try:
                    quote = SupplierQuoteEntry.objects.get(id=quote_id)
                    conversation.quote = quote
                    conversation.save()
                except SupplierQuoteEntry.DoesNotExist:
                    pass  # Ignore if quote doesn't exist
        
        return JsonResponse({
            'id': conversation.id,
            'created': not existing_conversations.exists()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_get_unread_counts(request):
    """API endpoint to get unread message counts"""
    user = request.user
    
    # Get all unread counts for user conversations
    unread_counts = UnreadMessage.objects.filter(
        user=user
    ).select_related('conversation')
    
    result = {}
    for unread in unread_counts:
        result[unread.conversation.id] = unread.unread_count
    
    return JsonResponse(result)

@login_required
def api_mark_read(request, convo_id):
    """API endpoint to mark all messages in a conversation as read"""
    user = request.user
    
    try:
        conversation = Conversation.objects.get(id=convo_id, participants=user)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    
    # Mark all messages as read
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=user).update(is_read=True)
    
    # Reset unread counter
    UnreadMessage.objects.filter(user=user, conversation=conversation).update(unread_count=0)
    
    return JsonResponse({'success': True})

@login_required
def messaging_center(request):
    """Main messaging UI view"""
    user_data = {
        'id': request.user.id,
        'name': request.user.get_full_name() or request.user.username,
        'role': get_user_role(request.user),  # You need to implement this function
    }
    
    return render(request, 'chat.html', {
        'user_data_json': json.dumps(user_data),
    })

@login_required
def api_conversations(request):
    """API endpoint to get all conversations for the current user"""
    user = request.user
    print(user)
    user_role = get_user_role(user)
    
    # Get all conversations with unread counts and last message time
    conversations = Conversation.objects.filter(
        participants=user
    ).annotate(
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=user)),
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')
    print(Conversation.objects.filter(participants=user))
    results = []
    for convo in conversations:
        # Get the other participant(s)
        participants = []
        for participant in convo.participants.exclude(pk=user.id):
            participant_data = {
                'id': participant.id,
                'name': participant.get_full_name() or participant.username,
            }
            
            # Add role-specific fields
            if user_role == 'client':
                # If viewing as client, add supplier company info
                supplier_profile = get_supplier_profile(participant)  # Implement this
                print(supplier_profile)
                participant_data.update({
                    'company_name': supplier_profile.get('company_name', 'Independent Supplier'),
                    'contact_name': participant.get_full_name(),
                    'rating': supplier_profile.get("rating"),
                    'review_count': supplier_profile.get("review_count"),
                })
            else:
                # If viewing as supplier, add client location
                client_profile = get_client_profile(participant)  # Implement this
                participant_data.update({
                    'location': client_profile.get('location', 'Unknown Location'),
                })
                
            participants.append(participant_data)
            
        # Get quote ID if any
        quote_id = convo.quote_id if hasattr(convo, 'quote') else None
            
        results.append({
            'id': convo.id,
            'participants': participants,
            'unread_count': convo.unread_count,
            'last_message_time': convo.last_message_time.isoformat() if convo.last_message_time else None,
            'quote_id': quote_id,
        })
    
    return JsonResponse(results, safe=False)

@login_required
def api_conversation_detail(request, convo_id):
    """API endpoint to get details of a specific conversation"""
    user = request.user
    user_role = get_user_role(user)
    
    try:
        conversation = Conversation.objects.get(id=convo_id, participants=user)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    
    # Mark unread messages as read
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=user).update(is_read=True)
    
    # Reset unread counter
    UnreadMessage.objects.filter(user=user, conversation=conversation).update(unread_count=0)
    
    # Get conversation participants
    participants = []
    for participant in conversation.participants.exclude(pk=user.id):
        participant_data = {
            'id': participant.id,
            'name': participant.get_full_name() or participant.username,
        }
        
        # Add role-specific fields (similar to api_conversations)
        if user_role == 'client':
            supplier_profile = get_supplier_profile(participant)
            participant_data.update({
                'company_name': supplier_profile.get('company_name'),
                'contact_name': participant.get_full_name(),
                'rating': supplier_profile.get('rating'),
                'review_count': supplier_profile.get('review_count'),
            })
        else:
            client_profile = get_client_profile(participant)
            participant_data.update({
                'location': client_profile.get('location', 'Unknown Location'),
            })
            
        participants.append(participant_data)
    
    # Get messages
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
    message_data = []
    for msg in messages:
        message_data.append({
            'id': msg.id,
            'sender': {
                'id': msg.sender.id,
                'name': msg.sender.get_full_name() or msg.sender.username,
            },
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'is_read': msg.is_read,
        })
    
    # Get quote data if available
    quote_data = None
    if hasattr(conversation, 'quote'):
        quote = conversation.quote
        quote_data = {
            'id': quote.id,
            'price': quote.offer_price,
            'model': quote.inverter_model,
            # 'need_met': quote.need_met_percentage,
            # 'payback_period': quote.payback_period,
            # 'funding': quote.funding_source,
        }
    
    response_data = {
        'id': conversation.id,
        'participants': participants,
        'messages': message_data,
        'quote': quote_data,
    }
    
    return JsonResponse(response_data)

@login_required
def api_send_message(request):
    """API endpoint to send a new message"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        
        if not conversation_id or not content:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Verify user is part of the conversation
        try:
            conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversation not found'}, status=404)
        
        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            is_read=False
        )
        
        # Update conversation timestamp
        conversation.updated_at = message.timestamp
        conversation.save()
        
        # Update unread counts for other participants
        for participant in conversation.participants.exclude(pk=request.user.id):
            unread, created = UnreadMessage.objects.get_or_create(
                user=participant,
                conversation=conversation
            )
            unread.unread_count = F('unread_count') + 1
            unread.save()
        
        # Send WebSocket notification (you'll need to implement this)
        send_message_notification(message)
        
        return JsonResponse({
            'id': message.id,
            'timestamp': message.timestamp.isoformat(),
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)