from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import rememberTree,Photo, Question, UserQuestionAnswer, Letters, UserEmotion,DailyQuestion  # 감정 저장을 위한 모델 추가
from .serializers import RememberSerializer,PhotoSerializer,UserQuestionAnswerSerializer,DailyQuestionSerializer,LetterSerializer
from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from datetime import timedelta
import random
import openai

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
 
 #하루가 지났는지 확인 (last_emotion가 있다는 조건임. 없으면 False나옴)
def has_a_day_passed(user):
        today = timezone.localtime(timezone.now()).date()
        print(f"today: {today}")
        # Fetch the last UserEmotion entry for the user
        last_emotion = UserEmotion.objects.filter(user=user).last()
       
        if last_emotion:
            last_date = last_emotion.created_at.date()  # Assuming this is a DateField
            print(f"last_date: {last_date}")
            return (today - last_date).days >= 1
        
        return False  #하루가 안지난거지   

class ChatCounselingAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    QUESTION_TYPES = ['DENIAL', 'ANGER', 'BARGAINING', 'DEPRESSION', 'ACCEPTANCE']
    PERIOD_DAYS = 18
    user_conversations = {}  # 사용자별 대화 상태 저장

    def get_daily_question(self, user):
        
        print(f"has_a_day_passed: true")
        today = timezone.localtime(timezone.now()).date()
        print(f"today: {today}")
        date_joined = user.date_joined
        print(f"date_joined: {date_joined}")
        day_count = (today - date_joined).days
        print(f"day_count: {day_count}")

       # 같은 날에 답한 답이 있다면
        existing_answer = UserQuestionAnswer.objects.filter(user=user, date_answered=today).exists()

        if existing_answer:
            #continue 응답 보내고 이전 답들과 질문 가져온 다음에 대화 계속하기
            return "continue" 

        #하루가 지났다면
        if has_a_day_passed(user):
            
            # 감정에 따른 질문 타입 결정
            last_emotion = UserEmotion.objects.filter(user=user).last()
            if last_emotion:
                question_type = last_emotion.emotion_type  # 마지막 감정에 따른 질문 타입
                print(f"question_type: {question_type}")
            
            else:
                # 감정 데이터가 없을 경우 기본 질문
                period_index = (day_count // self.PERIOD_DAYS) % len(self.QUESTION_TYPES)
                question_type = self.QUESTION_TYPES[period_index]

        # 해당 타입의 질문을 랜덤으로 반환
            questions = Question.objects.filter(question_type=question_type)
            if questions.exists():
                question = questions.order_by('?').first()  # 랜덤으로 선택
                DailyQuestion.objects.create(user=user, question=question)
                return question
           
        else:
            # 하루가 안지남. 대화하다가 다시나갔다가 들어왔을 수도, 아니면 대화가 처음일수도
            #대화가 처음일때만을 처리해야함. 그럼 이전 대화에서 해당 날짜의 답이 있으면 그냥 넘기기
            print(f"has_a_day_passed: false")
            period_index = (day_count // self.PERIOD_DAYS) % len(self.QUESTION_TYPES)
            question_type = self.QUESTION_TYPES[period_index]
            questions = Question.objects.filter(question_type=question_type)
            if questions.exists():
                question = questions.order_by('?').first()  # 랜덤으로 선택
                DailyQuestion.objects.create(user=user, question=question)
                return question
           

    def post(self, request):
        user = request.user
        user_message = request.data.get('message')

        if not user_message:
            return Response({"detail": "메시지를 제공해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 대화 상태 초기화
        if user.id not in self.user_conversations:
            self.user_conversations[user.id] = []

        # 사용자 답변 저장
        self.user_conversations[user.id].append({"role": "user", "content": user_message})

        # 감정 분석을 위한 OpenAI API 호출
        try:
            emotion_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
                max_tokens=100
            )

            # 감정 분석 결과를 기반으로 AI 질문 생성
            emotion_analysis = emotion_response['choices'][0]['message']['content']
            
            print(f"Emotion Analysis: {emotion_analysis}")
             # 감정 분석 결과에서 QUESTION_TYPES로 매핑
            emotion_type = self.map_emotion_to_type(emotion_analysis)
            print(f"Emotion Type: {emotion_type}")
             # 감정 분석 결과 저장
            UserEmotion.objects.create(user=user, emotion_type=emotion_type)

            # AI의 후속 질문 생성
            follow_up_question = f"{emotion_analysis}"
            print(f"follow_up_question: {follow_up_question}")
            # AI 질문을 대화 상태에 추가
            self.user_conversations[user.id].append({"role": "assistant", "content": follow_up_question})

            UserQuestionAnswer.objects.create(
                user=user,
                question=follow_up_question,  # AI-generated question
                answer_text=user_message,  # User's answer to the AI question
                source_type='AI'  # Marking this as an AI question
     )

            return Response({"message": follow_up_question}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error communicating with OpenAI: {str(e)}")
            return Response({"detail": "AI와의 통신 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def map_emotion_to_type(self, emotion_analysis):
        # 여기서 사용자 답변에 따라 감정 상태를 매핑합니다.
        if "슬픔" in emotion_analysis or "우울" in emotion_analysis:
            return 'DEPRESSION'
        elif "분노" in emotion_analysis or "화" in emotion_analysis:
            return 'ANGER'
        elif "거부" in emotion_analysis:
            return 'DENIAL'
        elif "협상" in emotion_analysis:
            return 'BARGAINING'
        elif "수용" in emotion_analysis:
            return 'ACCEPTANCE'
        
        # 기본값을 설정할 수 있습니다.
        return 'ACCEPTANCE'  # 기본값
    
    def get(self, request):
        user = request.user
        question = self.get_daily_question(user)

        if not question:
            return Response({"detail": "오늘 받을 질문이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if user.id not in self.user_conversations:
                self.user_conversations[user.id] = []  # Initialize the conversation list for the user

   
        # 질문을 대화 상태에 추가
        self.user_conversations[user.id].append({"role": "assistant", "content": question.question_text})

        return Response({"question": question.question_text}, status=status.HTTP_200_OK)

#하루의 대화내역 불러오기
class DailyQuestionView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        # Get the current date
        today = timezone.localdate()
        user = request.user
        print(f"Today: {today}")
        print(f"user: {user}")
        
        daily_question = DailyQuestion.objects.filter(user=user, date_asked=today).first() 
        print(f"Daily Question: {daily_question}")

       
        user_answers = UserQuestionAnswer.objects.filter(user=user, date_answered=today)
        print(f"User Answers: {user_answers}")

        # Serialize the data
        daily_question_data = DailyQuestionSerializer(daily_question).data if daily_question else None
        user_answers_data = UserQuestionAnswerSerializer(user_answers, many=True).data

        # Create the response data
        response_data = {
            'daily_question': daily_question_data,
            'user_answers': user_answers_data,
        }

        return Response(response_data)
      
# # 기억나무 질문 view
# class DailyQuestionAPIView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     # 질문 타입과 주기 설정
#     QUESTION_TYPES = ['DENIAL', 'ANGER', 'BARGAINING', 'DEPRESSION', 'ACCEPTANCE']
#     PERIOD_DAYS = 18

#     def get(self, request):
#         user = request.user
#         today = timezone.localtime(timezone.now()).date()  # 로컬 시간대의 날짜 가져오기
#         date_joined = user.date_joined

#         # 가입일과 오늘 날짜 사이의 차이 계산
#         day_count = (today - date_joined).days
#         print(f"오늘 날짜 : {today}")
#         print(f"가입일: {date_joined}")
#         print(f"가입일과 오늘 날짜 사이의 차이 계산: {day_count}")

#         # 18일 주기를 기준으로 질문 타입 결정
#         period_index = (day_count // self.PERIOD_DAYS) % len(self.QUESTION_TYPES)
#         question_type = self.QUESTION_TYPES[period_index]
#         print(f"질문 타입: {question_type}")
#         # 오늘 이미 답변이 있는지 확인
#         answered_questions = UserQuestionAnswer.objects.filter(user=user, date_answered=today).values_list('question_id', flat=True)

       
#         if answered_questions:
#             return Response({"detail": "오늘 받을 수 있는 질문이 없습니다1."}, status=status.HTTP_404_NOT_FOUND)
        
#         # 해당 타입의 질문을 랜덤으로 반환 (이미 답변한 질문은 제외)
#         questions = Question.objects.filter(question_type=question_type).exclude(id__in=answered_questions)
        
#         if not questions:
#             return Response({"detail": "오늘 받을 수 있는 질문이 없습니다2."}, status=status.HTTP_404_NOT_FOUND)

#         question = random.choice(questions)
#         serializer = QuestionSerializer(question)
#         return Response(serializer.data)
    
#     def post(self, request):
#         today = timezone.localtime(timezone.now()).date()  # 로컬 시간대의 날짜 가져오기
#         user = request.user

#         # 오늘 날짜에 이미 답변이 있는지 확인
#         if UserQuestionAnswer.objects.filter(user=user, date_answered=today).exists():
#             return Response({"detail": "오늘 이미 답변 완료하셨습니다3."}, status=status.HTTP_400_BAD_REQUEST)

#         question_id = request.data.get('question_id')
#         answer_text = request.data.get('answer_text')

#         try:
#             question = Question.objects.get(pk=question_id)
#         except Question.DoesNotExist:
#             return Response({"detail": "질문을 찾을 수 없습니다4."}, status=status.HTTP_404_NOT_FOUND)
        
    
#      # 사용자의 답변을 저장
#         answer = UserQuestionAnswer.objects.create(
#             user=user, 
#             question=question, 
#             answer_text=answer_text, 
#             date_answered=today
#         )

#         # 답변을 직렬화
#         serializer = AnswerSerializer(answer)
        
#         return Response({"detail": "Answer recorded successfully.", "answer": serializer.data}, status=status.HTTP_201_CREATED)
    

# # 오늘의 질문과 답변 가져오기
# class GetTodayAnswersAPIView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         today = timezone.localtime(timezone.now()).date()  # 로컬 시간대의 날짜 가져오기

#         answers = UserQuestionAnswer.objects.filter(user=user, date_answered=today)
#         if not answers:
#             return Response({"detail": "오늘 답변이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

#         question_ids = answers.values_list('question_id', flat=True)
#         questions = Question.objects.filter(id__in=question_ids)

#         print(f"로그인한 사용자: {user}")
#         print(f"오늘 날짜: {today}")
#         print(f"답변 목록: {answers}")
#         print(f"질문 목록: {questions}")
#         answer_with_question = []
#         for answer in answers:
#             question = questions.get(id=answer.question_id)
#             answer_with_question.append({
#                 'question': QuestionSerializer(question).data,
#                 'answer_text': answer.answer_text,
#                 'date_answered': answer.date_answered
#             })

#         return Response(answer_with_question)
    
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