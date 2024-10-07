from django.shortcuts import render
from .models import MemorialHall, Wreath, Message
from .serializers import MemorialHallSerializer, WreathSerializer, MessageSerializer
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Count, Value, BooleanField
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .pagenation import MemorialHallPagination, MessagePagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status 
from rest_framework.test import APIRequestFactory 
from badwords.models import BadWord

#추모관 페이지네이션(한페이지 6개 추모관)
class MemorialHallViewSet(ModelViewSet) :
    queryset = MemorialHall.objects.all()
    serializer_class = MemorialHallSerializer
    pagination_class = MemorialHallPagination
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        # 검색 기능이 포함된 list 액션에 대해 인증을 허용하지 않음
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

    
    #검색
    def get_queryset(self):
        user = self.request.user
        queryset = MemorialHall.objects.filter(approved=True, public=True).annotate(
            wreath_count=Count('wreath'),
            message_count=Count('message')
        ).order_by('-wreath_count', '-date')

        if user.is_authenticated:
            participated_ids = user.participation_halls.values_list('id', flat=True)
            queryset = queryset.annotate(
                is_participated=Value(True, output_field=BooleanField())
            ).filter(id__in=participated_ids) | queryset.annotate(
                is_participated=Value(False, output_field=BooleanField())
            ).exclude(id__in=participated_ids)

        search_keyword = self.request.GET.get('q', '')
        if search_keyword:
            queryset = queryset.filter(Q(name__icontains=search_keyword))

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    # 추모관 생성 시 신청한 사용자를 자동으로 participation에 추가
    def perform_create(self, serializer):
        instance = serializer.save()
        user = self.request.user
        instance.participation.add(user)  # 추모관 생성자를 participation에 추가

        # participate 메서드를 POST로 호출하여 참여 상태를 저장
        factory = APIRequestFactory()
        response = self.participate(self.request, pk=instance.id)
        # 디버깅을 위한 응답 로그 추가
        print(f'Participate response: {response.data}')
        # 생성자는 자동으로 참여 중 상태 반영
        return Response({'status': 'participated','id': instance.id,'is_participated': True}, status=status.HTTP_201_CREATED)
        
    #내가 참여한 추모관
    @action(detail=False, methods=['get'], url_path='my-participation')
    def my_participation(self, request):
        user = request.user
        queryset = MemorialHall.objects.filter(approved=True).annotate(
            wreath_count=Count('wreath'),
            message_count=Count('message')
        ).order_by('-wreath_count', '-date')

        participated_halls = queryset.filter(participation=user)
        serializer = self.get_serializer(participated_halls, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def participate(self, request, pk=None):
        hall = get_object_or_404(MemorialHall, pk=pk)
        
        if request.method == 'GET':
            user = request.user
            is_participated = hall.participation.filter(id=user.id).exists()
            return Response({'is_participated': is_participated})
        if hall.private:
            token = request.data.get('token')
            if not token or token != str(hall.token):
                return Response({'status': 'Invalid token'}, status=400)
        user = request.user
        hall.participation.add(user)
        return Response({'status': 'participated'})

    # 추모관 참여 취소하기
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unparticipate(self, request, pk=None):
        hall = get_object_or_404(MemorialHall, pk=pk)
        user = request.user
        hall.participation.remove(user)
        return Response({'status': 'unparticipated'})
    
    # 토큰을 통해 비공개 추모관 접근
    @action(detail=True, methods=['get'], url_path='access', permission_classes=[AllowAny])
    def access_private_hall(self, request, pk=None):
        token = request.query_params.get('token')
        hall = get_object_or_404(MemorialHall, pk=pk, token=token)
        serializer = self.get_serializer(hall)
        return Response(serializer.data) 
   
#헌화하기
class WreathViewSet(ModelViewSet):
    queryset = Wreath.objects.all()
    serializer_class = WreathSerializer
    pagination_class = None  # 페이지네이션을 사용하지 않도록 설정
    authentication_classes = [JWTAuthentication]


    def get_permissions(self):
        # 'list', 'retrieve', 'get' 액션에 대해 인증을 허용하지 않음
        if self.action in ['list', 'retrieve', 'get']:
            return [AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(nickname=self.request.user)
        
    def get_queryset(self):
        memorialHall_id = self.kwargs['memorialHall_id']
        return self.queryset.filter(hall_id=memorialHall_id).order_by('-created_at')[:3]
    
    # 내가 한 헌화 신청만 확인
    @action(detail=False, methods=['get'], url_path='my-wreaths')
    def my_wreaths(self, request):
        user = request.user
        my_wreaths = self.queryset.filter(nickname=user).order_by('-created_at')
        serializer = self.get_serializer(my_wreaths, many=True)
        return Response(serializer.data)
    
    # 토닥토닥
    @action(detail=True, methods=['get', 'post'])
    def todak(self, request, pk=None, memorialHall_id=None):
        wreath = get_object_or_404(Wreath, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in wreath.todak.all():
                wreath.todak.remove(user)
                return Response({'status': 'todak removed'})
            else:
                wreath.todak.add(user)
                return Response({'status': 'todak added'})
        elif request.method == 'GET':
            total_todak_count = wreath.todak.count()
            return Response({'total_todak': total_todak_count})
    # 공감해요
    @action(detail=True, methods=['get', 'post'])
    def sympathize(self, request, pk=None, memorialHall_id=None):
        wreath = get_object_or_404(Wreath, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in wreath.sympathize.all():
                wreath.sympathize.remove(user)
                return Response({'status': 'sympathize removed'})
            else:
                wreath.sympathize.add(user)
                return Response({'status': 'sympathize added'})
        elif request.method == 'GET':
            total_sympathize_count = wreath.sympathize.count()
            return Response({'total_sympathize': total_sympathize_count})
    # 슬퍼요
    @action(detail=True, methods=['get', 'post'])
    def sad(self, request, pk=None, memorialHall_id=None):
        wreath = get_object_or_404(Wreath, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in wreath.sad.all():
                wreath.sad.remove(user)
                return Response({'status': 'sad removed'})
            else:
                wreath.sad.add(user)
                return Response({'status': 'sad added'})
        elif request.method == 'GET':
            total_sad_count = wreath.sad.count()
            return Response({'total_sad': total_sad_count})
    # 추모해요
    @action(detail=True, methods=['get', 'post'])
    def commemorate(self, request, pk=None, memorialHall_id=None):
        wreath = get_object_or_404(Wreath, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in wreath.commemorate.all():
                wreath.commemorate.remove(user)
                return Response({'status': 'commemorate removed'})
            else:
                wreath.commemorate.add(user)
                return Response({'status': 'commemorate added'})
        elif request.method == 'GET':
            total_commemorate_count = wreath.commemorate.count()
            return Response({'total_commemorate': total_commemorate_count})
    # 함께해요
    @action(detail=True, methods=['get', 'post'])
    def together(self, request, pk=None, memorialHall_id=None):
        wreath = get_object_or_404(Wreath, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in wreath.together.all():
                wreath.together.remove(user)
                return Response({'status': 'together removed'})
            else:
                wreath.together.add(user)
                return Response({'status': 'together added'})
        elif request.method == 'GET':
            total_together_count = wreath.together.count()
            return Response({'total_together': total_together_count})
    
#추모글
class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = MessagePagination
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        # 'list', 'retrieve', 'get' 액션에 대해 인증을 허용하지 않음
        if self.action in ['list', 'retrieve', 'get']:
            return [AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # 비속어 필터링 및 대체
        content = serializer.validated_data.get('content', '')  # 추모글 내용
        sanitized_content = self.replace_bad_words(content)
        #print(f'sanitized_content word: {sanitized_content}')  #테스트 로그
        serializer.save(nickname=self.request.user, content=sanitized_content)

    def replace_bad_words(self, content):
        bad_words = BadWord.objects.values_list('word', flat=True)
        # for bad_word in bad_words:
        #     content = content.replace(bad_word, '❤️')  # 비속어를 하트로 대체
        # return content
        # 비속어가 포함된 문장을 하트로 대체
        for bad_word in bad_words:
            # 비속어가 포함된 전체 문장을 찾습니다.
            if bad_word in content:
                # 전체 문장을 하트로 대체
                content = '❤️' * content.count(bad_word)  # 비속어가 몇 번 등장하는지에 따라 하트로 대체

        return content
    
    def get_queryset(self, **kwargs): 
        id = self.kwargs['memorialHall_id']
        return self.queryset.filter(hall=id).order_by('-created_at')
    #memorialHall로 MemorialHall과 foriegnkey연결시켰더니 인식 못하는 오류!!
    
    # 내가 작성한 추모글만 확인 #연결된 추모관 제목만 가져와서 불러오도록
    @action(detail=False, methods=['get'], url_path='my-messages')
    def my_messages(self, request):
        user = request.user
        my_messages = self.queryset.filter(nickname=user).order_by('-created_at')
        serializer = self.get_serializer(my_messages, many=True)
        return Response(serializer.data)
    
    #토닥토닥
    @action(detail=True, methods=['get', 'post'])
    def todak(self, request, pk=None, memorialHall_id=None):
        message = get_object_or_404(Message, pk=pk) 
        user = request.user
        
        if request.method == 'POST':
            if user in message.todak.all():
                message.todak.remove(user)
                return Response({'status': 'todak removed'})
            else:
                message.todak.add(user)
                return Response({'status': 'todak added'})
        elif request.method == 'GET':
            total_todak_count = message.todak.count()
            return Response({'total_todak': total_todak_count})
    #공감해요 
    @action(detail=True, methods=['get', 'post'])
    def sympathize(self, request, pk=None, memorialHall_id=None):
        message = get_object_or_404(Message, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in message.sympathize.all():
                message.sympathize.remove(user)
                return Response({'status': 'sympathize removed'})
            else:
                message.sympathize.add(user)
                return Response({'status': 'sympathize added'})
        elif request.method == 'GET':
            total_sympathize_count = message.sympathize.count()
            return Response({'total_sympathize': total_sympathize_count})
    #슬퍼요
    @action(detail=True, methods=['get', 'post'])
    def sad(self, request, pk=None, memorialHall_id=None):
        message = get_object_or_404(Message, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in message.sad.all():
                message.sad.remove(user)
                return Response({'status': 'sad removed'})
            else:
                message.sad.add(user)
                return Response({'status': 'sad added'})
        elif request.method == 'GET':
            total_sad_count = message.sad.count()
            return Response({'total_sad': total_sad_count})
    # 추모해요
    @action(detail=True, methods=['get', 'post'])
    def commemorate(self, request, pk=None, memorialHall_id=None):
        message = get_object_or_404(Message, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in message.commemorate.all():
                message.commemorate.remove(user)
                return Response({'status': 'commemorate removed'})
            else:
                message.commemorate.add(user)
                return Response({'status': 'commemorate added'})
        elif request.method == 'GET':
            total_commemorate_count = message.commemorate.count()
            return Response({'total_commemorate': total_commemorate_count})
    #함께해요
    @action(detail=True, methods=['get', 'post'])
    def together(self, request, pk=None, memorialHall_id=None):
        message = get_object_or_404(Message, pk=pk)
        user = request.user
        
        if request.method == 'POST':
            if user in message.together.all():
                message.together.remove(user)
                return Response({'status': 'together removed'})
            else:
                message.together.add(user)
                return Response({'status': 'together added'})
        elif request.method == 'GET':
            total_together_count = message.together.count()
            return Response({'total_together': total_together_count})
     
    #추모글 + 헌화의 한마디 목록조회   
    def list(self, request, memorialHall_id=None):
        hall = get_object_or_404(MemorialHall, pk=memorialHall_id)
        messages = hall.message_set.all().order_by('-created_at')
        wreaths = hall.wreath_set.all().order_by('-created_at')

        message_serializer = MessageSerializer(messages, many=True)
        wreath_serializer = WreathSerializer(wreaths, many=True)

        combined_data = message_serializer.data + wreath_serializer.data
        combined_data.sort(key=lambda x: x['created_at'], reverse=True)

        paginator = MessagePagination()
        page = paginator.paginate_queryset(combined_data, request)

        return paginator.get_paginated_response(page)
