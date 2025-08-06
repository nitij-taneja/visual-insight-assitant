from django.db import models
from django.contrib.auth import get_user_model
from videos.models import Video, Event
from chat.models import Conversation
import uuid

User = get_user_model()

class AnalysisSession(models.Model):
    """Model for tracking analysis sessions"""
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_sessions')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='analysis_sessions')
    
    # Session information
    session_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # Analysis configuration
    analysis_types = models.JSONField(default=list)
    custom_rules = models.JSONField(default=dict)
    confidence_threshold = models.FloatField(default=0.7)
    
    # Progress tracking
    progress_percentage = models.FloatField(default=0.0)
    current_stage = models.CharField(max_length=100, blank=True)
    
    # Results summary
    total_events_detected = models.PositiveIntegerField(default=0)
    total_violations_detected = models.PositiveIntegerField(default=0)
    total_objects_detected = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    processing_time = models.DurationField(null=True, blank=True)
    frames_processed = models.PositiveIntegerField(default=0)
    
    # Error handling
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analysis_sessions'
        ordering = ['-started_at']
        verbose_name = 'Analysis Session'
        verbose_name_plural = 'Analysis Sessions'
    
    def __str__(self):
        name = self.session_name or f"Session {self.id}"
        return f"{name} - {self.video.title}"
    
    def update_progress(self, percentage, stage=None):
        """Update analysis progress"""
        self.progress_percentage = percentage
        if stage:
            self.current_stage = stage
        self.save(update_fields=['progress_percentage', 'current_stage', 'updated_at'])

class VideoSummary(models.Model):
    """Model for storing AI-generated video summaries"""
    
    SUMMARY_TYPE_CHOICES = [
        ('overview', 'Overview'),
        ('events', 'Events Summary'),
        ('violations', 'Violations Summary'),
        ('objects', 'Objects Summary'),
        ('timeline', 'Timeline Summary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='summaries')
    analysis_session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='summaries')
    
    # Summary information
    summary_type = models.CharField(max_length=20, choices=SUMMARY_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Metadata
    word_count = models.PositiveIntegerField()
    key_points = models.JSONField(default=list)
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Generation information
    model_used = models.CharField(max_length=100)
    generation_time = models.FloatField()  # Time taken to generate summary
    
    # User feedback
    user_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 rating
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_summaries'
        ordering = ['-created_at']
        unique_together = ['video', 'summary_type']
        verbose_name = 'Video Summary'
        verbose_name_plural = 'Video Summaries'
    
    def __str__(self):
        return f"{self.title} - {self.video.title}"

class Insight(models.Model):
    """Model for storing AI-generated insights and recommendations"""
    
    INSIGHT_TYPE_CHOICES = [
        ('pattern', 'Pattern Recognition'),
        ('anomaly', 'Anomaly Detection'),
        ('trend', 'Trend Analysis'),
        ('recommendation', 'Recommendation'),
        ('alert', 'Alert'),
        ('prediction', 'Prediction'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='insights')
    analysis_session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='insights')
    
    # Insight information
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Supporting data
    supporting_events = models.ManyToManyField(Event, blank=True)
    evidence_data = models.JSONField(default=dict)
    confidence_score = models.FloatField()
    
    # Actionability
    is_actionable = models.BooleanField(default=False)
    recommended_actions = models.JSONField(default=list)
    
    # Temporal information
    relevant_timeframe_start = models.FloatField(null=True, blank=True)
    relevant_timeframe_end = models.FloatField(null=True, blank=True)
    
    # User interaction
    is_acknowledged = models.BooleanField(default=False)
    user_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'insights'
        ordering = ['-priority', '-confidence_score', '-created_at']
        verbose_name = 'Insight'
        verbose_name_plural = 'Insights'
    
    def __str__(self):
        return f"{self.title} ({self.priority})"
    
    def acknowledge(self, user_notes=None):
        """Mark insight as acknowledged by user"""
        self.is_acknowledged = True
        if user_notes:
            self.user_notes = user_notes
        self.save(update_fields=['is_acknowledged', 'user_notes'])

class UserAnalytics(models.Model):
    """Model for tracking user analytics and usage patterns"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')
    
    # Usage statistics
    total_videos_uploaded = models.PositiveIntegerField(default=0)
    total_analysis_time = models.DurationField(default=models.DurationField().default)
    total_conversations = models.PositiveIntegerField(default=0)
    total_messages_sent = models.PositiveIntegerField(default=0)
    
    # Feature usage
    most_used_analysis_types = models.JSONField(default=list)
    favorite_video_categories = models.JSONField(default=list)
    
    # Performance metrics
    average_session_duration = models.DurationField(null=True, blank=True)
    most_active_time_of_day = models.TimeField(null=True, blank=True)
    
    # Engagement metrics
    insights_acknowledged = models.PositiveIntegerField(default=0)
    feedback_provided = models.PositiveIntegerField(default=0)
    
    # Timestamps
    first_activity = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_analytics'
        verbose_name = 'User Analytics'
        verbose_name_plural = 'User Analytics'
    
    def __str__(self):
        return f"Analytics for {self.user.get_full_name()}"

class SystemMetrics(models.Model):
    """Model for tracking system-wide metrics and performance"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # System performance
    average_processing_time = models.FloatField()
    total_videos_processed = models.PositiveIntegerField()
    total_events_detected = models.PositiveIntegerField()
    total_insights_generated = models.PositiveIntegerField()
    
    # Model performance
    model_accuracy_scores = models.JSONField(default=dict)
    model_usage_statistics = models.JSONField(default=dict)
    
    # Resource usage
    cpu_usage_average = models.FloatField(null=True, blank=True)
    memory_usage_average = models.FloatField(null=True, blank=True)
    storage_usage = models.BigIntegerField(null=True, blank=True)  # in bytes
    
    # Error tracking
    error_rate = models.FloatField(default=0.0)
    common_errors = models.JSONField(default=dict)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_metrics'
        ordering = ['-created_at']
        verbose_name = 'System Metrics'
        verbose_name_plural = 'System Metrics'
    
    def __str__(self):
        return f"System Metrics {self.period_start.date()} - {self.period_end.date()}"

