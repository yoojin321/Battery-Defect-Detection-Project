"""
이미지 처리 및 마스크 생성 모듈
"""

import cv2
import numpy as np
from typing import List, Tuple
from .config import COLORS

class ImageProcessor:
    """이미지 처리 및 마스크 생성 클래스"""
    
    @staticmethod
    def create_defect_mask(mask: np.ndarray, defect_class: int = 2) -> np.ndarray:
        """결함 클래스만 추출하여 마스크 생성"""
        defect_mask = (mask == defect_class).astype(np.uint8) * 255
        return defect_mask
    
    @staticmethod
    def create_colored_mask(mask: np.ndarray) -> np.ndarray:
        """모든 클래스를 색상으로 구분하여 마스크 생성"""
        colored_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
        for class_id, color in COLORS.items():
            colored_mask[mask == class_id] = color
        return colored_mask
    
    @staticmethod
    def get_detected_defects(mask: np.ndarray) -> List[int]:
        """탐지된 결함 클래스들을 반환"""
        unique_classes = np.unique(mask)
        # 배터리(클래스 1)는 결함이 아니므로 제외, 실제 결함만 반환
        defect_classes = [cls for cls in unique_classes if cls > 1]
        return defect_classes
    
    @staticmethod
    def create_overlay(image: np.ndarray, colored_mask: np.ndarray, alpha: float = 0.4) -> np.ndarray:
        """오버레이 이미지 생성"""
        return cv2.addWeighted(image, 1 - alpha, colored_mask, alpha, 0)
    
    @staticmethod
    def resize_mask_safely(mask: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
        """안전한 마스크 리사이즈"""
        try:
            if mask is not None and mask.size > 0 and len(mask.shape) == 2:
                return cv2.resize(mask, target_shape)
            else:
                return np.zeros(target_shape, dtype=np.uint8)
        except Exception as e:
            print(f"마스크 리사이즈 오류: {e}")
            return np.zeros(target_shape, dtype=np.uint8) 