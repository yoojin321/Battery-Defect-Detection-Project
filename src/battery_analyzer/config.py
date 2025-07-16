"""
배터리 CT 결함 분석 프로그램 설정
"""

import os

# 환경 변수 설정
ENV_VARS = {
    "CUDA_VISIBLE_DEVICES": "0",
    "OLLAMA_HOST": "0.0.0.0:11434",
    "OLLAMA_GPU_LAYERS": "35",
    "OLLAMA_GPU_MEMORY_UTILIZATION": "0.8"
}

# 모델 설정
MODEL_CONFIG = {
    "path": "models/best_deeplabv3_efficientnet_model.pth",
    "num_classes": 5,
    "backbone": "efficientnet-b0",
    "input_size": (256, 256)
}

# 결함 클래스 정의
DEFECT_CLASSES = {
    0: "Background",
    1: "Battery", 
    2: "Swelling",
    3: "Porosity",
    4: "Resin Overflow"
}

# 색상 정의
COLORS = {
    0: [0, 0, 0],        # Background - Black
    1: [255, 0, 0],      # Battery - Red
    2: [0, 255, 0],      # Swelling - Green
    3: [0, 0, 255],      # Porosity - Blue
    4: [255, 255, 0],    # Resin Overflow - Yellow
}

# 색상과 레이블 매핑
COLORS_AND_LABELS = {
    class_id: (COLORS[class_id], DEFECT_CLASSES[class_id])
    for class_id in COLORS.keys()
}

# 정상 배터리 조건
NORMAL_BATTERY_RULE = """정상 배터리 셀은 외곽이 매끄럽고, 두께가 일정하며, 내부 구조가 균일하게 분포되어 있어야 합니다. 
셀 표면이나 내부에 불룩하게 팽창된 부위, 움푹 들어간 부분, 비정상적인 명암 변화, 이물질 또는 손상 흔적이 없어야 합니다.""" 