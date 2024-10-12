from django.db import models
from accounts.models import CustomUser
from datetime import date
from django.utils import timezone

def user_photo_upload_to(instance, filename):
    user_id = instance.remember_tree.user.id
    return f'user_{user_id}/rememberTree_photos/{filename}'

# 기억나무 모델
class rememberTree(models.Model): 
    treeName = models.CharField(max_length=20)
    myName = models.CharField(max_length=100, null=False, default='토닥토닥') 
    flowerType = models.CharField(max_length=20, null=True, blank=True, default='')
    growth_period = models.DateField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trees')

    def __str__(self):
        return self.treeName

# 사진 모델
class Photo(models.Model):
    rememberPhoto = models.ImageField(upload_to=user_photo_upload_to, null=True, blank=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    rememberDate = models.DateField(default=date.today,null=True, blank=True)
    comment = models.CharField(max_length=2000, null = True, blank = True) 
    remember_tree = models.ForeignKey(rememberTree, on_delete=models.CASCADE, related_name='photos')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id} for {self.remember_tree.treeName}"
    
# 질문 모델
class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('DENIAL', 'Denial'),
        ('ANGER', 'Anger'),
        ('BARGAINING', 'Bargaining'),
        ('DEPRESSION', 'Depression'),
        ('ACCEPTANCE', 'Acceptance'),
    ]
    question_text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, null = False, default='') 
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.question_text

#매일 질문 하나씩
class DailyQuestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_daily_question')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    date_asked = models.DateField(auto_now_add=True)  # Automatically set to now when created

    def __str__(self):
        return f"{self.user.username} - {self.question.question_text} on {self.date_asked}"

# 대화 모델
class UserQuestionAnswer(models.Model):
    QUESTION_SOURCE_CHOICES = [
        ('PREDEFINED', 'Predefined Question'),  # Question from the Question model
        ('AI', 'AI-generated Question'),  # AI-generated question
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_question_answers')
    question = models.TextField()  # This will store both predefined and AI-generated questions
    answer_text = models.TextField()
    date_answered = models.DateField(default=timezone.now)
    source_type = models.CharField(max_length=10, choices=QUESTION_SOURCE_CHOICES, default='PREDEFINED')

    class Meta:
        unique_together = ('user', 'date_answered', 'question')  # Ensure unique answers per day

    def __str__(self):
        return f"Answer by {self.user.username} to {self.question} on {self.date_answered} (Source: {self.source_type})"

# 감정 모델
class UserEmotion(models.Model):
    EMOTION_TYPE_CHOICES = [
        ('DENIAL', 'Denial'),
        ('ANGER', 'Anger'),
        ('BARGAINING', 'Bargaining'),
        ('DEPRESSION', 'Depression'),
        ('ACCEPTANCE', 'Acceptance'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='emotions')
    emotion_type = models.CharField(max_length=20, choices=EMOTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s emotion: {self.emotion_type} at {self.created_at}"
    
#편지모델
class Letters(models.Model):
    content = models.TextField(max_length=780, null = False)
    remember_tree = models.ForeignKey(rememberTree, on_delete=models.CASCADE, related_name='letters')
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='letters')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Letters {self.id} by {self.writer.username} for {self.remember_tree.treeName}"
