from django.urls import path
from . import views

urlpatterns = [
    path('', views.VideoListView.as_view(), name='video-list'),
    path('upload/', views.VideoUploadView.as_view(), name='video-upload'),
    path('search/', views.search_videos, name='video-search'),
    path('statistics/', views.video_statistics, name='video-statistics'),
    path('<uuid:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    path('<uuid:video_id>/analyze/', views.start_video_analysis, name='start-analysis'),
    path('<uuid:video_id>/status/', views.video_analysis_status, name='analysis-status'),
    path('<uuid:video_id>/frames/', views.VideoFramesView.as_view(), name='video-frames'),
    path('<uuid:video_id>/events/', views.VideoEventsView.as_view(), name='video-events'),
    path('events/<uuid:pk>/', views.EventDetailView.as_view(), name='event-detail'),
]

