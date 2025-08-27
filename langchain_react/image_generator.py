"""
Image Generation Tool (복사본)
원본: mcp_react_client/image_generator.py
주의: 원본 로직을 변경하지 않고, 이 복사본만 사용합니다.
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import openai


class ImageGenerator:
    """이미지 생성 클래스 - OpenAI DALL-E를 사용"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        self.client = openai.OpenAI(api_key=self.openai_api_key)

        output_dir_env = os.getenv("MCP_OUTPUT_DIR") or os.getenv("PGPT_WORK_DIR")
        if output_dir_env:
            self.output_dir = Path(output_dir_env)
        else:
            project_root = Path(__file__).resolve().parents[1]
            self.output_dir = project_root / "outputs" / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> str:
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            raise Exception(f"이미지 생성 오류: {e}")
    
    def download_image(self, image_url: str, filename: str) -> str:
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            filepath = self.output_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # 무조건 512x512로 리사이즈
            try:
                img = Image.open(filepath)
                img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
                img_resized.save(filepath, quality=95)
                print(f"다운로드된 이미지를 512x512로 리사이즈했습니다.")
            except Exception as e:
                print(f"리사이즈 중 오류 발생: {e}")
            
            return str(filepath)
        except Exception as e:
            raise Exception(f"이미지 다운로드 오류: {e}")
    
    def generate_and_save_image(self, prompt: str, filename: Optional[str] = None, 
                               size: str = "512x512", quality: str = "standard") -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
        image_url = self.generate_image(prompt, size, quality)
        filepath = self.download_image(image_url, filename)
        
        # 무조건 512x512로 리사이즈
        try:
            img = Image.open(filepath)
            img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
            img_resized.save(filepath, quality=95)
            print(f"이미지를 512x512로 리사이즈했습니다.")
        except Exception as e:
            print(f"리사이즈 중 오류 발생: {e}")
        
        return filepath
    
    def create_comic_story(self, topic: str) -> Dict[str, Any]:
        prompt = f"""
주제: {topic}

위 주제로 재미있고 흥미로운 4컷 만화의 스토리를 만들어주세요.
각 컷마다 다음 정보를 JSON 형식으로 제공해주세요:

{{
    "comic_title": "만화 제목",
    "panels": [
        {{
            "panel_number": 1,
            "scene_description": "첫 번째 컷의 장면 묘사 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사나 설명",
            "mood": "분위기나 감정"
        }},
        {{
            "panel_number": 2,
            "scene_description": "두 번째 컷의 장면 묘사 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사나 설명",
            "mood": "분위기나 감정"
        }},
        {{
            "panel_number": 3,
            "scene_description": "세 번째 컷의 장면 묘사 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사나 설명",
            "mood": "분위기나 감정"
        }},
        {{
            "panel_number": 4,
            "scene_description": "네 번째 컷의 장면 묘사 (영어로, 이미지 생성용)",
            "dialogue": "등장인물의 대사나 설명",
            "mood": "분위기나 감정"
        }}
    ]
}}

주의사항:
- scene_description은 영어로 작성하고, DALL-E가 이해할 수 있도록 구체적이고 시각적으로 묘사
- 각 컷은 논리적으로 연결되어 하나의 완성된 스토리를 만들어야 함
- 대화나 설명은 한국어로 작성
- 만화답고 재미있는 요소를 포함
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 창의적인 만화 스토리 작가입니다. 주어진 주제로 재미있는 4컷 만화를 만들어주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            result = response.choices[0].message.content.strip()
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                result = result[json_start:json_end].strip()
            elif "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                result = result[json_start:json_end]
            story_data = json.loads(result)
            return story_data
        except json.JSONDecodeError as e:
            raise Exception(f"스토리 JSON 파싱 오류: {e}")
        except Exception as e:
            raise Exception(f"스토리 생성 오류: {e}")
    
    def create_comic_layout(self, story_data: Dict[str, Any], image_paths: List[str]) -> str:
        try:
            images = []
            for path in image_paths:
                img = Image.open(path)
                img = img.resize((512, 512), Image.Resampling.LANCZOS)
                images.append(img)
            comic_width = 1024 + 60
            comic_height = 1024 + 60
            comic_image = Image.new('RGB', (comic_width, comic_height), 'white')
            positions = [(30, 30), (542, 30), (30, 542), (542, 542)]
            for i, (img, pos) in enumerate(zip(images, positions)):
                comic_image.paste(img, pos)
            draw = ImageDraw.Draw(comic_image)
            try:
                title_font = ImageFont.load_default()
            except:
                title_font = ImageFont.load_default()
            title = story_data.get('comic_title', '4컷 만화')
            bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = bbox[2] - bbox[0]
            title_x = (comic_width - title_width) // 2
            draw.text((title_x, 5), title, fill='black', font=title_font)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comic_filename = f"comic_{timestamp}.png"
            comic_path = self.output_dir / comic_filename
            comic_image.save(comic_path)
            return str(comic_path)
        except Exception as e:
            raise Exception(f"만화 레이아웃 생성 오류: {e}")


def generate_single_image(prompt: str, filename: Optional[str] = None, 
                         size: str = "512x512", quality: str = "standard") -> str:
    generator = ImageGenerator()
    return generator.generate_and_save_image(prompt, filename, size, quality)


def generate_comic(topic: str) -> str:
    generator = ImageGenerator()
    story_data = generator.create_comic_story(topic)
    image_paths = []
    for panel in story_data['panels']:
        panel_num = panel['panel_number']
        scene_desc = panel['scene_description']
        prompt = f"4-panel comic style: {scene_desc}"
        image_url = generator.generate_image(prompt, "512x512")
        filename = f"panel_{panel_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image_path = generator.download_image(image_url, filename)
        image_paths.append(image_path)
    comic_path = generator.create_comic_layout(story_data, image_paths)
    return comic_path


def resize_existing_image(image_path: str, new_size: tuple = (512, 512)) -> str:
    """기존 이미지 파일을 리사이즈하는 함수"""
    try:
        img = Image.open(image_path)
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # 원본 파일명에 _resized 추가
        path_obj = Path(image_path)
        new_filename = f"{path_obj.stem}_resized{path_obj.suffix}"
        new_path = path_obj.parent / new_filename
        
        img_resized.save(new_path, quality=95)
        print(f"이미지를 {new_size[0]}x{new_size[1]}로 리사이즈하여 {new_path}에 저장했습니다.")
        return str(new_path)
    except Exception as e:
        raise Exception(f"이미지 리사이즈 오류: {e}")


