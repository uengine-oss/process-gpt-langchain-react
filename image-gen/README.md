# 4컷 카툰 생성기

랭체인(LangChain)과 OpenAI API를 이용하여 주제에 대한 4컷 만화를 자동으로 생성하는 Python 프로그램입니다.

## 기능

- 📝 **스토리 생성**: GPT-4를 이용하여 주제에 맞는 재미있는 4컷 만화 스토리 생성
- 🎨 **이미지 생성**: DALL-E 3를 이용하여 각 컷에 해당하는 이미지 생성
- 🖼️ **레이아웃 합성**: 4개의 이미지를 하나의 완성된 4컷 만화로 조합
- 💾 **결과 저장**: 생성된 만화와 스토리를 파일로 저장

## 설치

1. **저장소 클론 및 이동**
```bash
cd image-gen
```

2. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```

3. **환경변수 설정**
```bash
# 환경변수 파일 생성
cp env.example .env

# .env 파일을 편집하여 OpenAI API 키 입력
# OPENAI_API_KEY=your_actual_api_key_here
```

## OpenAI API 키 발급

1. [OpenAI Platform](https://platform.openai.com/api-keys)에 접속
2. 계정 생성 또는 로그인
3. API Keys 섹션에서 새 API 키 생성
4. 생성된 키를 `.env` 파일에 입력

## 사용법

### 기본 사용법

```bash
python comic_generator.py
```

프로그램을 실행하면 만화 주제를 입력하라는 프롬프트가 나타납니다.

### 예시

```
4컷 카툰 생성기
==============================
만화 주제를 입력하세요: 인공지능과 고양이의 하루
```

## 출력 파일

프로그램 실행 후 `output/` 디렉토리에 다음 파일들이 생성됩니다:

- `4cut_comic_YYYYMMDD_HHMMSS.png`: 완성된 4컷 만화
- `story_YYYYMMDD_HHMMSS.json`: 생성된 스토리 데이터 (JSON 형식)
- `panel_1_YYYYMMDD_HHMMSS.png`: 개별 컷 이미지들 (1-4)

## 생성 과정

1. **스토리 생성**: 입력받은 주제로 GPT-4가 4컷 만화의 스토리를 구성
2. **이미지 생성**: 각 컷의 장면 설명을 바탕으로 DALL-E 3가 이미지 생성
3. **이미지 다운로드**: 생성된 이미지들을 로컬에 저장
4. **레이아웃 합성**: 4개의 이미지를 2x2 배치로 조합하여 완성된 만화 생성

## 프로젝트 구조

```
image-gen/
├── comic_generator.py      # 메인 스크립트
├── requirements.txt        # 필요한 패키지 목록
├── env.example            # 환경변수 템플릿
├── README.md              # 이 파일
└── output/                # 생성된 파일들이 저장되는 디렉토리
    ├── 4cut_comic_*.png   # 완성된 4컷 만화
    ├── story_*.json       # 스토리 데이터
    └── panel_*.png        # 개별 컷 이미지들
```

## 주요 클래스 및 메서드

### `ComicGenerator` 클래스

- `generate_story(topic)`: 주제를 바탕으로 4컷 만화 스토리 생성
- `generate_image(scene_description, panel_number)`: 장면 설명을 바탕으로 이미지 생성
- `create_comic_layout(story_data, image_paths)`: 4컷 만화 레이아웃 생성
- `generate_comic(topic)`: 전체 생성 프로세스 실행

## 사용 비용

이 프로그램은 OpenAI의 유료 API를 사용합니다:

- **GPT-4**: 스토리 생성 (텍스트 생성)
- **DALL-E 3**: 이미지 생성 (4개 이미지)

자세한 요금은 [OpenAI Pricing](https://openai.com/pricing)을 참조하세요.

## 주의사항

1. **API 키 보안**: `.env` 파일을 절대 공개 저장소에 커밋하지 마세요
2. **사용 제한**: OpenAI API의 사용 정책을 준수하세요
3. **비용 관리**: API 사용량을 모니터링하고 예산을 설정하세요
4. **저작권**: 생성된 이미지의 사용에 대한 OpenAI 정책을 확인하세요

## 문제 해결

### 자주 발생하는 오류

1. **API 키 오류**
   ```
   ValueError: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.
   ```
   - `.env` 파일에 올바른 API 키가 입력되었는지 확인

2. **패키지 누락 오류**
   ```
   ModuleNotFoundError: No module named 'langchain'
   ```
   - `pip install -r requirements.txt` 실행

3. **이미지 생성 오류**
   - 네트워크 연결 확인
   - OpenAI API 사용량 한도 확인
   - 장면 설명이 OpenAI 정책에 위배되지 않는지 확인

## 라이선스

MIT License

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

**참고**: 이 프로그램은 교육 및 실험 목적으로 제작되었습니다. 상업적 사용 시 OpenAI의 사용 정책을 확인하시기 바랍니다.

