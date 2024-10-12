# from django.test import TestCase

# # Create your tests here.
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from rest_framework_simplejwt.tokens import AccessToken
# from rememberTree.models import UserEmotion, Question

# class ChatCounselingAPITest(APITestCase):

#     def setUp(self):
#         # 테스트 유저 생성

#         # 테스트를 위한 질문 생성
#         for question_type in ['DENIAL', 'ANGER', 'BARGAINING', 'DEPRESSION', 'ACCEPTANCE']:
#             Question.objects.create(question_text=f"{question_type} question?", question_type=question_type)

#         self.url = reverse('chat-counseling')  # 이 URL 패턴과 일치하는지 확인

#     def test_get_daily_question_no_emotion(self):
#         """감정 데이터가 없을 때 하루 질문을 가져오는 테스트."""
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('question', response.data)

#     def test_post_message_and_receive_follow_up(self):
#         """사용자 메시지를 보내고 후속 질문을 받는 테스트."""
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        
#         # API에 메시지 전송 시뮬레이션
#         user_message = "I'm feeling down."
#         response = self.client.post(self.url, {'message': user_message}, format='json')
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('message', response.data)

#         # 감정이 저장되었는지 확인
#         self.assertTrue(UserEmotion.objects.filter(user=self.user).exists())
#         last_emotion = UserEmotion.objects.last()
#         self.assertIsNotNone(last_emotion)
        
#         # 다시 하루 질문을 가져오는 시뮬레이션
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('question', response.data)

#     def test_post_empty_message(self):
#         """빈 메시지를 게시하는 테스트."""
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
#         response = self.client.post(self.url, {'message': ''}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_daily_question_with_emotion(self):
#         """감정 데이터가 있을 때 하루 질문을 가져오는 테스트."""
#         # 사용자에 대한 감정 추가
#         UserEmotion.objects.create(user=self.user, emotion_type='DENIAL')

#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('question', response.data)
