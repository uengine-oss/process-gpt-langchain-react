#!/usr/bin/env python3
"""
4컷 카툰 생성기
랭체인과 OpenAI API를 이용하여 주제에 대한 4컷 만화를 생성합니다.
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import io

# 환경변수 로드
load_dotenv()

class ComicGenerator:
    """4컷 만화 생성기 클래스"""
    
    def __init__(self):
        """초기화"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            
        # OpenAI 클라이언트 초기화
        self.llm = OpenAI(
            model="gpt-3.5-turbo-instruct",
            temperature=0.7,
            openai_api_key=self.openai_api_key
        )
        
        # 출력 디렉토리 생성
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def create_story_prompt(self) -> PromptTemplate:
        """스토리 생성을 위한 프롬프트 템플릿 생성"""
        template = """
주제: {topic}

위 주제로 재미있고 흥미로운 4컷 만화의 스토리를 만들어주세요.
각 컷마다 다음 정보를 JSON 형식으로 제공해주세요:

{{
    "comic_title": "만화 제목",
    "panels": [
        {{
            "panel_number": 1,
            "scene_description": "첫 번째 컷의 장면 설명 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사 (한글)",
            "narration": "나레이션 (한글, 선택사항)"
        }},
        {{
            "panel_number": 2,
            "scene_description": "두 번째 컷의 장면 설명 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사 (한글)",
            "narration": "나레이션 (한글, 선택사항)"
        }},
        {{
            "panel_number": 3,
            "scene_description": "세 번째 컷의 장면 설명 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사 (한글)",
            "narration": "나레이션 (한글, 선택사항)"
        }},
        {{
            "panel_number": 4,
            "scene_description": "네 번째 컷의 장면 설명 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사 (한글)",
            "narration": "나레이션 (한글, 선택사항)"
        }}
    ]
}}

scene_description은 DALL-E 3가 이해할 수 있도록 영어로 구체적이고 시각적으로 작성해주세요.
만화 스타일, 캐릭터의 표정과 동작, 배경 등을 포함해주세요.
예: "cartoon style illustration of a confused person looking at their smartphone with question marks around their head, indoor office background"

JSON 형식만 응답해주세요.
        """
        
        return PromptTemplate(
            input_variables=["topic"],
            template=template
        )
    
    def generate_story(self, topic: str) -> Dict[str, Any]:
        """주제를 바탕으로 4컷 만화 스토리 생성"""
        print(f"주제 '{topic}'에 대한 4컷 만화 스토리를 생성 중...")
        
        prompt = self.create_story_prompt()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(topic=topic)
            # JSON 파싱
            story_data = json.loads(result.strip())
            print(f"스토리 생성 완료: {story_data['comic_title']}")
            return story_data
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"응답 내용: {result}")
            raise
    
    def generate_image(self, scene_description: str, panel_number: int) -> str:
        """DALL-E 3를 이용하여 이미지 생성"""
        print(f"컷 {panel_number} 이미지 생성 중...")
        
        # OpenAI API 직접 호출 (langchain의 OpenAI 이미지 생성이 업데이트되지 않은 경우를 대비)
        import openai
        
        client = openai.OpenAI(api_key=self.openai_api_key)
        
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"4-panel comic style: {scene_description}",
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            print(f"컷 {panel_number} 이미지 생성 완료")
            return image_url
            
        except Exception as e:
            print(f"이미지 생성 오류 (컷 {panel_number}): {e}")
            raise
    
    def download_image(self, image_url: str, filename: str) -> str:
        """이미지를 다운로드하고 파일로 저장"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            filepath = self.output_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"이미지 저장: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"이미지 다운로드 오류: {e}")
            raise
    
    def create_comic_layout(self, story_data: Dict[str, Any], image_paths: List[str]) -> str:
        """4개의 이미지를 하나의 4컷 만화로 합성"""
        print("4컷 만화 레이아웃 생성 중...")
        
        # 각 패널 크기
        panel_width, panel_height = 512, 512
        margin = 20
        
        # 전체 캔버스 크기 (2x2 배치)
        canvas_width = panel_width * 2 + margin * 3
        canvas_height = panel_height * 2 + margin * 4 + 100  # 제목 공간 추가
        
        # 새 이미지 생성 (흰색 배경)
        comic_image = Image.new('RGB', (canvas_width, canvas_height), 'white')
        draw = ImageDraw.Draw(comic_image)
        
        # 제목 그리기
        title = story_data['comic_title']
        try:
            # 시스템 폰트 사용 시도
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            # 기본 폰트 사용
            font = ImageFont.load_default()
        
        # 제목 중앙 정렬
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (canvas_width - title_width) // 2
        draw.text((title_x, margin), title, fill='black', font=font)
        
        # 패널 위치 계산 (2x2 배치)
        positions = [
            (margin, margin + 50),  # 좌상
            (margin * 2 + panel_width, margin + 50),  # 우상
            (margin, margin * 2 + panel_height + 50),  # 좌하
            (margin * 2 + panel_width, margin * 2 + panel_height + 50)  # 우하
        ]
        
        # 각 패널 이미지 배치
        for i, (image_path, position) in enumerate(zip(image_paths, positions)):
            try:
                panel_img = Image.open(image_path)
                panel_img = panel_img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
                comic_image.paste(panel_img, position)
                
                # 패널 번호 그리기
                draw.text((position[0] + 10, position[1] + 10), 
                         str(i + 1), fill='white', font=font)
                
            except Exception as e:
                print(f"패널 {i+1} 처리 오류: {e}")
        
        # 최종 이미지 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"4cut_comic_{timestamp}.png"
        output_path = self.output_dir / output_filename
        
        comic_image.save(output_path)
        print(f"4컷 만화 완성: {output_path}")
        
        return str(output_path)
    
    def save_story_json(self, story_data: Dict[str, Any]) -> str:
        """스토리 데이터를 JSON 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"story_{timestamp}.json"
        json_path = self.output_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
        
        print(f"스토리 저장: {json_path}")
        return str(json_path)
    
    def generate_comic(self, topic: str) -> Dict[str, str]:
        """전체 4컷 만화 생성 프로세스"""
        print(f"\n=== 4컷 만화 생성 시작 ===")
        print(f"주제: {topic}")
        print("=" * 50)
        
        try:
            # 1. 스토리 생성
            story_data = self.generate_story(topic)
            
            # 2. 스토리 JSON 저장
            story_json_path = self.save_story_json(story_data)
            
            # 3. 각 컷의 이미지 생성 및 다운로드
            image_paths = []
            for panel in story_data['panels']:
                panel_num = panel['panel_number']
                scene_desc = panel['scene_description']
                
                # 이미지 생성
                image_url = self.generate_image(scene_desc, panel_num)
                
                # 이미지 다운로드
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"panel_{panel_num}_{timestamp}.png"
                image_path = self.download_image(image_url, filename)
                image_paths.append(image_path)
            
            # 4. 4컷 만화 레이아웃 생성
            comic_path = self.create_comic_layout(story_data, image_paths)
            
            print("\n=== 생성 완료 ===")
            print(f"제목: {story_data['comic_title']}")
            
            # 각 컷의 내용 출력
            for panel in story_data['panels']:
                print(f"\n컷 {panel['panel_number']}:")
                print(f"  장면: {panel['scene_description']}")
                print(f"  대사: {panel['dialogue']}")
                if panel.get('narration'):
                    print(f"  나레이션: {panel['narration']}")
            
            return {
                'comic_image': comic_path,
                'story_json': story_json_path,
                'individual_panels': image_paths
            }
            
        except Exception as e:
            print(f"만화 생성 오류: {e}")
            raise

def main():
    """메인 함수"""
    print("4컷 카툰 생성기")
    print("=" * 30)
    
    # 사용자 입력
    topic = input("만화 주제를 입력하세요: ").strip()
    
    if not topic:
        print("주제를 입력해주세요.")
        return
    
    try:
        # 생성기 초기화
        generator = ComicGenerator()
        
        # 만화 생성
        result = generator.generate_comic(topic)
        
        print(f"\n생성된 파일:")
        print(f"- 4컷 만화: {result['comic_image']}")
        print(f"- 스토리 JSON: {result['story_json']}")
        print(f"- 개별 패널: {len(result['individual_panels'])}개")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
