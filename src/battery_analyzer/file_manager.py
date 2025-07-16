"""
파일 관리 모듈
"""

import os
import tempfile
import uuid
from typing import Optional

class FileManager:
    """파일 관리 클래스"""
    
    def __init__(self):
        self.temp_dir = "./temp"
        self._ensure_temp_dir()
    
    def _ensure_temp_dir(self):
        """임시 디렉토리 생성"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            print(f"📁 임시 폴더 생성: {self.temp_dir}")
    
    def save_uploaded_image(self, uploaded_file) -> str:
        """업로드된 이미지 저장"""
        try:
            # 임시 디렉토리에 고유한 파일명으로 저장
            file_extension = uploaded_file.name.split('.')[-1]
            unique_filename = f"uploaded_{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(self.temp_dir, unique_filename)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            print(f"💾 업로드 이미지 저장: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ 이미지 저장 실패: {e}")
            return None
    
    def create_temp_image_path(self, prefix: str = "temp", extension: str = "png") -> str:
        """임시 이미지 파일 경로 생성"""
        unique_filename = f"{prefix}_{uuid.uuid4()}.{extension}"
        return os.path.join(self.temp_dir, unique_filename)
    
    def cleanup_temp_files(self, file_paths: list):
        """임시 파일들 정리"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🧹 임시 파일 삭제: {file_path}")
            except Exception as e:
                print(f"⚠️ 파일 삭제 실패 {file_path}: {e}")
    
    def cleanup_all_temp_files(self):
        """모든 임시 파일 정리"""
        try:
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception:
                        pass
                print(f"🧹 모든 임시 파일 정리 완료: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ 임시 파일 정리 실패: {e}")
    
    def get_temp_dir(self) -> str:
        """임시 디렉토리 경로 반환"""
        return self.temp_dir 