"""
배터리 CT 결함 분석 프로그램
Streamlit 기반 AI 분석 애플리케이션
"""

import streamlit as st
import atexit
st.set_page_config(page_title="배터리 CT 결함 분석 프로그램", layout="wide")

# 메인 애플리케이션 실행
from src.battery_analyzer import BatteryDefectAnalyzer

if __name__ == "__main__":
    app = BatteryDefectAnalyzer()
    
    # 애플리케이션 종료 시 정리 함수 등록
    atexit.register(app.cleanup)
    
    app.run()