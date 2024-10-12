from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import rememberTree, Photo, Question, UserQuestionAnswer,Letters, UserEmotion,DailyQuestion
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

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question  # Replace with your actual Question model
        fields = ['id', 'question_text']  # Adjust fields as needed

class DailyQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()  # Use the nested serializer for the question

    class Meta:
        model = DailyQuestion
        fields = ['id', 'user', 'question', 'date_asked']

    
    
class UserQuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuestionAnswer
        fields = ['id', 'user', 'question', 'answer_text', 'date_answered', 'source_type']
    

class UserEmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmotion
        fields = ['id', 'user', 'emotion_type', 'created_at']


class LetterSerializer(serializers.ModelSerializer):
    writer = UserAdditionalInfoSerializer(read_only=True)

    def create(self, validated_data):
        validated_data['writer'] = self.context['request'].user
        validated_data['remember_tree'] = self.context['remember_tree']
        return super().create(validated_data)

    class Meta:
        model = Letters
        fields = ['id', 'content', 'remember_tree', 'writer', 'uploaded_at']

