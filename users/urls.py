from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.login_view, name='user-login'),
    path('logout/', views.logout_view, name='user-logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('preferences/', views.UserPreferencesView.as_view(), name='user-preferences'),
    path('stats/', views.UserStatsView.as_view(), name='user-stats'),
    path('change-password/', views.change_password_view, name='change-password'),
    path('delete-account/', views.delete_account_view, name='delete-account'),
]

