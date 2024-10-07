import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from badwords.models import BadWord 

# 비속어 JSON 파일 경로 설정
BAD_WORDS_FILE_PATH = os.path.join(settings.BASE_DIR, 'badWords.json')

class Command(BaseCommand):
    help = 'Import bad words from JSON file into the database'

    def handle(self, *args, **kwargs):
        # JSON 파일 열기
        with open(BAD_WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # data가 리스트인 경우
        if isinstance(data, list) and len(data) > 0:
            # 첫 번째 요소에서 rows 가져오기
            rows = data[0].get("rows", [])
            for word in rows:
                # word[0]를 사용하여 실제 단어를 가져옵니다.
                #print(f'Processing word: {word[0]}') 테스트로그
                BadWord.objects.get_or_create(word=word[0])

        self.stdout.write(self.style.SUCCESS('Successfully imported bad words.'))