from django.urls import path
from .views import TreeAPIView,PhotoAPIView,LettersAPIView,ChatCounselingAPIView,DailyQuestionView

urlpatterns = [
    path('rememberTree/', TreeAPIView.as_view()),
    path('rememberTree/<int:pk>/', TreeAPIView.as_view()),
    path('rememberTree/user/<int:user_id>/', TreeAPIView.as_view(), name='user-tree-list'),  # 특정 사용자의 기억나무 조회
    path('rememberTree/<int:tree_id>/photos/', PhotoAPIView.as_view(), name='photo-list'),
    path('rememberTree/<int:tree_id>/photos/<int:pk>/', PhotoAPIView.as_view(), name='photo-detail'),
    # path('rememberTree/daily-question/', DailyQuestionAPIView.as_view(), name='daily-question'),
    # path('daily-question/today-answers/', GetTodayAnswersAPIView.as_view(), name='today-answers'),
    path('rememberTree/<int:tree_id>/letters/', LettersAPIView.as_view(), name='letters-list'),
    path('rememberTree/<int:tree_id>/letters/<int:pk>/', LettersAPIView.as_view(), name='letters-detail'),
    path('rememberTree/chat-counseling/', ChatCounselingAPIView.as_view(), name='chat-counseling'),  # POST a message or GET daily question
    path('rememberTree/daily-question-and-answer', DailyQuestionView.as_view(), name='daily-question_answer'),  # POST a message or GET daily question
]

# ,DailyQuestionAPIView,GetTodayAnswersAPIView