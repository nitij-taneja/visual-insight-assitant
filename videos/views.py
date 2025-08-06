from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Video, VideoFrame, Event, DetectedObject
from .serializers import (
    VideoUploadSerializer, VideoListSerializer, VideoDetailSerializer,
    VideoFrameSerializer, EventSerializer, EventCreateSerializer,
    VideoAnalysisRequestSerializer, VideoSearchSerializer
)
from .tasks import process_video_analysis  # We'll create this later

class VideoUploadView(generics.CreateAPIView):
    """API view for video upload"""
    
    serializer_class = VideoUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save video with current user
        video = serializer.save(user=request.user)
        
        # Start background processing
        process_video_analysis.delay(video.id)
        
        return Response({
            'video': VideoDetailSerializer(video).data,
            'message': 'Video uploaded successfully and processing started'
        }, status=status.HTTP_201_CREATED)

class VideoListView(generics.ListAPIView):
    """API view for listing user's videos"""
    
    serializer_class = VideoListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['uploaded_at', 'title', 'duration']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        return Video.objects.filter(user=self.request.user).select_related('user')

class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for video detail, update, and delete"""
    
    serializer_class = VideoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Video.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_video_analysis(request, video_id):
    """API view to start or restart video analysis"""
    
    video = get_object_or_404(Video, id=video_id, user=request.user)
    
    serializer = VideoAnalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Update video analysis configuration
    video.analysis_types = serializer.validated_data['analysis_types']
    video.custom_rules = serializer.validated_data.get('custom_rules', {})
    video.save()
    
    # Start background processing
    process_video_analysis.delay(video.id, serializer.validated_data)
    
    return Response({
        'message': 'Video analysis started',
        'video_id': str(video.id),
        'analysis_types': video.analysis_types
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def video_analysis_status(request, video_id):
    """API view to get video analysis status"""
    
    video = get_object_or_404(Video, id=video_id, user=request.user)
    
    return Response({
        'video_id': str(video.id),
        'status': video.status,
        'processing_started_at': video.processing_started_at,
        'processing_completed_at': video.processing_completed_at,
        'processing_error': video.processing_error,
        'events_count': video.events.count(),
        'violations_count': video.events.filter(is_violation=True).count()
    }, status=status.HTTP_200_OK)

class VideoFramesView(generics.ListAPIView):
    """API view for listing video frames"""
    
    serializer_class = VideoFrameSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        video_id = self.kwargs['video_id']
        video = get_object_or_404(Video, id=video_id, user=self.request.user)
        return VideoFrame.objects.filter(video=video).order_by('timestamp')

class VideoEventsView(generics.ListCreateAPIView):
    """API view for listing and creating video events"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventCreateSerializer
        return EventSerializer
    
    def get_queryset(self):
        video_id = self.kwargs['video_id']
        video = get_object_or_404(Video, id=video_id, user=self.request.user)
        queryset = Event.objects.filter(video=video)
        
        # Filter by severity if provided
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by violation status if provided
        is_violation = self.request.query_params.get('is_violation')
        if is_violation is not None:
            queryset = queryset.filter(is_violation=is_violation.lower() == 'true')
        
        # Filter by time range if provided
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        if start_time:
            queryset = queryset.filter(start_time__gte=float(start_time))
        if end_time:
            queryset = queryset.filter(start_time__lte=float(end_time))
        
        return queryset.order_by('start_time')

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for event detail, update, and delete"""
    
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Event.objects.filter(video__user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def search_videos(request):
    """API view for advanced video search"""
    
    serializer = VideoSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Video.objects.filter(user=request.user)
    
    # Apply search filters
    query = serializer.validated_data.get('query')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    status_filter = serializer.validated_data.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    date_from = serializer.validated_data.get('date_from')
    if date_from:
        queryset = queryset.filter(uploaded_at__gte=date_from)
    
    date_to = serializer.validated_data.get('date_to')
    if date_to:
        queryset = queryset.filter(uploaded_at__lte=date_to)
    
    has_violations = serializer.validated_data.get('has_violations')
    if has_violations is not None:
        if has_violations:
            queryset = queryset.filter(events__is_violation=True).distinct()
        else:
            queryset = queryset.exclude(events__is_violation=True).distinct()
    
    analysis_types = serializer.validated_data.get('analysis_types')
    if analysis_types:
        for analysis_type in analysis_types:
            queryset = queryset.filter(analysis_types__contains=[analysis_type])
    
    # Serialize results
    videos = VideoListSerializer(queryset, many=True).data
    
    return Response({
        'videos': videos,
        'count': len(videos)
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def video_statistics(request):
    """API view for user's video statistics"""
    
    videos = Video.objects.filter(user=request.user)
    
    stats = {
        'total_videos': videos.count(),
        'videos_by_status': {
            'uploaded': videos.filter(status='uploaded').count(),
            'processing': videos.filter(status='processing').count(),
            'completed': videos.filter(status='completed').count(),
            'failed': videos.filter(status='failed').count(),
        },
        'total_events': Event.objects.filter(video__user=request.user).count(),
        'total_violations': Event.objects.filter(
            video__user=request.user, 
            is_violation=True
        ).count(),
        'events_by_severity': {
            'info': Event.objects.filter(
                video__user=request.user, 
                severity='info'
            ).count(),
            'warning': Event.objects.filter(
                video__user=request.user, 
                severity='warning'
            ).count(),
            'violation': Event.objects.filter(
                video__user=request.user, 
                severity='violation'
            ).count(),
            'critical': Event.objects.filter(
                video__user=request.user, 
                severity='critical'
            ).count(),
        }
    }
    
    return Response(stats, status=status.HTTP_200_OK)

