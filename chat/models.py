from django.db import models
from django.contrib.auth import get_user_model
from videos.models import Video, Event
import uuid

User = get_user_model()

class Conversation(models.Model):
    """Model for managing chat conversations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    
    # Conversation metadata
    title = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Context information
    context_summary = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-last_activity']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        title = self.title or f"Conversation {self.id}"
        return f"{title} - {self.user.get_full_name()}"
    
    def generate_title(self):
        """Generate a title based on the first few messages"""
        first_message = self.messages.filter(sender='user').first()
        if first_message:
            # Take first 50 characters of the first user message
            self.title = first_message.content[:50] + "..." if len(first_message.content) > 50 else first_message.content
            self.save(update_fields=['title'])

class Message(models.Model):
    """Model for storing individual chat messages"""
    
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('video_reference', 'Video Reference'),
        ('event_reference', 'Event Reference'),
        ('analysis_result', 'Analysis Result'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    # Message content
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    
    # Rich content
    attachments = models.JSONField(default=list)  # File attachments, images, etc.
    metadata = models.JSONField(default=dict)  # Additional message metadata
    
    # References
    referenced_video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True)
    referenced_events = models.ManyToManyField(Event, blank=True)
    referenced_timestamp = models.FloatField(null=True, blank=True)  # Video timestamp reference
    
    # Message status
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # AI processing
    processing_time = models.FloatField(null=True, blank=True)  # Time taken to generate response
    model_used = models.CharField(max_length=100, blank=True)  # AI model used for generation
    confidence = models.FloatField(null=True, blank=True)  # Confidence in AI response
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.sender}: {content_preview}"

class ConversationContext(models.Model):
    """Model for storing conversation context and memory"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='context')
    
    # Context data
    current_video_focus = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True)
    current_timestamp_focus = models.FloatField(null=True, blank=True)
    
    # Conversation memory
    key_topics = models.JSONField(default=list)  # Important topics discussed
    mentioned_events = models.ManyToManyField(Event, blank=True)
    user_preferences = models.JSONField(default=dict)  # User preferences discovered in conversation
    
    # Analysis context
    active_analysis_types = models.JSONField(default=list)
    custom_rules_discussed = models.JSONField(default=dict)
    
    # Session state
    last_query_type = models.CharField(max_length=100, blank=True)
    pending_actions = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversation_contexts'
        verbose_name = 'Conversation Context'
        verbose_name_plural = 'Conversation Contexts'
    
    def __str__(self):
        return f"Context for {self.conversation}"
    
    def add_topic(self, topic):
        """Add a key topic to the conversation"""
        if topic not in self.key_topics:
            self.key_topics.append(topic)
            self.save(update_fields=['key_topics'])
    
    def set_video_focus(self, video, timestamp=None):
        """Set the current video and timestamp focus"""
        self.current_video_focus = video
        self.current_timestamp_focus = timestamp
        self.save(update_fields=['current_video_focus', 'current_timestamp_focus'])

class QuickReply(models.Model):
    """Model for storing quick reply suggestions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Reply information
    text = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    
    # Context matching
    context_keywords = models.JSONField(default=list)
    applicable_message_types = models.JSONField(default=list)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quick_replies'
        ordering = ['-usage_count', 'text']
        verbose_name = 'Quick Reply'
        verbose_name_plural = 'Quick Replies'
    
    def __str__(self):
        return self.text
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

