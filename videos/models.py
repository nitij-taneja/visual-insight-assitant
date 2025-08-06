from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid
import os

User = get_user_model()

def video_upload_path(instance, filename):
    """Generate upload path for video files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('videos', str(instance.user.id), filename)

class Video(models.Model):
    """Model for storing video information and metadata"""
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    
    # Video file information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=video_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])]
    )
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    
    # Video metadata
    duration = models.DurationField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # in bytes
    resolution_width = models.PositiveIntegerField(null=True, blank=True)
    resolution_height = models.PositiveIntegerField(null=True, blank=True)
    frame_rate = models.FloatField(null=True, blank=True)
    format = models.CharField(max_length=10, null=True, blank=True)
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)
    
    # Analysis configuration
    analysis_types = models.JSONField(default=list)  # Types of analysis to perform
    custom_rules = models.JSONField(default=dict)  # Custom rules for guideline adherence
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['-uploaded_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"
    
    def start_processing(self):
        """Mark video as processing"""
        self.status = 'processing'
        self.processing_started_at = timezone.now()
        self.save(update_fields=['status', 'processing_started_at'])
    
    def complete_processing(self):
        """Mark video processing as completed"""
        self.status = 'completed'
        self.processing_completed_at = timezone.now()
        self.save(update_fields=['status', 'processing_completed_at'])
    
    def fail_processing(self, error_message):
        """Mark video processing as failed"""
        self.status = 'failed'
        self.processing_error = error_message
        self.save(update_fields=['status', 'processing_error'])
    
    @property
    def processing_duration(self):
        """Calculate processing duration"""
        if self.processing_started_at and self.processing_completed_at:
            return self.processing_completed_at - self.processing_started_at
        return None

class VideoFrame(models.Model):
    """Model for storing extracted video frames"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='frames')
    
    # Frame information
    frame_number = models.PositiveIntegerField()
    timestamp = models.FloatField()  # Time in seconds from video start
    image = models.ImageField(upload_to='frames/')
    
    # Frame metadata
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    file_size = models.PositiveIntegerField()  # in bytes
    
    # Analysis flags
    has_objects = models.BooleanField(default=False)
    has_events = models.BooleanField(default=False)
    is_keyframe = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_frames'
        ordering = ['timestamp']
        unique_together = ['video', 'frame_number']
        verbose_name = 'Video Frame'
        verbose_name_plural = 'Video Frames'
    
    def __str__(self):
        return f"Frame {self.frame_number} from {self.video.title}"

class DetectedObject(models.Model):
    """Model for storing detected objects in video frames"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    frame = models.ForeignKey(VideoFrame, on_delete=models.CASCADE, related_name='objects')
    
    # Object information
    class_name = models.CharField(max_length=100)
    confidence = models.FloatField()
    
    # Bounding box coordinates (normalized 0-1)
    bbox_x = models.FloatField()
    bbox_y = models.FloatField()
    bbox_width = models.FloatField()
    bbox_height = models.FloatField()
    
    # Tracking information
    track_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Additional attributes
    attributes = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'detected_objects'
        ordering = ['-confidence']
        verbose_name = 'Detected Object'
        verbose_name_plural = 'Detected Objects'
    
    def __str__(self):
        return f"{self.class_name} ({self.confidence:.2f}) in frame {self.frame.frame_number}"

class Event(models.Model):
    """Model for storing detected events in videos"""
    
    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('violation', 'Violation'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='events')
    
    # Event information
    event_type = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    
    # Temporal information
    start_time = models.FloatField()  # Start time in seconds
    end_time = models.FloatField(null=True, blank=True)  # End time in seconds
    duration = models.FloatField(null=True, blank=True)  # Duration in seconds
    
    # Spatial information (if applicable)
    location_x = models.FloatField(null=True, blank=True)
    location_y = models.FloatField(null=True, blank=True)
    
    # Analysis information
    confidence = models.FloatField()
    detected_by = models.CharField(max_length=100)  # Model or rule that detected the event
    
    # Related objects
    related_objects = models.ManyToManyField(DetectedObject, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict)
    
    # Guideline adherence
    is_violation = models.BooleanField(default=False)
    guideline_reference = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'events'
        ordering = ['start_time']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return f"{self.title} at {self.start_time}s in {self.video.title}"
    
    @property
    def calculated_duration(self):
        """Calculate event duration if not provided"""
        if self.duration:
            return self.duration
        elif self.end_time:
            return self.end_time - self.start_time
        return 0

