#!/usr/bin/env python3
"""
4컷 카툰 생성기 데모 스크립트
미리 정의된 주제들로 빠르게 테스트할 수 있습니다.
"""

from comic_generator import ComicGenerator
import os

def main():
    """데모 실행"""
    print("🎨 4컷 카툰 생성기 데모")
    print("=" * 40)
    
    # API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("1. env.example을 .env로 복사하세요")
        print("2. .env 파일에 OpenAI API 키를 입력하세요")
        return
    
    # 미리 정의된 주제들
    demo_topics = [
        "고양이와 로봇의 우정",
        "커피를 찾는 좀비",
        "시간여행하는 학생",
        "요리하는 외계인",
        "춤추는 AI",
    ]
    
    print("\n📝 사용 가능한 데모 주제들:")
    for i, topic in enumerate(demo_topics, 1):
        print(f"{i}. {topic}")
    
    print("0. 직접 입력")
    print()
    
    try:
        choice = input("주제를 선택하세요 (1-5, 0): ").strip()
        
        if choice == "0":
            topic = input("만화 주제를 입력하세요: ").strip()
        elif choice.isdigit() and 1 <= int(choice) <= len(demo_topics):
            topic = demo_topics[int(choice) - 1]
        else:
            print("❌ 잘못된 선택입니다.")
            return
        
        if not topic:
            print("❌ 주제를 입력해주세요.")
            return
        
        print(f"\n🚀 '{topic}' 주제로 4컷 만화를 생성합니다...")
        print("⏳ 이 과정은 몇 분이 걸릴 수 있습니다...")
        
        # 생성기 초기화 및 실행
        generator = ComicGenerator()
        result = generator.generate_comic(topic)
        
        print(f"\n✅ 생성 완료!")
        print(f"📁 4컷 만화: {result['comic_image']}")
        print(f"📄 스토리: {result['story_json']}")
        print(f"🖼️ 개별 패널: {len(result['individual_panels'])}개")
        
        # 운영체제별 파일 열기 명령
        import platform
        import subprocess
        
        if platform.system() == "Darwin":  # macOS
            print(f"\n🔍 결과를 보려면: open {result['comic_image']}")
        elif platform.system() == "Windows":
            print(f"\n🔍 결과를 보려면: start {result['comic_image']}")
        else:  # Linux
            print(f"\n🔍 결과를 보려면: xdg-open {result['comic_image']}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("💡 다음을 확인해보세요:")
        print("   - OpenAI API 키가 올바른지")
        print("   - 인터넷 연결이 정상인지")
        print("   - API 사용량 한도를 초과하지 않았는지")

if __name__ == "__main__":
    main()

