"""
AI 분석 모듈
"""

import ollama
import streamlit as st
from .config import NORMAL_BATTERY_RULE, DEFECT_CLASSES
import time

class AIAnalyzer:
    """AI 분석 클래스"""
    
    def __init__(self):
        self.normal_rule = NORMAL_BATTERY_RULE
    
    def create_prompt(self, defect_info: str, analysis_type: str) -> str:
        """분석 프롬프트 생성"""
        if analysis_type == "defect_analysis":
            return f"""
당신은 배터리 결함 분석 전문가입니다. (의료, 건강 관련 분석은 하지 않습니다.)

업로드된 2개의 이미지를 분석해주세요:
- 첫 번째 이미지: 배터리 셀의 CT 이미지
- 두 번째 이미지: 첫 번째 이미지에서 발견된 모든 결함 영역을 마스킹한 이미지
- {defect_info}

정상 배터리 조건: {self.normal_rule}

아래 항목을 참고하여, 실제 이미지에서 관찰된 내용을 바탕으로 논리적이고 구체적으로 분석 결과를 작성하세요.

1. 배터리의 전반적인 구조와 특징을 간단히 요약
2. 탐지된 결함(들)이 정상 조건과 어떻게 다른지, 구체적으로 어떤 부분이 결함으로 판단되는지 설명
3. 각 결함이 배터리 성능에 미치는 영향(실제 관찰된 결함의 특성에 근거)
4. 결론 및 권장사항(중복 없이 간결하게)

**주의사항**
- 각 항목을 한 번씩만, 중복 없이 서술
- 프롬프트 문구를 복사하지 말고, 실제 이미지에서 관찰된 차이점과 결함의 근거를 중심으로 설명
- 자연스럽고 논리적인 한국어로 작성
"""
        else:
            return f"""
당신은 배터리 결함 분석 전문가입니다. (의료, 건강 관련 분석은 하지 않습니다.)

업로드된 2개의 이미지를 분석해주세요:
- 첫 번째 이미지: 배터리 셀의 CT 이미지
- 두 번째 이미지: 첫 번째 이미지에서 발견된 모든 결함 영역을 마스킹한 이미지
- {defect_info}

정상 배터리 조건: {self.normal_rule}

**중요: 결함이 감지되지 않았으므로, 정상 배터리로 판단하여 분석해주세요.**

아래 항목을 참고하여, 실제 이미지에서 관찰된 내용을 바탕으로 논리적이고 구체적으로 분석 결과를 작성하세요.

1. 배터리의 전반적인 구조와 특징을 간단히 요약
2. 정상 배터리의 특징과 관찰된 구조의 일치점 설명
3. 결함이 없다고 판단한 근거 (정상 조건과의 비교)
4. 결론

**주의사항**
- 결함이 감지되지 않았으므로, 결함 관련 내용을 언급하지 마세요
- 정상 배터리의 특징과 현재 상태의 일치점을 중심으로 설명
- 프롬프트 문구를 복사하지 말고, 실제 이미지에서 관찰된 내용을 바탕으로 설명
- 자연스럽고 논리적인 한국어로 작성
"""
    
    def analyze_image(self, image_path: str, mask_path: str, defect_info: str, analysis_type: str) -> str:
        """이미지 분석 수행"""
        print("🔧 프롬프트 생성 중...")
        prompt_start = time.time()
        prompt = self.create_prompt(defect_info, analysis_type)
        prompt_end = time.time()
        print(f"📝 프롬프트 생성 완료: {prompt_end - prompt_start:.2f}초")
        print(f"📄 프롬프트 길이: {len(prompt)} 문자")
        
        print("🤖 LLaVA 모델 호출 중...")
        try:
            llava_start = time.time()
            res = ollama.chat(
                model="llava:7b",
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_path, mask_path]
                    }
                ]
            )
            llava_end = time.time()
            llava_time = llava_end - llava_start
            print(f"✅ LLaVA 응답 완료: {llava_time:.2f}초")
            
            result = res['message']['content']
            print(f"📊 응답 길이: {len(result)} 문자")
            return result
        except Exception as e:
            print(f"❌ LLaVA 분석 오류: {str(e)}")
            st.error(f"LLaVA 분석 중 오류가 발생했습니다: {str(e)}")
            return "분석 중 오류가 발생했습니다."
    
    def answer_question(self, image_path: str, mask_path: str, question: str, analysis_result: str) -> str:
        """추가 질문 답변"""
        print("🔧 질의응답 프롬프트 생성 중...")
        qa_prompt = f'''배터리 결함 분석 전문가입니다.

분석 결과: {analysis_result}

질문: {question}

위 정보와 이미지를 바탕으로 3~4문장으로 답변해주세요.'''
        
        print(f"📄 질의응답 프롬프트 길이: {len(qa_prompt)} 문자")
        print("🤖 LLaVA 질의응답 호출 중...")
        
        try:
            qa_llava_start = time.time()
            qa_res = ollama.chat(
                model="llava:7b",
                messages=[
                    {
                        'role': 'user',
                        'content': qa_prompt,
                        'images': [image_path, mask_path]
                    }
                ]
            )
            qa_llava_end = time.time()
            qa_llava_time = qa_llava_end - qa_llava_start
            print(f"✅ LLaVA 질의응답 완료: {qa_llava_time:.2f}초")
            
            result = qa_res['message']['content']
            print(f"📊 질의응답 길이: {len(result)} 문자")
            return result
        except Exception as e:
            print(f"❌ LLaVA 질의응답 오류: {str(e)}")
            st.error(f"질의응답 중 오류가 발생했습니다: {str(e)}")
            return "답변 생성 중 오류가 발생했습니다." 