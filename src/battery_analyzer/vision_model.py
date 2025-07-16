"""
비전 모델 관리 모듈
"""

import cv2
import numpy as np
import torch
import segmentation_models_pytorch as smp
from typing import Tuple
from .config import MODEL_CONFIG

class VisionModel:
    """비전 모델 관리 클래스"""
    
    def __init__(self, model_path: str, num_classes: int = 5, backbone: str = 'efficientnet-b0'):
        self.model_path = model_path
        self.num_classes = num_classes
        self.backbone = backbone
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def load_model(self):
        """모델 로드"""
        try:
            self.model = smp.DeepLabV3Plus(
                encoder_name=self.backbone,
                encoder_weights=None,
                in_channels=3,
                classes=self.num_classes,
                activation=None,
            )
            self.model.load_state_dict(torch.load(self.model_path, map_location='cpu'))
            self.model.to(self.device)
            self.model.eval()
            return True
        except Exception as e:
            import streamlit as st
            st.error(f"비전 모델 로딩 실패: {str(e)}")
            return False
    
    def predict(self, image_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """이미지 예측"""
        if self.model is None:
            raise ValueError("모델이 로드되지 않았습니다.")
        
        # 이미지 로드 및 전처리
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 리사이즈
        image_resized = cv2.resize(image, MODEL_CONFIG["input_size"])
        
        # 정규화
        image_normalized = image_resized.astype(np.float32) / 255.0
        image_normalized = (image_normalized - 0.5) / 0.5
        
        # 텐서 변환
        image_tensor = torch.from_numpy(image_normalized).permute(2, 0, 1).unsqueeze(0)
        image_tensor = image_tensor.to(self.device)
        
        # 예측
        with torch.no_grad():
            prediction = self.model(image_tensor)
            prediction = torch.softmax(prediction, dim=1)
            prediction = torch.argmax(prediction, dim=1)
        
        # numpy 변환
        mask = prediction.cpu().numpy().squeeze()
        
        return image_resized, mask 