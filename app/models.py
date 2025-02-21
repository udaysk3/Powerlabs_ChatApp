from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name="conversations")
    updated_at = models.DateTimeField(auto_now=True)  # For sorting by latest message
    quote = models.ForeignKey('user.SupplierQuoteEntry', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Conversation between {', '.join(p.first_name + p.last_name for p in self.participants.all())}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username}: {self.content[:20]}..."

class UnreadMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    unread_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'conversation')
