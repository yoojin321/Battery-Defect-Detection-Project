"""
배터리 CT 결함 분석 메인 애플리케이션
"""

import streamlit as st
import cv2
import numpy as np
import uuid
import time
import os
from typing import Optional

# 모듈 import
from .system_config import SystemConfig
from .vision_model import VisionModel
from .image_processor import ImageProcessor
from .ui_components import UIComponents
from .file_manager import FileManager
from .ai_analyzer import AIAnalyzer
from .pdf_generator import PDFGenerator
from .config import MODEL_CONFIG, DEFECT_CLASSES, COLORS_AND_LABELS

class BatteryDefectAnalyzer:
    """배터리 결함 분석 메인 애플리케이션"""
    
    def __init__(self):
        self.system_config = SystemConfig()
        self.file_manager = FileManager()
        self.ai_analyzer = AIAnalyzer()
        self.pdf_generator = PDFGenerator()
        self.vision_model = None
        
        # 세션 상태 초기화
        self._init_session_state()
    
    def _init_session_state(self):
        """세션 상태 초기화"""
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = []
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "show_pdf" not in st.session_state:
            st.session_state.show_pdf = False
    
    def _cleanup_previous_files(self):
        """이전 임시 파일 정리"""
        if "uploaded_files" in st.session_state:
            self.file_manager.cleanup_temp_files(st.session_state.uploaded_files)
            st.session_state.uploaded_files = []
    
    def cleanup(self):
        """애플리케이션 종료 시 정리"""
        print("🧹 애플리케이션 종료 - 임시 파일 정리 중...")
        self._cleanup_previous_files()
        self.file_manager.cleanup_all_temp_files()
        print("✅ 정리 완료")
    
    def _load_vision_model(self):
        """비전 모델 로드"""
        if "vision_model" not in st.session_state:
            with st.spinner("비전 모델을 로딩 중입니다..."):
                self.vision_model = VisionModel(MODEL_CONFIG["path"])
                if self.vision_model.load_model():
                    st.session_state.vision_model = self.vision_model
                    st.session_state.device = self.vision_model.device
                else:
                    st.session_state.vision_model = None
        else:
            self.vision_model = st.session_state.vision_model
    
    def _process_uploaded_image(self, uploaded_file):
        """업로드된 이미지 처리"""
        image_path = self.file_manager.save_uploaded_image(uploaded_file)
        
        if self.vision_model is not None:
            with st.spinner("AI가 결함 영역을 자동으로 탐지하고 있습니다..."):
                try:
                    image_resized, mask = self.vision_model.predict(image_path)
                    
                    # 탐지된 결함 확인
                    detected_defects = ImageProcessor.get_detected_defects(mask)
                    st.session_state.detected_defects = detected_defects
                    st.session_state.full_mask = mask
                    
                    # 컬러 마스크 생성
                    colored_mask = ImageProcessor.create_colored_mask(mask)
                    st.session_state.colored_mask = colored_mask
                    
                    # 기본 결함 선택 (스웰링 우선)
                    if 2 in detected_defects:
                        selected_defect = 2
                    elif detected_defects:
                        selected_defect = detected_defects[0]
                    else:
                        selected_defect = 2
                    
                    st.session_state.selected_defect = selected_defect
                    
                    # 선택된 결함 마스크 생성
                    defect_mask = ImageProcessor.create_defect_mask(mask, selected_defect)
                    st.session_state.generated_mask = defect_mask
                    st.session_state.image_resized = image_resized
                    
                except Exception as e:
                    st.error(f"결함 탐지 실패: {str(e)}")
                    st.session_state.generated_mask = None
        
        return image_path
    
    def _display_results(self, image_path: str) -> Optional[str]:
        """결과 표시"""
        if "generated_mask" in st.session_state and st.session_state.generated_mask is not None:
            # 원본 이미지 로드
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # 컬러 마스크 리사이즈 (단순화)
            try:
                if "colored_mask" in st.session_state and st.session_state.colored_mask is not None:
                    colored_mask_resized = cv2.resize(st.session_state.colored_mask, (img.shape[1], img.shape[0]))
                else:
                    colored_mask_resized = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
            except Exception as e:
                print(f"컬러 마스크 리사이즈 오류: {e}")
                colored_mask_resized = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
            
            # 오버레이 생성
            overlay = ImageProcessor.create_overlay(img_display, colored_mask_resized)
            
            # 마스크 이미지 저장 (컬러 마스크를 직접 사용)
            mask_path = self.file_manager.create_temp_image_path("generated_mask", "png")
            cv2.imwrite(mask_path, colored_mask_resized)
            if "uploaded_files" not in st.session_state:
                st.session_state.uploaded_files = []
            st.session_state.uploaded_files.append(mask_path)
            
            # 이미지 표시
            legend_img = UIComponents.make_legend_img(COLORS_AND_LABELS)
            UIComponents.display_images(img_display, colored_mask_resized, overlay, legend_img)
            
            # 탐지된 결함 메시지
            if "detected_defects" in st.session_state and st.session_state.detected_defects:
                detected_names = [DEFECT_CLASSES.get(d, f"Class {d}") for d in st.session_state.detected_defects]
                st.success(f"감지된 결함: {', '.join(detected_names)}")
            else:
                st.warning("결함이 감지되지 않았습니다.")
            
            return mask_path
        return None
    
    def _handle_ai_analysis(self, image_path: str, mask_path: str):
        """AI 분석 처리"""
        if st.button("AI 분석 시작") or "llava_output" in st.session_state:
            st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
            
            # 결함 정보 수집
            detected_defects = st.session_state.detected_defects if "detected_defects" in st.session_state else []
            
            if detected_defects:
                defect_labels = [DEFECT_CLASSES.get(d, f"Class {d}") for d in detected_defects]
                defect_info = f"Detected defects: {', '.join(defect_labels)}"
                analysis_type = "defect_analysis"
            else:
                defect_info = "No defects detected (Normal battery)"
                analysis_type = "normal_analysis"
            
            if "llava_output" not in st.session_state:
                print("=" * 60)
                print("🚀 AI 분석 시작")
                print(f"📊 분석 유형: {analysis_type}")
                print(f"🔍 결함 정보: {defect_info}")
                print("=" * 60)
                
                start_time = time.time()
                with st.spinner("이미지를 분석 중입니다..."):
                    # GPU 상태 표시
                    if self.system_config.gpu_available:
                        print(f"🚀 GPU 가속 모드로 실행 중: {self.system_config.gpu_name}")
                        print("💡 Ollama가 자동으로 GPU를 사용하여 더 빠른 처리를 제공합니다.")
                    else:
                        print("💻 CPU 모드로 실행 중")
                        print("⚠️ GPU를 사용할 수 없어 처리 시간이 오래 걸릴 수 있습니다.")
                    
                    # Ollama 모델 상태 확인
                    print("📋 Ollama 모델 상태 확인 중...")
                    
                    analysis_start = time.time()
                    st.session_state.llava_output = self.ai_analyzer.analyze_image(
                        image_path, mask_path, defect_info, analysis_type
                    )
                    analysis_end = time.time()
                
                end_time = time.time()
                total_time = end_time - start_time
                analysis_time = analysis_end - analysis_start
                
                print("=" * 60)
                print("✅ AI 분석 완료")
                print(f"⏱️  총 소요 시간: {total_time:.2f}초 ({total_time/60:.2f}분)")
                print(f"🤖 AI 분석 시간: {analysis_time:.2f}초 ({analysis_time/60:.2f}분)")
                print(f"📝 답변 길이: {len(st.session_state.llava_output)} 문자")
                print("=" * 60)
            
            st.markdown(f"**분석 결과:**\n\n{st.session_state.llava_output}")
            st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    
    def _handle_chat(self, image_path: str, mask_path: str):
        """채팅 처리"""
        if ("llava_output" in st.session_state and st.session_state.llava_output 
            and not st.session_state.get("show_pdf", False)):
            
            st.subheader("💬 추가 질문")
            
            # 기존 대화 히스토리 표시
            for chat in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.markdown(chat["question"])
                with st.chat_message("assistant"):
                    st.markdown(chat["answer"])
            
            # 사용자 입력
            user_input = st.chat_input("결함 분석 결과에 대해 궁금한 점을 입력하세요.")
            if user_input:
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                print("-" * 50)
                print("💬 채팅 질의응답 시작")
                print(f"❓ 질문: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")
                
                qa_start = time.time()
                with st.spinner("답변 중입니다..."):
                    answer = self.ai_analyzer.answer_question(
                        image_path, mask_path, user_input, st.session_state.llava_output
                    )
                qa_end = time.time()
                
                qa_time = qa_end - qa_start
                print(f"⏱️  질의응답 시간: {qa_time:.2f}초 ({qa_time/60:.2f}분)")
                print(f"📝 답변 길이: {len(answer)} 문자")
                print("-" * 50)
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                
                st.session_state.chat_history.append({"question": user_input, "answer": answer})
    
    def _handle_pdf_generation(self, image_path: str, mask_path: str):
        """PDF 생성 처리"""
        if ("llava_output" in st.session_state and st.session_state.llava_output 
            and "chat_history" in st.session_state and len(st.session_state.chat_history) > 0):
            
            if not st.session_state.show_pdf:
                if st.button("대화 종료 및 보고서 생성"):
                    st.session_state.show_pdf = True
            
            if st.session_state.show_pdf:
                try:
                    print("📄 PDF 보고서 생성 시작...")
                    
                    # 오버레이 이미지 저장
                    overlay_path = self.file_manager.create_temp_image_path("overlay", "png")
                    overlay_created = False
                    
                    if "colored_mask" in st.session_state and st.session_state.colored_mask is not None:
                        try:
                            # 원본 이미지 로드
                            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
                            if img is not None:
                                img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                
                                # 컬러 마스크 리사이즈
                                colored_mask_resized = cv2.resize(st.session_state.colored_mask, (img.shape[1], img.shape[0]))
                                
                                # 오버레이 생성
                                overlay = ImageProcessor.create_overlay(img_display, colored_mask_resized)
                                
                                # 오버레이 이미지 저장
                                cv2.imwrite(overlay_path, overlay)
                                overlay_created = True
                                print(f"✅ 오버레이 이미지 생성 완료: {overlay_path}")
                            else:
                                print("⚠️ 원본 이미지를 로드할 수 없습니다.")
                        except Exception as e:
                            print(f"❌ 오버레이 이미지 생성 실패: {e}")
                    else:
                        print("⚠️ 컬러 마스크가 세션에 없습니다.")
                    
                    # PDF 생성
                    print("📋 PDF 생성 중...")
                    tmp_file = self.pdf_generator.create_report(
                        image_path, mask_path, overlay_path if overlay_created else None,
                        st.session_state.llava_output, st.session_state.chat_history
                    )
                    
                    if tmp_file:
                        print(f"✅ PDF 생성 완료: {tmp_file}")
                        with open(tmp_file, "rb") as f:
                            st.download_button(
                                label="보고서 PDF 다운로드",
                                data=f,
                                file_name="battery_defect_llava_report.pdf",
                                mime="application/pdf"
                            )
                        
                        # 임시 파일들을 세션에 추가하여 나중에 정리
                        if "uploaded_files" not in st.session_state:
                            st.session_state.uploaded_files = []
                        st.session_state.uploaded_files.append(tmp_file)
                        
                        # 임시 파일 정리 (다운로드 후)
                        try:
                            os.remove(tmp_file)
                            print("🧹 PDF 임시 파일 정리 완료")
                        except Exception:
                            pass
                    else:
                        print("❌ PDF 생성 실패")
                    
                    # 오버레이 임시 파일 정리
                    if overlay_created and os.path.exists(overlay_path):
                        try:
                            os.remove(overlay_path)
                            print("🧹 오버레이 임시 파일 정리 완료")
                        except Exception:
                            pass
                        
                except Exception as e:
                    print(f"❌ PDF 생성 중 오류: {str(e)}")
                    st.error(f"PDF 생성 중 오류가 발생했습니다: {str(e)}")
                    # 오류 발생 시에도 임시 파일 정리
                    if 'overlay_path' in locals() and os.path.exists(overlay_path):
                        try:
                            os.remove(overlay_path)
                        except Exception:
                            pass
    
    def run(self):
        """메인 애플리케이션 실행"""
        # 제목
        st.markdown("""
        <h1 style='text-align: center; margin-bottom: 50px;'>🔍 배터리 CT 결함 분석 프로그램</h1>
        """, unsafe_allow_html=True)
        
        # 이전 파일 정리
        self._cleanup_previous_files()
        
        # 비전 모델 로드
        self._load_vision_model()
        
        # 이미지 업로드
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            uploaded_ct = st.file_uploader("**CT 이미지를 업로드하세요**", type=["png", "jpg", "jpeg"])
        
        if uploaded_ct:
            # 이미지 처리
            image_path = self._process_uploaded_image(uploaded_ct)
            
            # 결과 표시
            mask_path = self._display_results(image_path)
            
            if mask_path:
                # AI 분석
                self._handle_ai_analysis(image_path, mask_path)
                
                # 채팅
                self._handle_chat(image_path, mask_path)
                
                # PDF 생성
                self._handle_pdf_generation(image_path, mask_path)

# =============================================================================
# 메인 실행
# =============================================================================

if __name__ == "__main__":
    app = BatteryDefectAnalyzer()
    app.run() 