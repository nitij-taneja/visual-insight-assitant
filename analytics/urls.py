from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.AnalysisSessionListView.as_view(), name='analysis-sessions'),
    path('sessions/<uuid:pk>/', views.AnalysisSessionDetailView.as_view(), name='analysis-session-detail'),
    path('summaries/', views.VideoSummaryListView.as_view(), name='video-summaries'),
    path('summaries/<uuid:pk>/', views.VideoSummaryDetailView.as_view(), name='video-summary-detail'),
    path('insights/', views.InsightListView.as_view(), name='insights'),
    path('insights/<uuid:pk>/', views.InsightDetailView.as_view(), name='insight-detail'),
    path('user-analytics/', views.UserAnalyticsView.as_view(), name='user-analytics'),
    path('dashboard/', views.dashboard_data, name='dashboard-data'),
]

