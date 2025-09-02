"""
Image Generation Tool (Slim)
원본은 유지, 이 복사본만 사용하세요.
기능: GPT Image 생성 → Supabase Storage 저장 → 공개 URL 반환
"""

import os
import base64
from io import BytesIO
from datetime import datetime
from typing import Optional

import openai
from PIL import Image
from supabase import create_client


class ImageGenerator:
    """GPT Image 생성 후 Supabase Storage에 저장"""

    def __init__(self, api_key: Optional[str] = None):
        # OpenAI
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        self.client = openai.OpenAI(api_key=self.openai_api_key)

        # Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not (supabase_url and supabase_key):
            raise ValueError("SUPABASE_URL 또는 SUPABASE_KEY가 없습니다.")
        self._supabase = create_client(supabase_url, supabase_key)

        # 기본 버킷명
        self.bucket = os.getenv("SUPABASE_IMAGE_BUCKET", "task-image")

    def _resize_png(self, png_bytes: bytes, size=(512, 512)) -> bytes:
        """PNG 바이트를 지정 크기로 리사이즈(옵션)"""
        try:
            img = Image.open(BytesIO(png_bytes))
            img = img.convert("RGBA")  # 안전 변환
            img_resized = img.resize(size, Image.Resampling.LANCZOS)
            buf = BytesIO()
            img_resized.save(buf, format="PNG", optimize=True)
            return buf.getvalue()
        except Exception:
            # 리사이즈 실패 시 원본 반환
            return png_bytes

    def generate_and_upload(
        self,
        prompt: str,
        filename: Optional[str] = None,
        *,
        size: str = "1024x1024",   # "1024x1024" | "1536x1024" | "1024x1536" | "auto"
        quality: str = "medium",   # "low" | "medium" | "high" | "auto"
        resize_to_512: bool = True,
        return_markdown: bool = False,
    ) -> str:
        """
        이미지를 생성해 Supabase에 저장하고 공개 URL(또는 마크다운 링크)을 반환.
        """
        # 파일명 기본값
        if not filename:
            filename = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        # 1) GPT Image 생성 (b64_json)
        resp = self.client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        b64 = resp.data[0].b64_json
        png_bytes = base64.b64decode(b64)

        # 2) (옵션) 512x512 리사이즈
        if resize_to_512:
            png_bytes = self._resize_png(png_bytes, (512, 512))

        # 3) Supabase Storage 업로드
        #    동일 이름 존재 시 실패하므로, 덮어쓰고 싶다면 remove 후 upload 하거나 upsert 사용
        self._supabase.storage.from_(self.bucket).upload(filename, png_bytes)

        # 4) 공개 URL 반환
        public_url = self._supabase.storage.from_(self.bucket).get_public_url(filename)

        if return_markdown:
            supabase_url_env = os.getenv("SUPABASE_URL")
            if supabase_url_env:
                return f"![{filename}]({supabase_url_env}/storage/v1/object/public/{self.bucket}/{filename})"
            return f"![{filename}]({public_url})"

        return public_url