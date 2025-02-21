from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Main UI view
    path('', views.messaging_center, name='messaging_center'),
    
    # API endpoints for conversations
    path('api/conversations/', views.api_conversations, name='api_conversations'),
    path('api/conversations/<int:convo_id>/', views.api_conversation_detail, name='api_conversation_detail'),
    path('api/conversations/create/', views.api_create_conversation, name='api_create_conversation'),
    
    # API endpoints for messages
    path('api/send-message/', views.api_send_message, name='api_send_message'),
    path('api/mark-read/<int:convo_id>/', views.api_mark_read, name='api_mark_read'),
    path('api/unread-counts/', views.api_get_unread_counts, name='api_get_unread_counts'),
]