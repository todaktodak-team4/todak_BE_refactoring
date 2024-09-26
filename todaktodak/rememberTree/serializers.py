from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import rememberTree, Photo, Question, UserQuestionAnswer,Letters
from accounts.serializers import UserAdditionalInfoSerializer
 
class RememberSerializer(ModelSerializer):
    class Meta:
        model = rememberTree
        fields = ['id', 'treeName', 'myName', 'flowerType', 'growth_period']
       

class PhotoSerializer(ModelSerializer):

    class Meta:
        model = Photo
        fields =['id', 'rememberPhoto','description','rememberDate','comment','remember_tree']
    

class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerSerializer(ModelSerializer):
    class Meta:
        model = UserQuestionAnswer
        fields = '__all__'

    
class LetterSerializer(serializers.ModelSerializer):
    writer = UserAdditionalInfoSerializer(read_only=True)

    def create(self, validated_data):
        validated_data['writer'] = self.context['request'].user
        validated_data['remember_tree'] = self.context['remember_tree']
        return super().create(validated_data)

    class Meta:
        model = Letters
        fields = ['id', 'content', 'remember_tree', 'writer', 'uploaded_at']