from rest_framework import serializers
from .models import Video, VideoFrame, DetectedObject, Event

class VideoUploadSerializer(serializers.ModelSerializer):
    """Serializer for video upload"""
    
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'file', 'analysis_types', 'custom_rules'
        ]
    
    def validate_file(self, value):
        # Validate file size (50MB limit)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 50MB")
        
        # Validate file extension
        allowed_extensions = ['mp4', 'avi', 'mov', 'mkv']
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File extension '{file_extension}' not allowed. "
                f"Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        return value

class VideoListSerializer(serializers.ModelSerializer):
    """Serializer for video list view"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    processing_duration_display = serializers.SerializerMethodField()
    events_count = serializers.SerializerMethodField()
    violations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'thumbnail', 'duration',
            'file_size', 'resolution_width', 'resolution_height',
            'status', 'user_name', 'processing_duration_display',
            'events_count', 'violations_count', 'uploaded_at'
        ]
    
    def get_processing_duration_display(self, obj):
        duration = obj.processing_duration
        if duration:
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            return f"{minutes}m {seconds}s"
        return None
    
    def get_events_count(self, obj):
        return obj.events.count()
    
    def get_violations_count(self, obj):
        return obj.events.filter(is_violation=True).count()

class VideoDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed video view"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    events = serializers.SerializerMethodField()
    frames_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'file', 'thumbnail',
            'duration', 'file_size', 'resolution_width', 'resolution_height',
            'frame_rate', 'format', 'status', 'processing_started_at',
            'processing_completed_at', 'processing_error', 'analysis_types',
            'custom_rules', 'user_name', 'events', 'frames_count',
            'uploaded_at', 'updated_at'
        ]
    
    def get_events(self, obj):
        events = obj.events.all()[:10]  # Limit to first 10 events
        return EventSerializer(events, many=True).data
    
    def get_frames_count(self, obj):
        return obj.frames.count()

class DetectedObjectSerializer(serializers.ModelSerializer):
    """Serializer for detected objects"""
    
    class Meta:
        model = DetectedObject
        fields = [
            'id', 'class_name', 'confidence', 'bbox_x', 'bbox_y',
            'bbox_width', 'bbox_height', 'track_id', 'attributes'
        ]

class VideoFrameSerializer(serializers.ModelSerializer):
    """Serializer for video frames"""
    
    objects = DetectedObjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = VideoFrame
        fields = [
            'id', 'frame_number', 'timestamp', 'image', 'width', 'height',
            'has_objects', 'has_events', 'is_keyframe', 'objects'
        ]

class EventSerializer(serializers.ModelSerializer):
    """Serializer for events"""
    
    related_objects = DetectedObjectSerializer(many=True, read_only=True)
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'event_type', 'title', 'description', 'severity',
            'start_time', 'end_time', 'duration', 'duration_display',
            'location_x', 'location_y', 'confidence', 'detected_by',
            'is_violation', 'guideline_reference', 'metadata',
            'related_objects', 'created_at'
        ]
    
    def get_duration_display(self, obj):
        duration = obj.calculated_duration
        if duration > 0:
            return f"{duration:.2f}s"
        return "Instant"

class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events"""
    
    class Meta:
        model = Event
        fields = [
            'video', 'event_type', 'title', 'description', 'severity',
            'start_time', 'end_time', 'location_x', 'location_y',
            'confidence', 'detected_by', 'is_violation',
            'guideline_reference', 'metadata'
        ]
    
    def validate(self, attrs):
        if attrs.get('end_time') and attrs.get('start_time'):
            if attrs['end_time'] <= attrs['start_time']:
                raise serializers.ValidationError("End time must be after start time")
        return attrs

class VideoAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for video analysis requests"""
    
    analysis_types = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=True
    )
    custom_rules = serializers.JSONField(required=False, default=dict)
    confidence_threshold = serializers.FloatField(
        required=False, 
        default=0.7,
        min_value=0.0,
        max_value=1.0
    )
    
    def validate_analysis_types(self, value):
        allowed_types = [
            'object_detection', 'activity_recognition', 'event_classification',
            'guideline_adherence', 'anomaly_detection'
        ]
        for analysis_type in value:
            if analysis_type not in allowed_types:
                raise serializers.ValidationError(
                    f"'{analysis_type}' is not a valid analysis type. "
                    f"Allowed types: {', '.join(allowed_types)}"
                )
        return value

class VideoSearchSerializer(serializers.Serializer):
    """Serializer for video search requests"""
    
    query = serializers.CharField(max_length=255, required=False)
    status = serializers.ChoiceField(
        choices=Video.STATUS_CHOICES,
        required=False
    )
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    has_violations = serializers.BooleanField(required=False)
    analysis_types = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )

