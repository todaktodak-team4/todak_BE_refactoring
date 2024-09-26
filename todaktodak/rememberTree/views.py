from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import rememberTree,Photo, Question, UserQuestionAnswer, Letters
from .serializers import RememberSerializer,PhotoSerializer,QuestionSerializer,AnswerSerializer,LetterSerializer
from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from datetime import timedelta
import random

#APIView 사용 : HTTP request에 대한 처리
#TreeAPIView : 기억나무 심기 view
class TreeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, user_id=None):
        if pk:
            # 특정 기억나무 조회
            tree = get_object_or_404(rememberTree, pk=pk, user=request.user)
            serializer = RememberSerializer(tree)
        elif user_id:
            # 사용자의 ID로 기억나무 조회
            trees = rememberTree.objects.filter(user_id=user_id)
            serializer = RememberSerializer(trees, many=True)
        else:
            # 인증된 사용자가 만든 기억나무 조회
            trees = rememberTree.objects.filter(user=request.user)
            serializer = RememberSerializer(trees, many=True)
        
        return Response(serializer.data)

    def post(self, request):
        print(request.user)
        print(request.data)
        data = {
            'treeName': request.data.get('tree_name'),
            'myName': request.data.get('my_name'),
            'flowerType': request.data.get('flower_type'),
            'growth_period': request.data.get('growth_period')
        }
        serializer = RememberSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # 인증된 사용자를 설정
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        data = {
            'treeName': request.data.get('tree_name'),
            'myName': request.data.get('my_name'),
            'flowerType': request.data.get('flower_type'),
            'growth_period': request.data.get('growth_period')
        }
        tree = get_object_or_404(rememberTree, pk=pk)
        serializer = RememberSerializer(tree, data=data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tree = get_object_or_404(rememberTree, pk=pk)
        tree.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#PhotoAPIView : 기억나무 앨범 view
class PhotoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, tree_id, pk=None):
        tree = get_object_or_404(rememberTree, pk=tree_id)
        if pk:
            photo = get_object_or_404(Photo, pk=pk, remember_tree=tree)
            serializer = PhotoSerializer(photo)
        else:
            photos = Photo.objects.filter(remember_tree=tree)
            serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

    def post(self, request, tree_id):
        print(request.data)
        tree = get_object_or_404(rememberTree, pk=tree_id)
        data = {
            'rememberPhoto': request.data.get('rememberPhoto'),
            'description': request.data.get('description'),
            'rememberDate': request.data.get('rememberDate'),
            'comment': request.data.get('comment'),
            'remember_tree': tree.id,
        }
        serializer = PhotoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, tree_id, pk):
        tree = get_object_or_404(rememberTree, pk=tree_id)
        photo = get_object_or_404(Photo, pk=pk, remember_tree=tree)
        data = {
            'rememberPhoto': request.data.get('remember_photo'),
            'description': request.data.get('description'),
            'rememberDate': request.data.get('rememberDate'),
            'comment': request.data.get('comment'),
            'remember_tree': tree.id,
        }
        serializer = PhotoSerializer(photo, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, tree_id, pk):
        tree = get_object_or_404(rememberTree, pk=tree_id)
        photo = get_object_or_404(Photo, pk=pk, remember_tree=tree)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


# 기억나무 질문 view
class DailyQuestionAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # 질문 타입과 주기 설정
    QUESTION_TYPES = ['DENIAL', 'ANGER', 'BARGAINING', 'DEPRESSION', 'ACCEPTANCE']
    PERIOD_DAYS = 18

    def get(self, request):
        user = request.user
        today = timezone.localtime(timezone.now()).date()  # 로컬 시간대의 날짜 가져오기
        date_joined = user.date_joined

        # 가입일과 오늘 날짜 사이의 차이 계산
        day_count = (today - date_joined).days
        print(f"오늘 날짜 : {today}")
        print(f"가입일: {date_joined}")
        print(f"가입일과 오늘 날짜 사이의 차이 계산: {day_count}")

        # 18일 주기를 기준으로 질문 타입 결정
        period_index = (day_count // self.PERIOD_DAYS) % len(self.QUESTION_TYPES)
        question_type = self.QUESTION_TYPES[period_index]
        print(f"질문 타입: {question_type}")
        # 오늘 이미 답변이 있는지 확인
        answered_questions = UserQuestionAnswer.objects.filter(user=user, date_answered=today).values_list('question_id', flat=True)

       
        if answered_questions:
            return Response({"detail": "오늘 받을 수 있는 질문이 없습니다1."}, status=status.HTTP_404_NOT_FOUND)
        
        # 해당 타입의 질문을 랜덤으로 반환 (이미 답변한 질문은 제외)
        questions = Question.objects.filter(question_type=question_type).exclude(id__in=answered_questions)
        
        if not questions:
            return Response({"detail": "오늘 받을 수 있는 질문이 없습니다2."}, status=status.HTTP_404_NOT_FOUND)

        question = random.choice(questions)
        serializer = QuestionSerializer(question)
        return Response(serializer.data)
    
    def post(self, request):
        today = timezone.localtime(timezone.now()).date()  # 로컬 시간대의 날짜 가져오기
        user = request.user

        # 오늘 날짜에 이미 답변이 있는지 확인
        if UserQuestionAnswer.objects.filter(user=user, date_answered=today).exists():
            return Response({"detail": "오늘 이미 답변 완료하셨습니다3."}, status=status.HTTP_400_BAD_REQUEST)

        question_id = request.data.get('question_id')
        answer_text = request.data.get('answer_text')

        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return Response({"detail": "질문을 찾을 수 없습니다4."}, status=status.HTTP_404_NOT_FOUND)
        
    
     # 사용자의 답변을 저장
        answer = UserQuestionAnswer.objects.create(
            user=user, 
            question=question, 
            answer_text=answer_text, 
            date_answered=today
        )

        # 답변을 직렬화
        serializer = AnswerSerializer(answer)
        
        return Response({"detail": "Answer recorded successfully.", "answer": serializer.data}, status=status.HTTP_201_CREATED)
    

# 오늘의 질문과 답변 가져오기
class GetTodayAnswersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localtime(timezone.now()).date()  # 로컬 시간대의 날짜 가져오기

        answers = UserQuestionAnswer.objects.filter(user=user, date_answered=today)
        if not answers:
            return Response({"detail": "오늘 답변이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        question_ids = answers.values_list('question_id', flat=True)
        questions = Question.objects.filter(id__in=question_ids)

        print(f"로그인한 사용자: {user}")
        print(f"오늘 날짜: {today}")
        print(f"답변 목록: {answers}")
        print(f"질문 목록: {questions}")
        answer_with_question = []
        for answer in answers:
            question = questions.get(id=answer.question_id)
            answer_with_question.append({
                'question': QuestionSerializer(question).data,
                'answer_text': answer.answer_text,
                'date_answered': answer.date_answered
            })

        return Response(answer_with_question)
    
class LettersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, tree_id, pk=None):
        tree = get_object_or_404(rememberTree, pk=tree_id)
        if pk:
            letter = get_object_or_404(Letters, pk=pk, remember_tree=tree)
            serializer = LetterSerializer(letter)
        else:
            letters = Letters.objects.filter(remember_tree=tree)
            serializer = LetterSerializer(letters, many=True)
        return Response(serializer.data)

    def post(self, request, tree_id):
        tree = get_object_or_404(rememberTree, pk=tree_id)

        serializer = LetterSerializer(data=request.data, context={
            'request': request,
            'remember_tree': tree
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)