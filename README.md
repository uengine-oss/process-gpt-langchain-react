# MCP ReAct Client 🚀

**LangChain MCP 어댑터를 사용한 ReAct 기반 Python 인터프리터 클라이언트**

영상: https://youtu.be/PunCR0aQAC0

이 프로젝트는 [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)를 활용하여 MCP (Model Context Protocol) 서버와 상호작용하는 ReAct 에이전트를 구현합니다. 자연어 명령을 통해 Python 코드 실행, 파일 관리, 환경 관리 등의 작업을 수행할 수 있습니다.

## 🌟 주요 기능

- **🤖 ReAct 에이전트**: OpenAI GPT-4를 사용한 추론-행동 패턴
- **🔌 MCP 서버 연결**: Python 인터프리터 서버와 자동 연결
- **💬 인터랙티브 모드**: 실시간 사용자 입력 처리
- **📊 데모 모드**: 미리 정의된 예시 실행
- **🛠️ 9가지 도구**: 파일 조작, 코드 실행, 환경 관리
- **🎯 복잡한 작업**: Bayesian 최적화 같은 고급 엔지니어링 문제 해결

## 📦 설치 및 설정

### 1. 프로젝트 클론 및 의존성 설치

```bash
git clone <repository-url>
cd langchain-mcp-adapters

# uv를 사용한 의존성 설치
uv sync
```

### 2. OpenAI API 키 설정

환경 변수로 설정하거나 코드에서 직접 설정:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## 🚀 사용 방법

### 인터랙티브 모드 (기본)

```bash
uv run python -m mcp_react_client.main
# 또는
uv run python -m mcp_react_client.main interactive
```

## 설치
`.env` 파일에 환경변수 설정
uv venv
uv pip install -r requirements.txt
source .venv/Scripts/activate
deactivate
python -X utf8 main.py > output.log 2>&1
python main.py

### 데모 모드

```bash
uv run python -m mcp_react_client.main demo
```

## 🛠️ 사용 가능한 도구

클라이언트는 다음 9가지 MCP 도구를 사용할 수 있습니다:

1. **read_file** - 파일 내용 읽기
2. **write_file** - 파일 생성/수정
3. **list_directory** - 디렉토리 내용 나열
4. **list_python_environments** - Python 환경 목록
5. **list_installed_packages** - 설치된 패키지 목록
6. **run_python_code** - Python 코드 실행
7. **install_package** - 패키지 설치
8. **write_python_file** - Python 파일 생성
9. **run_python_file** - Python 파일 실행

## 💡 특별 명령어

인터랙티브 모드에서 사용 가능한 특별 명령어:

- `help` - 예제 명령어들 보기
- `tools` - 사용 가능한 도구 목록 보기
- `quit`, `exit`, `q` - 프로그램 종료

## 📚 사용 예시

### 기본 예시

```
🤖 Enter your command: Show me all available Python environments on my system

🤖 Enter your command: Run this Python code: print('Hello, World!')

🤖 Enter your command: Create a Python file called 'test.py' with a hello function

🤖 Enter your command: List all files in the current directory
```

### 고급 예시

```
🤖 Enter your command: Install numpy and create a script to calculate matrix multiplication

🤖 Enter your command: Create a data analysis script with pandas and matplotlib

🤖 Enter your command: Write a function to solve quadratic equations and test it
```

### 복잡한 엔지니어링 예시

**열연 최적화 문제** (Bayesian Optimization):

```
🤖 Enter your command: Create and run Python code for energy-saving hot-rolling recipe optimization: minimize cost (electricity + roll wear) with constraints thickness deviation ≤ 0.20 mm and surface defect rate ≤ 0.5%, using Bayesian optimization on temperature (800-950°C) and speed (2-8 m/s), with surrogate models electricity=0.6*(0.02*(temp-800)+0.03*speed²), roll_wear=1.0*(0.002*(temp-800)+0.04*speed), thickness_dev=0.35-0.00015*(temp-800)+0.01*speed, surface_def=1.00-0.001*(temp-800)+0.03*speed, run 30 iterations with penalties 2000 for thickness and 1500 for surface violations, output best settings, recipe summary, CSV history and matplotlib plots
```

**실행 결과:**
- ✅ Bayesian 최적화 알고리즘 구현 및 실행
- ✅ 제약 조건 적용 및 처리
- ✅ 최적 설정 발견: 온도 800°C, 속도 2m/s
- ✅ 최소 비용: 3,500.152
- ✅ 시각화 파일 생성: 'optimization_history.png'

## 🎯 사용 사례 카테고리

### 🔧 Python 환경 관리
- "Show me all available Python environments"
- "List installed packages in default environment"
- "Install numpy package in system environment"

### 💻 Python 코드 실행
- "Run this Python code: print('Hello, World!')"
- "Execute this code: import math; print(math.pi)"
- "Run a calculation: 2 + 2 * 3"

### 📁 파일 작업
- "Create a Python file called 'test.py' with a hello function"
- "Read the contents of hello.py file"
- "List all files in the current directory"

### 🧮 고급 예시
- "Create a script that calculates fibonacci numbers"
- "Write a Python function to sort a list"
- "Run a data analysis script with pandas"

### 🏭 복잡한 엔지니어링 작업
- "Optimize a hot-rolling steel process using Bayesian optimization"
- "Create a machine learning model for predictive maintenance"
- "Solve a multi-objective optimization problem with constraints"

## 🏗️ 프로젝트 구조

```
langchain-mcp-adapters/
├── mcp_react_client/
│   ├── __init__.py
│   └── main.py          # 메인 클라이언트 코드
├── pyproject.toml       # 프로젝트 설정
├── README.md           # 이 파일
└── .venv/              # 가상 환경 (uv로 생성)
```

## ⚙️ 설정

### MCP 서버 설정

클라이언트는 다음 MCP 서버 설정을 사용합니다:

```python
server_params = StdioServerParameters(
    command="uvx",
    args=[
        "mcp-python-code-interpreter",
        "--dir",
        "/Users/uengine/temp",
        "--python-path",
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
    ],
    env={"MCP_ALLOW_SYSTEM_ACCESS": "0"}
)
```

### 필요 의존성

- Python ≥ 3.10
- langchain ≥ 0.3.0
- langchain-openai ≥ 0.2.0
- langgraph ≥ 0.2.0
- langchain-mcp-adapters ≥ 0.1.9
- python-dotenv ≥ 1.0.0
- mcp ≥ 1.9.1

## 🔍 동작 원리

1. **MCP 서버 연결**: `mcp-python-code-interpreter` 서버에 연결
2. **도구 로드**: MCP 서버에서 사용 가능한 도구들을 가져옴
3. **ReAct 에이전트**: 사용자 입력을 분석하고 적절한 도구 선택
4. **작업 실행**: 선택된 도구를 사용해 작업 수행
5. **결과 반환**: 실행 결과를 사용자에게 제공

## 🔬 기술 스택

- **LangChain**: LLM 애플리케이션 프레임워크
- **LangGraph**: 에이전트 워크플로우 관리
- **MCP (Model Context Protocol)**: 모델-컨텍스트 통신 프로토콜
- **OpenAI GPT-4**: 언어 모델
- **uvx**: Python 패키지 관리

## 🤝 기여

이 프로젝트는 [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)를 기반으로 구축되었습니다.

## 📄 라이선스

MIT License

## 🆘 문제 해결

### 일반적인 문제

1. **MCP 서버 연결 실패**
   - `mcp-python-code-interpreter` 패키지가 설치되어 있는지 확인
   - Python 경로가 올바른지 확인

2. **OpenAI API 오류**
   - API 키가 올바르게 설정되어 있는지 확인
   - API 사용량 한도를 확인

3. **의존성 문제**
   - `uv sync`를 다시 실행
   - Python 버전이 3.10 이상인지 확인

### 로그 확인

자세한 로그를 보려면 코드에서 다음을 추가:

```python
import traceback
traceback.print_exc()
```

## 🎉 성과

이 클라이언트는 다음과 같은 복잡한 작업들을 성공적으로 수행할 수 있습니다:

- ✅ 단순한 Python 코드 실행
- ✅ 파일 시스템 조작
- ✅ 패키지 관리
- ✅ 복잡한 데이터 분석
- ✅ 기계학습 워크플로우
- ✅ **Bayesian 최적화 같은 고급 엔지니어링 문제**

**"자연어로 명령하면, AI가 코드로 실행한다"** - 이것이 MCP ReAct Client의 핵심 가치입니다! 🚀
