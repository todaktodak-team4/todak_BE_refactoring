from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import MemorialHall, Wreath, Message

class MemorialHallSerializer(ModelSerializer) :
    wreath_count = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta :
        model = MemorialHall
        # fields = '__all__'
        fields = ['id', 'name', 'date', 'info', 'public', 'private', 'thumbnail', 'participation', 'token', 'wreath_count', 'message_count']
        
    extra_kwargs = {
            'participation': {'required': False, 'default': []},
            'token': {'read_only': True}  # token 필드를 읽기 전용으로 설정
    }

    def get_wreath_count(self, obj):
        return obj.wreath_set.count()
    
    def get_message_count(self, obj):
        return obj.message_set.count()
    
class WreathSerializer(ModelSerializer) :
    nickname = serializers.ReadOnlyField(source = 'nickname.nickname')
    profile = serializers.SerializerMethodField()
    hall_name = serializers.ReadOnlyField(source='hall.name')
    class Meta :
        model = Wreath
        fields = ['id', 'donation', 'comment', 'name', 'hall', 'hall_name', 'nickname', 'profile', 'created_at']
        
    def get_profile(self, obj):
        if obj.nickname.profile and hasattr(obj.nickname.profile, 'url'):
            return obj.nickname.profile.url
        return None  # 기본 이미지 URL을 반환하거나 None을 반환
        
class MessageSerializer(ModelSerializer) :
    nickname = serializers.ReadOnlyField(source = 'nickname.nickname')
    profile = serializers.SerializerMethodField()
    hall_name = serializers.ReadOnlyField(source = 'hall.name')
    
    class Meta :
        model = Message
        fields = ['id', 'content', 'hall', 'hall_name', 'nickname', 'profile', 'created_at']
        
    def get_profile(self, obj):
        if obj.nickname.profile and hasattr(obj.nickname.profile, 'url'):
            return obj.nickname.profile.url
        return None  # 기본 이미지 URL을 반환하거나 None을 반환