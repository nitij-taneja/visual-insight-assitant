from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserPreferences

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'password', 'password_confirm', 'preferred_language'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create default preferences
        UserPreferences.objects.create(user=user)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'profile_picture', 'bio', 'preferred_language',
            'total_videos_analyzed', 'total_analysis_time', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'total_videos_analyzed', 
            'total_analysis_time', 'created_at', 'updated_at'
        ]

class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences"""
    
    class Meta:
        model = UserPreferences
        fields = [
            'default_analysis_types', 'confidence_threshold', 
            'enable_real_time_alerts', 'email_notifications',
            'push_notifications', 'analysis_complete_notifications',
            'violation_alert_notifications', 'theme', 'dashboard_layout'
        ]
    
    def validate_confidence_threshold(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Confidence threshold must be between 0.0 and 1.0")
        return value

class UserStatsSerializer(serializers.ModelSerializer):
    """Serializer for user statistics"""
    
    videos_this_month = serializers.SerializerMethodField()
    analysis_time_this_month = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'total_videos_analyzed', 'total_analysis_time',
            'videos_this_month', 'analysis_time_this_month'
        ]
    
    def get_videos_this_month(self, obj):
        # This would be implemented with proper date filtering
        return obj.videos.filter(
            uploaded_at__month=timezone.now().month
        ).count()
    
    def get_analysis_time_this_month(self, obj):
        # This would be implemented with proper date filtering and aggregation
        return "0:00:00"  # Placeholder

