"""
PDF 보고서 생성 모듈
"""

import os
import tempfile
from fpdf import FPDF
import streamlit as st
from typing import List, Dict

class PDFGenerator:
    """PDF 보고서 생성 클래스"""
    
    def __init__(self):
        self.font_path = "./fonts/NotoSansKR-Regular.ttf"
    
    def create_report(self, image_path: str, mask_path: str, overlay_path: str, 
                     analysis_result: str, chat_history: List[Dict]) -> str:
        """PDF 보고서 생성"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # 폰트 설정
            if os.path.exists(self.font_path):
                pdf.add_font("NotoSansKR", "", self.font_path, uni=True)
                pdf.set_font("NotoSansKR", size=12)
            else:
                pdf.set_font("Arial", size=12)
                st.warning("한국어 폰트 파일을 찾을 수 없어 기본 폰트를 사용합니다.")
            
            # 제목
            pdf.cell(200, 10, "배터리 결함 분석 보고서", ln=True, align="C")
            pdf.ln(10)
            
            # 이미지 삽입 (4개 컬럼: 원본, 마스크, 오버레이, 레이블)
            img_w = 40  # 이미지 너비 조정
            img_y = pdf.get_y()
            img_count = 0
            
            # 원본 이미지
            if os.path.exists(image_path):
                pdf.image(image_path, x=10, y=img_y, w=img_w)
                img_count += 1
            
            # AI 생성 마스크
            if os.path.exists(mask_path):
                pdf.image(mask_path, x=55, y=img_y, w=img_w)
                img_count += 1
            
            # 오버레이 이미지
            if overlay_path and os.path.exists(overlay_path):
                pdf.image(overlay_path, x=100, y=img_y, w=img_w)
                img_count += 1
            
            # 레이블 범례 생성 및 삽입
            legend_path = self._create_legend_image()
            if legend_path and os.path.exists(legend_path):
                pdf.image(legend_path, x=145, y=img_y, w=img_w)
                img_count += 1
            
            # 캡션 (이미지가 있는 경우만)
            if img_count > 0:
                if os.path.exists(image_path):
                    pdf.set_xy(10, img_y + img_w + 2)
                    pdf.cell(img_w, 8, "CT 원본 이미지", align="C")
                if os.path.exists(mask_path):
                    pdf.set_xy(55, img_y + img_w + 2)
                    pdf.cell(img_w, 8, "AI 생성 마스크", align="C")
                if overlay_path and os.path.exists(overlay_path):
                    pdf.set_xy(100, img_y + img_w + 2)
                    pdf.cell(img_w, 8, "결함 Overlay", align="C")
                if legend_path and os.path.exists(legend_path):
                    pdf.set_xy(145, img_y + img_w + 2)
                    pdf.cell(img_w, 8, "색상 레이블", align="C")
                pdf.ln(img_w + 12)
            
            # 분석 결과
            pdf.cell(0, 10, "분석 결과:", ln=True)
            pdf.multi_cell(0, 10, analysis_result)
            pdf.ln(5)
            
            # 질의응답
            if chat_history:
                pdf.cell(0, 10, "질의응답:", ln=True)
                for qa in chat_history:
                    pdf.multi_cell(0, 10, f"Q: {qa['question']}\nA: {qa['answer']}\n")
            
            # 임시 파일로 저장
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf.output(tmp_file.name)
            
            # 레이블 임시 파일 정리
            if legend_path and os.path.exists(legend_path):
                try:
                    os.remove(legend_path)
                except Exception:
                    pass
            
            return tmp_file.name
            
        except Exception as e:
            st.error(f"PDF 생성 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def _create_legend_image(self) -> str:
        """레이블 범례 이미지 생성"""
        try:
            from .ui_components import UIComponents
            from .config import COLORS_AND_LABELS
            
            # UI 컴포넌트를 사용하여 범례 이미지 생성
            legend_img = UIComponents.make_legend_img(COLORS_AND_LABELS)
            
            # temp 폴더에 임시 파일로 저장
            import cv2
            legend_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir="./temp")
            cv2.imwrite(legend_path.name, legend_img)
            
            return legend_path.name
        except Exception as e:
            print(f"레이블 범례 생성 오류: {e}")
            return None 