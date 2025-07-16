"""
시스템 설정 및 GPU 확인 모듈
"""

import os
import subprocess
import torch
from .config import ENV_VARS

class SystemConfig:
    """시스템 설정 및 GPU 확인 클래스"""
    
    def __init__(self):
        self.gpu_available = False
        self.gpu_name = "Unknown"
        self.gpu_memory = 0
        self._setup_environment()
        self._check_gpu()
        self._check_ollama()
    
    def _setup_environment(self):
        """환경 변수 설정"""
        for key, value in ENV_VARS.items():
            os.environ[key] = value
    
    def _check_gpu(self):
        """GPU 사용 가능 여부 확인"""
        # nvidia-smi로 GPU 확인
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(', ')
                if len(gpu_info) >= 2:
                    self.gpu_name = gpu_info[0]
                    self.gpu_memory = float(gpu_info[1]) / 1024
                    self.gpu_available = True
                    print(f"✅ GPU 감지됨: {self.gpu_name}")
                    print(f"GPU 메모리: {self.gpu_memory:.1f}GB")
                else:
                    print("⚠️ GPU를 찾을 수 없습니다.")
            else:
                print("⚠️ nvidia-smi를 실행할 수 없습니다.")
        except Exception as e:
            print(f"⚠️ GPU 확인 중 오류: {str(e)}")
        
        # PyTorch CUDA 확인
        try:
            if hasattr(torch, 'cuda') and torch.cuda.is_available():
                self.gpu_available = True
                self.gpu_name = torch.cuda.get_device_name(0)
                self.gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"✅ PyTorch CUDA 사용 가능: {self.gpu_name}")
            else:
                print("PyTorch CUDA를 사용할 수 없지만, Ollama가 직접 GPU를 사용할 수 있습니다.")
        except ImportError:
            print("PyTorch가 설치되지 않았습니다. Ollama가 자동으로 GPU를 사용할 것입니다.")
        except Exception as e:
            print(f"PyTorch 초기화 중 오류: {str(e)}. Ollama가 직접 GPU를 사용할 수 있습니다.")
    
    def _check_ollama(self):
        """Ollama 서비스 상태 확인"""
        try:
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True)
            if result.returncode == 0:
                print("Ollama 서비스가 실행 중입니다.")
            else:
                print("Ollama 서비스가 실행되지 않았습니다.")
        except Exception as e:
            print(f"Ollama 상태 확인 중 오류: {str(e)}") 