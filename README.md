# 🔍 배터리 CT 결함 분석 프로그램

Streamlit 기반 AI 분석 애플리케이션으로, 배터리 CT 이미지에서 결함을 자동으로 탐지하고 분석하는 프로그램입니다.

## 🚀 주요 기능

- **AI 결함 탐지**: DeepLabV3+ 모델을 사용한 자동 결함 영역 탐지
- **실시간 분석**: LLaVA 모델을 통한 자연어 기반 결함 분석
- **대화형 인터페이스**: 채팅 형태의 추가 질의응답 기능
- **PDF 보고서**: 분석 결과를 PDF 형태로 자동 생성
- **GPU 가속**: CUDA 지원으로 빠른 처리 속도

## 📁 프로젝트 구조

```
battery_final_project/
├── app.py                    # 메인 진입점
├── src/                      # 소스 코드 디렉토리
│   └── battery_analyzer/     # 메인 패키지
│       ├── __init__.py       # 패키지 초기화
│       ├── config.py         # 설정 및 상수
│       ├── system_config.py  # 시스템 설정
│       ├── vision_model.py   # AI 비전 모델
│       ├── image_processor.py # 이미지 처리
│       ├── ui_components.py  # UI 컴포넌트
│       ├── file_manager.py   # 파일 관리
│       ├── ai_analyzer.py    # AI 분석
│       ├── pdf_generator.py  # PDF 생성
│       └── main_app.py       # 메인 애플리케이션
├── models/                   # AI 모델 파일
│   └── best_deeplabv3_efficientnet_model.pth
├── fonts/                    # 폰트 파일
├── requirements.txt          # 의존성 패키지
└── README.md                # 프로젝트 설명
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. Ollama 설치 및 모델 다운로드
```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# LLaVA 모델 다운로드
ollama pull llava:7b
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

## 🎯 사용법

1. **이미지 업로드**: CT 이미지를 업로드합니다
2. **자동 탐지**: AI가 결함 영역을 자동으로 탐지합니다
3. **AI 분석**: "AI 분석 시작" 버튼을 클릭하여 상세 분석을 수행합니다
4. **추가 질문**: 채팅 인터페이스를 통해 추가 질문을 할 수 있습니다
5. **보고서 생성**: "대화 종료 및 보고서 생성" 버튼으로 PDF 보고서를 다운로드합니다

## 🔧 기술 스택

- **Frontend**: Streamlit
- **AI 모델**: 
  - DeepLabV3+ (이미지 세그멘테이션)
  - LLaVA 7B (이미지 분석)
- **백엔드**: Python, PyTorch
- **GPU 가속**: CUDA, Ollama

## 📊 지원하는 결함 유형

- **Swelling**: 배터리 팽창
- **Porosity**: 기공 현상
- **Resin Overflow**: 레진 오버플로우
- **Background**: 배경
- **Battery**: 정상 배터리

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
