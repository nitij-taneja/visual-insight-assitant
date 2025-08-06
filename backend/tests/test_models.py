import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from users.models import UserPreferences
from videos.models import Video, VideoFrame, Event, DetectedObject
from chat.models import Conversation, Message, ConversationContext
from analytics.models import AnalysisSession, VideoSummary, Insight, UserAnalytics

User = get_user_model()


class UserModelTests(TestCase):
    """Test cases for User and UserPreferences models"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_full_name_property(self):
        """Test the full_name property"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, 'Test User')
    
    def test_user_preferences_creation(self):
        """Test UserPreferences model"""
        user = User.objects.create_user(**self.user_data)
        preferences = UserPreferences.objects.create(
            user=user,
            theme='dark',
            notifications_enabled=False,
            default_analysis_types=['object_detection']
        )
        self.assertEqual(preferences.user, user)
        self.assertEqual(preferences.theme, 'dark')
        self.assertFalse(preferences.notifications_enabled)


class VideoModelTests(TestCase):
    """Test cases for Video-related models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a mock video file
        self.video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
    
    def test_create_video(self):
        """Test creating a video"""
        video = Video.objects.create(
            title='Test Video',
            description='A test video',
            file=self.video_file,
            uploaded_by=self.user,
            duration=120.5,
            file_size=1024000
        )
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.uploaded_by, self.user)
        self.assertEqual(video.status, 'uploaded')
        self.assertEqual(video.duration, 120.5)
    
    def test_video_frame_creation(self):
        """Test creating video frames"""
        video = Video.objects.create(
            title='Test Video',
            file=self.video_file,
            uploaded_by=self.user
        )
        
        frame = VideoFrame.objects.create(
            video=video,
            frame_number=100,
            timestamp=5.0,
            frame_data=b'fake frame data'
        )
        self.assertEqual(frame.video, video)
        self.assertEqual(frame.frame_number, 100)
        self.assertEqual(frame.timestamp, 5.0)
    
    def test_event_creation(self):
        """Test creating events"""
        video = Video.objects.create(
            title='Test Video',
            file=self.video_file,
            uploaded_by=self.user
        )
        
        event = Event.objects.create(
            video=video,
            title='Test Event',
            description='A test event',
            start_time=10.0,
            end_time=15.0,
            event_type='violation',
            severity='warning',
            confidence_score=0.85
        )
        self.assertEqual(event.video, video)
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.event_type, 'violation')
        self.assertEqual(event.severity, 'warning')
        self.assertTrue(event.is_violation)
    
    def test_detected_object_creation(self):
        """Test creating detected objects"""
        video = Video.objects.create(
            title='Test Video',
            file=self.video_file,
            uploaded_by=self.user
        )
        
        frame = VideoFrame.objects.create(
            video=video,
            frame_number=100,
            timestamp=5.0
        )
        
        detected_object = DetectedObject.objects.create(
            frame=frame,
            object_type='person',
            confidence_score=0.92,
            bounding_box={'x': 100, 'y': 150, 'width': 200, 'height': 300}
        )
        self.assertEqual(detected_object.frame, frame)
        self.assertEqual(detected_object.object_type, 'person')
        self.assertEqual(detected_object.confidence_score, 0.92)


class ChatModelTests(TestCase):
    """Test cases for Chat-related models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.video = Video.objects.create(
            title='Test Video',
            file=SimpleUploadedFile("test.mp4", b"content", content_type="video/mp4"),
            uploaded_by=self.user
        )
    
    def test_conversation_creation(self):
        """Test creating a conversation"""
        conversation = Conversation.objects.create(
            user=self.user,
            video=self.video,
            title='Test Conversation'
        )
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.video, self.video)
        self.assertEqual(conversation.title, 'Test Conversation')
    
    def test_message_creation(self):
        """Test creating messages"""
        conversation = Conversation.objects.create(
            user=self.user,
            video=self.video
        )
        
        message = Message.objects.create(
            conversation=conversation,
            content='Hello, AI!',
            sender='user'
        )
        self.assertEqual(message.conversation, conversation)
        self.assertEqual(message.content, 'Hello, AI!')
        self.assertEqual(message.sender, 'user')
    
    def test_conversation_context(self):
        """Test conversation context"""
        conversation = Conversation.objects.create(
            user=self.user,
            video=self.video
        )
        
        context = ConversationContext.objects.create(
            conversation=conversation,
            current_video_focus=self.video,
            context_data={'last_topic': 'events'}
        )
        self.assertEqual(context.conversation, conversation)
        self.assertEqual(context.current_video_focus, self.video)


class AnalyticsModelTests(TestCase):
    """Test cases for Analytics-related models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.video = Video.objects.create(
            title='Test Video',
            file=SimpleUploadedFile("test.mp4", b"content", content_type="video/mp4"),
            uploaded_by=self.user
        )
    
    def test_analysis_session_creation(self):
        """Test creating an analysis session"""
        session = AnalysisSession.objects.create(
            user=self.user,
            video=self.video,
            analysis_types=['object_detection', 'event_classification'],
            status='completed'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.video, self.video)
        self.assertEqual(session.status, 'completed')
    
    def test_video_summary_creation(self):
        """Test creating a video summary"""
        session = AnalysisSession.objects.create(
            user=self.user,
            video=self.video
        )
        
        summary = VideoSummary.objects.create(
            video=self.video,
            analysis_session=session,
            summary_text='This video contains multiple events.',
            key_insights=['High activity detected', 'No violations found'],
            statistics={'total_events': 5, 'violations': 0}
        )
        self.assertEqual(summary.video, self.video)
        self.assertEqual(summary.analysis_session, session)
        self.assertIn('High activity detected', summary.key_insights)
    
    def test_insight_creation(self):
        """Test creating insights"""
        insight = Insight.objects.create(
            video=self.video,
            insight_type='pattern',
            title='Movement Pattern Detected',
            description='Consistent movement pattern observed',
            confidence_score=0.88,
            metadata={'pattern_type': 'circular'}
        )
        self.assertEqual(insight.video, self.video)
        self.assertEqual(insight.insight_type, 'pattern')
        self.assertEqual(insight.confidence_score, 0.88)
    
    def test_user_analytics_creation(self):
        """Test creating user analytics"""
        analytics = UserAnalytics.objects.create(
            user=self.user,
            total_videos_uploaded=10,
            total_analysis_time=3600,
            most_used_analysis_types=['object_detection'],
            activity_stats={'daily_uploads': 2}
        )
        self.assertEqual(analytics.user, self.user)
        self.assertEqual(analytics.total_videos_uploaded, 10)
        self.assertEqual(analytics.total_analysis_time, 3600)


class ModelConstraintsTests(TestCase):
    """Test model constraints and validations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_unique_email_constraint(self):
        """Test that email must be unique"""
        User.objects.create_user(
            username='user1',
            email='unique@example.com',
            password='pass123'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='unique@example.com',  # Duplicate email
                password='pass123'
            )
    
    def test_video_status_choices(self):
        """Test video status field choices"""
        video = Video.objects.create(
            title='Test Video',
            file=SimpleUploadedFile("test.mp4", b"content", content_type="video/mp4"),
            uploaded_by=self.user,
            status='processing'
        )
        self.assertEqual(video.status, 'processing')
        
        # Test invalid status
        video.status = 'invalid_status'
        with self.assertRaises(Exception):
            video.full_clean()

