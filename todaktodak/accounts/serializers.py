from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class UserBasicInfoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'password_confirm', 'email','date_joined']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserAdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['nickname', 'profile', 'phone','postal_address', 'address', 'zone_code']



class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    new_username = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['new_username', 'password', 'nickname', 'profile', 'phone','postal_address' ,'address','zone_code']
        
    def validate(self, attrs):
        # 비밀번호 확인 없이 비밀번호만 확인
        if 'password' in attrs:
            validate_password(attrs['password'])
        return attrs

    def update(self, instance, validated_data):
        # 비밀번호 업데이트
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # 아이디 업데이트
        new_username = validated_data.pop('new_username', None)
        if new_username:
            instance.username = new_username
        
        # 기타 필드 업데이트
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.profile = validated_data.get('profile', instance.profile)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        instance.postal_address = validated_data.get('postal_address', instance.postal_address)
        instance.zone_code = validated_data.get('zone_code', instance.zone_code)
        instance.save()
        return instance


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['profile']

    def update(self, instance, validated_data):
        profile = validated_data.get('profile', None)
        if profile:
            instance.profile = profile
            instance.save()
        return instance