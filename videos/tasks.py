from celery import shared_task
from django.utils import timezone
from .models import Video, VideoFrame, DetectedObject, Event
import cv2
import numpy as np
import os
import tempfile
from datetime import timedelta

@shared_task
def process_video_analysis(video_id, analysis_config=None):
    """
    Celery task for processing video analysis
    This is a simplified version - in production, this would integrate with actual AI models
    """
    try:
        video = Video.objects.get(id=video_id)
        video.start_processing()
        
        # Extract video metadata
        extract_video_metadata(video)
        
        # Extract frames
        frames = extract_video_frames(video)
        
        # Perform analysis based on configuration
        if analysis_config:
            analysis_types = analysis_config.get('analysis_types', [])
        else:
            analysis_types = video.analysis_types
        
        for analysis_type in analysis_types:
            if analysis_type == 'object_detection':
                perform_object_detection(video, frames)
            elif analysis_type == 'event_classification':
                perform_event_classification(video, frames)
            elif analysis_type == 'guideline_adherence':
                check_guideline_adherence(video)
        
        # Generate summary events
        generate_summary_events(video)
        
        video.complete_processing()
        
        return {
            'status': 'success',
            'video_id': str(video.id),
            'frames_processed': len(frames),
            'events_detected': video.events.count()
        }
        
    except Exception as e:
        video = Video.objects.get(id=video_id)
        video.fail_processing(str(e))
        return {
            'status': 'error',
            'video_id': str(video.id),
            'error': str(e)
        }

def extract_video_metadata(video):
    """Extract metadata from video file"""
    try:
        cap = cv2.VideoCapture(video.file.path)
        
        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate duration
        duration_seconds = frame_count / fps if fps > 0 else 0
        duration = timedelta(seconds=duration_seconds)
        
        # Update video metadata
        video.duration = duration
        video.resolution_width = width
        video.resolution_height = height
        video.frame_rate = fps
        video.file_size = os.path.getsize(video.file.path)
        video.save()
        
        cap.release()
        
    except Exception as e:
        print(f"Error extracting metadata: {e}")

def extract_video_frames(video, interval=1.0):
    """Extract frames from video at specified interval"""
    frames = []
    
    try:
        cap = cv2.VideoCapture(video.file.path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval)  # Extract frame every 'interval' seconds
        
        frame_number = 0
        extracted_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % frame_interval == 0:
                timestamp = frame_number / fps
                
                # Save frame to temporary file
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, frame)
                    
                    # Create VideoFrame object
                    video_frame = VideoFrame.objects.create(
                        video=video,
                        frame_number=frame_number,
                        timestamp=timestamp,
                        width=frame.shape[1],
                        height=frame.shape[0],
                        file_size=os.path.getsize(temp_file.name)
                    )
                    
                    # Save frame image
                    with open(temp_file.name, 'rb') as f:
                        video_frame.image.save(
                            f'frame_{frame_number}.jpg',
                            f,
                            save=True
                        )
                    
                    frames.append(video_frame)
                    extracted_count += 1
                    
                    # Clean up temp file
                    os.unlink(temp_file.name)
            
            frame_number += 1
        
        cap.release()
        
    except Exception as e:
        print(f"Error extracting frames: {e}")
    
    return frames

def perform_object_detection(video, frames):
    """
    Perform object detection on video frames
    This is a mock implementation - in production, this would use actual AI models
    """
    # Mock object classes that might be detected in traffic scenarios
    mock_objects = [
        'car', 'truck', 'bus', 'motorcycle', 'bicycle', 'person', 
        'traffic_light', 'stop_sign', 'crosswalk'
    ]
    
    for frame in frames:
        # Mock detection - randomly generate some objects
        import random
        num_objects = random.randint(0, 5)
        
        for i in range(num_objects):
            obj_class = random.choice(mock_objects)
            confidence = random.uniform(0.7, 0.95)
            
            # Random bounding box coordinates (normalized)
            bbox_x = random.uniform(0, 0.8)
            bbox_y = random.uniform(0, 0.8)
            bbox_width = random.uniform(0.1, 0.2)
            bbox_height = random.uniform(0.1, 0.2)
            
            DetectedObject.objects.create(
                frame=frame,
                class_name=obj_class,
                confidence=confidence,
                bbox_x=bbox_x,
                bbox_y=bbox_y,
                bbox_width=bbox_width,
                bbox_height=bbox_height,
                track_id=f"track_{i}_{frame.frame_number}"
            )
        
        frame.has_objects = num_objects > 0
        frame.save()

def perform_event_classification(video, frames):
    """
    Perform event classification
    This is a mock implementation - in production, this would use actual AI models
    """
    # Mock events that might be detected
    mock_events = [
        {
            'type': 'vehicle_movement',
            'title': 'Vehicle Movement Detected',
            'description': 'A vehicle was observed moving through the scene',
            'severity': 'info'
        },
        {
            'type': 'pedestrian_crossing',
            'title': 'Pedestrian Crossing',
            'description': 'A pedestrian crossed the street',
            'severity': 'info'
        },
        {
            'type': 'traffic_light_change',
            'title': 'Traffic Light Change',
            'description': 'Traffic light changed state',
            'severity': 'info'
        },
        {
            'type': 'sudden_stop',
            'title': 'Sudden Vehicle Stop',
            'description': 'A vehicle stopped suddenly',
            'severity': 'warning'
        }
    ]
    
    import random
    
    # Generate some random events
    for i in range(random.randint(2, 8)):
        event_data = random.choice(mock_events)
        start_time = random.uniform(0, float(video.duration.total_seconds()) - 5)
        end_time = start_time + random.uniform(1, 5)
        
        Event.objects.create(
            video=video,
            event_type=event_data['type'],
            title=event_data['title'],
            description=event_data['description'],
            severity=event_data['severity'],
            start_time=start_time,
            end_time=end_time,
            confidence=random.uniform(0.7, 0.95),
            detected_by='mock_classifier'
        )

def check_guideline_adherence(video):
    """
    Check for guideline adherence violations
    This is a mock implementation
    """
    import random
    
    # Mock violation scenarios
    violations = [
        {
            'type': 'speed_violation',
            'title': 'Speed Limit Violation',
            'description': 'Vehicle exceeded speed limit',
            'severity': 'violation',
            'guideline': 'Traffic Speed Regulations'
        },
        {
            'type': 'red_light_violation',
            'title': 'Red Light Violation',
            'description': 'Vehicle ran through red light',
            'severity': 'critical',
            'guideline': 'Traffic Signal Compliance'
        },
        {
            'type': 'wrong_lane',
            'title': 'Wrong Lane Usage',
            'description': 'Vehicle used incorrect lane',
            'severity': 'warning',
            'guideline': 'Lane Usage Rules'
        }
    ]
    
    # Randomly generate some violations
    for i in range(random.randint(0, 3)):
        violation = random.choice(violations)
        start_time = random.uniform(0, float(video.duration.total_seconds()) - 2)
        
        Event.objects.create(
            video=video,
            event_type=violation['type'],
            title=violation['title'],
            description=violation['description'],
            severity=violation['severity'],
            start_time=start_time,
            end_time=start_time + random.uniform(1, 3),
            confidence=random.uniform(0.8, 0.95),
            detected_by='guideline_checker',
            is_violation=True,
            guideline_reference=violation['guideline']
        )

def generate_summary_events(video):
    """Generate summary events based on detected events"""
    events = video.events.all()
    violations = events.filter(is_violation=True)
    
    if violations.exists():
        Event.objects.create(
            video=video,
            event_type='summary',
            title=f'Analysis Complete: {violations.count()} Violations Found',
            description=f'Video analysis completed. Found {events.count()} total events, including {violations.count()} violations.',
            severity='warning' if violations.count() > 0 else 'info',
            start_time=0,
            end_time=float(video.duration.total_seconds()),
            confidence=1.0,
            detected_by='summary_generator'
        )

