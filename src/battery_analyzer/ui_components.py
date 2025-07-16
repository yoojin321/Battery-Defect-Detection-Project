"""
UI 컴포넌트 관리 모듈
"""

import cv2
import numpy as np
from PIL import Image
import streamlit as st
from typing import Dict
from .config import COLORS_AND_LABELS

class UIComponents:
    """UI 컴포넌트 관리 클래스"""
    
    @staticmethod
    def make_legend_img(colors_and_labels: Dict, width: int = 240, height_per_item: int = 40) -> np.ndarray:
        """범례 이미지 생성"""
        legend_height = height_per_item * len(colors_and_labels) + 20
        legend_img = np.ones((legend_height, width, 3), dtype=np.uint8) * 255
        
        for i, (class_id, (color, label)) in enumerate(colors_and_labels.items()):
            y_pos = i * height_per_item + 30
            color_tuple = tuple(int(c) for c in color)
            cv2.rectangle(legend_img, (15, y_pos-15), (45, y_pos+15), color_tuple, -1)
            cv2.rectangle(legend_img, (15, y_pos-15), (45, y_pos+15), (0,0,0), 2)
            cv2.putText(legend_img, label, (55, y_pos+7), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,0,0), 1, cv2.LINE_AA)
        
        return legend_img
    
    @staticmethod
    def display_images(original_img: np.ndarray, colored_mask: np.ndarray, overlay: np.ndarray, legend_img: np.ndarray):
        """이미지들을 UI에 표시"""
        st.markdown("""
        <style>
        .stColumns {margin-bottom: 0px !important;}
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 0.6])
        
        with col1:
            st.image(Image.fromarray(original_img), caption="CT 원본 이미지", use_container_width=True)
        with col2:
            st.image(Image.fromarray(colored_mask), caption="AI 생성 마스크 (모든 클래스)", use_container_width=True)
        with col3:
            st.image(Image.fromarray(overlay), caption="선택된 결함 Overlay (컬러)", use_container_width=True)
        with col4:
            st.image(Image.fromarray(legend_img), caption="", use_container_width=True) 