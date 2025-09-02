#!/usr/bin/env python3
"""
이미지 생성 기능 테스트 스크립트 (Slim 버전용)
- GPT Image(gpt-image-1)로 생성 → Supabase Storage 업로드 → 공개 URL 출력
"""

import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# langchain_react 모듈 import 경로 설정
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain_react'))
from image_generator import ImageGenerator  # Slim 버전의 클래스 사용

def test_image_generation():
    """이미지 생성 기능 테스트"""
    print("🎨 이미지 생성 테스트 시작...")

    # 환경 변수 확인
    print("\n📋 환경 변수 확인:")
    print(f"OPENAI_API_KEY: {'✅ 설정됨' if os.getenv('OPENAI_API_KEY') else '❌ 설정되지 않음'}")
    print(f"SUPABASE_URL:   {'✅ 설정됨' if os.getenv('SUPABASE_URL') else '❌ 설정되지 않음'}")
    print(f"SUPABASE_KEY:   {'✅ 설정됨' if os.getenv('SUPABASE_KEY') else '❌ 설정되지 않음'}")

    if not (os.getenv('OPENAI_API_KEY') and os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY')):
        print("\n❌ 필수 환경변수가 누락되었습니다. .env를 확인해주세요.")
        return

    # 테스트용 프롬프트 (동일 유지)
    test_prompt = "신입사원이 열심히 일하는 모습습"
    print(f"\n🖼️ 테스트 프롬프트: {test_prompt}")

    try:
        # 생성 → 업로드
        print("\n🚀 이미지 생성 및 업로드 중...")
        gen = ImageGenerator()
        public_url = gen.generate_and_upload(
            prompt=test_prompt,
            filename="test_1_gpt_image.png",
            size="1024x1024",
            quality="medium",      # 'low' | 'medium' | 'high' | 'auto'
            resize_to_512=True,    # 필요 없으면 False
            return_markdown=False  # True로 하면 마크다운 링크 반환
        )

        print("\n✅ 완료!")
        print(f"🔗 Supabase 공개 URL: {public_url}")

        # 마크다운 표시도 보고 싶다면:
        supabase_url_env = os.getenv("SUPABASE_URL")
        markdown = f"![test_1_gpt_image.png]({supabase_url_env}/storage/v1/object/public/images/test_1_gpt_image.png)" if supabase_url_env else f"![test_1_gpt_image.png]({public_url})"
        print(f"\n📝 마크다운:\n{markdown}")

    except Exception as e:
        print(f"\n❌ 이미지 생성 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_generation()
