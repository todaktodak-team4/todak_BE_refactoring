# import json
# import os
# import re
# from django.conf import settings
# from django.core.cache import cache

# #비속어 json파일 경로 설정
# BAD_WORDS_FILE_PATH = os.path.join(settings.BASE_DIR,'badWords.json')
# # JSON 파일에서 비속어 리스트 불러오기

# def load_bad_words():

#     """
#     JSON 파일에서 비속어 리스트를 불러오고 캐시에 저장
#     """
#     bad_words = cache.get('bad_words_set')
    
#     if not bad_words:
#             with open(BAD_WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
#             # "rows" 키에서 각 비속어를 추출
#             bad_words = set(word[0] for word in data.get("rows", []))
#             cache.set('bad_words_set', bad_words, timeout=None)  # 캐시에 무기한 저장
#     return bad_words

# # 비속어 필터링 함수
# def get_bad_words_pattern():
#     """
#     비속어 리스트를 기반으로 정규 표현식 패턴을 생성합니다.
#     """
#     bad_words = load_bad_words()
#     # 단어 경계를 고려하여 전체 단어만 매칭
#     pattern = re.compile(r'\b(?:' + "|".join(re.escape(word) for word in bad_words) + r')\b', re.IGNORECASE)
#     return pattern

# # 패턴을 미리 컴파일하여 성능 최적화
# BAD_WORDS_PATTERN = get_bad_words_pattern()

# def filter_bad_words(text):
#     """
#     입력된 텍스트에서 비속어를 찾아 하트 이모지로 대체합니다.
#     """
#     return BAD_WORDS_PATTERN.sub('❤️', text)