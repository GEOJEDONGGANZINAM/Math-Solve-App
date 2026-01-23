import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (형님 승인 완료된 버전)
# ==========================================
st.set_page_config(layout="wide", page_title="2호기: The Masterpiece")

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }

    /* 본문 13px, 제목 16px (절대 준수) */
 /* 전체 배경 흰색 강제 적용 */
    .stApp {
        background-color: #ffffff !important;
    }
    html, body, [class*="css"] {
        font-size: 13px !important; 
        color: #000000 !important; /* 완전 블랙으로 가독성 UP */
        background-color: #ffffff !important;
    }
    
    h1, h2, h3, h4, .step-title {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #000000 !important; /* 리얼 블랙 */
        margin-bottom: 0.5rem !important;
        line-height: 1.4 !important;
    }
    
    .stMarkdown p, li {
        font-size: 13px !important;
        line-height: 1.7 !important;
        color: #374151 !important;
        margin-bottom: 0.5rem !important;
    }

    /* 사이드바: 흰 배경, 검은 글씨 */
    section[data-testid="stSidebar"] {
        background-color: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    section[data-testid="stSidebar"] * {
        color: #111827 !important;
    }
    
    /* 카드 UI */
    .step-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    
    .step-number {
        display: inline-block;
        background-color: #111827;
        color: white !important;
        font-size: 11px !important;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 99px;
        margin-bottom: 12px;
    }

    /* 오른쪽 그래프 컨테이너 (Sticky) */
    div[data-testid="stVerticalBlock"] > div:has(> iframe),
    div[data-testid="stVerticalBlock"] > div:has(> img) {
        position: sticky;
        top: 3rem;
        z-index: 50;
        background: white;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
        border: 1px solid #f3f4f6;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background-color: white;
        border: 1px solid #d1d5db;
        color: #374151 !important;
        font-size: 12px !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1rem;
    }
    .stButton > button:hover {
        background-color: #f3f4f6;
        color: #000000 !important;
        border-color: #9ca3af;
    }

/* 1. 라디오 버튼 (Method 1, 2, 3) 글씨 검은색으로 강제 변경 */
    div[data-testid="stRadio"] label p {
        color: #000000 !important;
        font-weight: 600 !important; /* 잘 보이게 약간 굵게 */
    }

    /* 2. 사이드바 배경색을 3.png 색상(청록색)으로 변경 */
    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important; /* 형님이 주신 그 민트색 */
    }

/* 1. 상단 헤더바 흰색 + 하단 회색 테두리 1줄 */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 1px solid #e5e7eb !important; /* 여기 회색 줄 추가했습니다 */
    }

    /* 2. 텍스트 입력창 배경 흰색 & 테두리 제거 */
    input[type="text"], input[type="password"] {
        background-color: #ffffff !important;
        color: #000000 !important; /* 입력 글씨 검은색 */
        border: none !important; /* 테두리 삭제 */
    }
    
    /* 입력창 컨테이너도 흰색 처리 (잔여 테두리 방지) */
    div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
        border: none !important;
    }

    /* 3. 파일 업로더 박스 흰색 & 테두리 제거 */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border: none !important;
    }
    
    /* 업로더 내부 글씨 및 아이콘 색상 교정 */
    section[data-testid="stFileUploaderDropzone"] * {
        color: #374151 !important;
    }

/* 1. API Key 입력창 옆 '눈 모양' 버튼 배경 흰색으로 변경 */
    div[data-baseweb="input"] button {
        background-color: #ffffff !important;
        border: none !important;
    }

    /* 눈 아이콘(SVG) 색상은 잘 보이게 진한 회색으로 변경 (배경이 흰색이라 필수) */
    div[data-baseweb="input"] svg {
        fill: #374151 !important; 
    }

    /* 2. 'Browse files' 버튼 배경 흰색으로 변경 */
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #ffffff !important;
        color: #000000 !important; /* 글씨는 검은색 */
        border: 1px solid #d1d5db !important; /* 버튼 윤곽 살리기 */
    }

    /* Browse files 버튼에 마우스 올렸을 때 살짝 회색 (반응형) */
    section[data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #f9fafb !important;
        border-color: #9ca3af !important;
    }

/* API Key 입력창 전체 컨테이너의 검은색 테두리를 흰색으로 강제 변경 */
    div[data-baseweb="input"] {
        border-color: #ffffff !important;
        /* 스트림릿 구버전/신버전 테두리 방식 모두 대응 (박스 그림자까지 흰색 처리) */
        box-shadow: 0 0 0 1px #ffffff !important;
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 로직: LaTeX 강제 띄어쓰기 (강화판)
# ==========================================
def fix_latex_spacing(text):
    if not text: return ""
    
    # 1. $수식$ 뒤에 한글/알파벳/숫자가 붙으면 강제로 띄움
    # 예: $x$는 -> $x$ 는
    text = re.sub(r'(\$[^$]+\$)([가-힣a-zA-Z0-9])', r'\1 \2', text)
    
    # 2. 한글/알파벳/숫자 뒤에 $수식$이 붙으면 강제로 띄움
    # 예: 값은$y$ -> 값은 $y$
    text = re.sub(r'([가-힣a-zA-Z0-9])(\$[^$]+\$)', r'\1 \2', text)
    
    return text

# ==========================================
# 3. 상태 관리
# ==========================================
if 'step_index' not in st.session_state:
    st.session_state.step_index = 1
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# ==========================================
# 4. 사이드바
# ==========================================
# 수정된 사이드바 코드 (입력창 삭제됨)
with st.sidebar:
    st.header("입력 설정")
    
    # 1. 입력창 없이 바로 금고에서 키를 꺼내옵니다.
    # 학생들이나 다른 사람은 이 키를 절대 볼 수 없습니다.
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except FileNotFoundError:
        st.error("보안 키(secrets.toml)를 찾을 수 없습니다!")
        st.stop()
    
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"])
    
    if st.button("앱 초기화 (Reset)"):
        st.session_state.step_index = 1
        st.session_state.analysis_result = None
        st.rerun()

# ==========================================
# 5. 메인 로직
# ==========================================

if not uploaded_file:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("👈 API 키와 문제 사진을 넣어주세요.")
        st.markdown("""
        ### 🛠 수정 완료 보고
        1. **가독성 확보:** 모든 설명은 **개조식(Bullet Point)** 으로 작성되어 읽기 편합니다.
        2. **수식 렌더링 Fix:** 수식과 글자 사이를 강제로 띄워, `$코드`가 그대로 노출되는 현상을 막았습니다.
        3. **규격 준수:** 폰트 크기와 색상을 형님 지시대로 맞췄습니다.
        """)
    st.stop()

if uploaded_file and st.session_state.analysis_result is None:
    image = Image.open(uploaded_file)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(image, caption="원본 문제", use_container_width=True)
    with c2:
        st.markdown("### 🧠 분석 대기 중")
        if api_key:
            if st.button("3가지 관점으로 완벽 분석 시작", type="primary"):
                status_box = st.empty()
                status_box.info("🕵️ 최적의 AI 모델 탐색 중...")
                
                try:
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = next((m for m in models if 'gemini-1.5-flash' in m), 
                                     next((m for m in models if 'gemini-1.5-pro' in m), models[0]))
                    
                    model = genai.GenerativeModel(model_name)
                    
                    status_box.info(f"⚡ {model_name} 모델로 분석 시작...")
                    
# --- [프롬프트 수정: 폰트 크기 및 가독성 지시 강화] ---
                    prompt = """
                    너는 대한민국 1타 수학 강사야. 이 문제를 **3가지 방식**으로 풀이해.
                    
                    **[제 1원칙: 가독성 (형님 지시사항)]**
                    1. **무조건 개조식(Bullet Points) 사용**: 줄글로 길게 쓰지 마. `- ` 기호를 써서 문장을 끊어.
                    2. **줄바꿈 필수**: 내용이 바뀌면 무조건 줄을 바꿔. 벽돌처럼 뭉친 텍스트 절대 금지.
                    3. **수식 강조**: 중요한 계산식은 본문 중간에 끼워넣지 말고, **별도의 줄에 `$$ 수식 $$`** 형태로 써서 강조해.
                    4. **형광펜/코드 스타일 금지**: 텍스트 중간에 ` `(백틱)을 절대 쓰지 마. 강조가 필요하면 오직 **굵게(Bold)** 처리만 해.
                    
                    **[제 2원칙: 띄어쓰기 (매우 중요)]**
                    1. 인라인 수식 `$수식$`을 쓸 때는 **반드시 앞뒤에 공백**을 넣어. 
                       - (O) 값은 $x$ 이다.
                       - (X) 값은$x$이다.
                    
                    **[풀이 구성]**
                    - Method 1: **정석 풀이** (논리적 서술)
                    - Method 2: **빠른 풀이** (실전 스킬)
                    - Method 3: **직관 풀이** (도형/그래프 해석)
                    
                    **[시각화 코드 규칙 (폰트 크기 엄수)]**
                    - `def draw(method, step):` 작성. `figsize=(6, 6)`.
                    - **한글 깨짐 방지를 위해 반드시 영어(English)로 텍스트 출력.**
                    - **그래프 제목(Title) 폰트 크기는 무조건 16으로 설정.** (`fontsize=16`)
                    - **그래프 내부 텍스트/좌표(Annotation) 폰트 크기는 무조건 11로 설정.** (`fontsize=11`)
                    - 중요 포인트(Points)는 눈에 띄는 색(빨강, 파랑 등)으로 강조.
                    
                    **[출력 포맷]**
                    #METHOD_1#
                    [1단계 제목]
                    - 설명...
                    $$ 수식 $$
                    ---
                    [2단계 제목]
                    - 설명...
                    
                    #METHOD_2#
                    ...
                    
                    #METHOD_3#
                    ...
                    
                    #CODE#
                    ```python
                    def draw(method, step):
                        fig, ax = plt.subplots(figsize=(6, 6))
                        # 예시: 제목 16, 텍스트 11
                        ax.set_title(f"Method {method} - Step {step}", fontsize=16)
                        ax.text(0, 0, "Text", fontsize=11)
                        return fig
                    ```
                    """
                    
                    response = model.generate_content([prompt, image])
                    st.session_state.analysis_result = response.text
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                    st.write(traceback.format_exc())
        else:
            st.warning("API 키를 입력해주세요.")
    st.stop()

# [결과 화면 표시 섹션 - 왼쪽 벽에 딱 붙임]
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    try:
        # 1. 코드와 본문 분리
        parts = full_text.split("#CODE#")
        text_full = parts[0]
        code_part = parts[1] if len(parts) > 1 else ""
        
        # 2. 풀이 방법 파싱 (정규표현식)
        import re
        methods = {}
        pattern = r"#METHOD_(\d)#(.*?)(?=#METHOD_|\Z)"
        matches = re.findall(pattern, text_full, re.DOTALL)
        
        for m_id, content in matches:
            methods[int(m_id)] = content.strip()
        
        # 3. 파이썬 코드 추출
        code_match = re.search(r"```python(.*?)```", code_part, re.DOTALL)
        final_code = code_match.group(1).strip() if code_match else code_part.strip()
        
        # 4. 화면 분할 (왼쪽: 설명 / 오른쪽: 그래프)
        col_left, col_right = st.columns([1.2, 1])
        
        # === [왼쪽: 설명 창] ===
        with col_left:
            st.markdown("### 🟦 풀이 방법 선택")
            selected_method_name = st.radio(
                "풀이 방법을 선택하세요",
                ["Method 1: 정석 풀이", "Method 2: 빠른 풀이", "Method 3: 직관 풀이"],
                label_visibility="collapsed",
                horizontal=True
            )
            
            method_id = int(selected_method_name.split(":")[0].replace("Method ", ""))
            st.markdown("---")
            
            # 단계별 설명 출력 (박스형 UI)
# [수정된 부분] 화살표 삭제 & 형광펜 제거 버전
        if method_id in methods:
            steps_raw = methods[method_id].split("---")
            steps = [s.strip() for s in steps_raw if s.strip()]
            
            for i, step_text in enumerate(steps):
                lines = step_text.split('\n')
                
                # 1. 제목 처리 (대괄호 제거 + arrow_down 글자 삭제)
                raw_title = lines[0].strip().replace('[', '').replace(']', '')
                raw_title = raw_title.replace('arrow_down', '').replace(':arrow_down:', '').replace('_', ' ')
                title = raw_title.replace('$', ' $ ').strip()
                
                # 2. 본문 처리 (형광펜 ` 제거 -> 수식 $ 변환)
                body_lines = lines[1:]
                body_text = '\n'.join(body_lines).strip()
                
                # 핵심: ` (백틱)을 $ (달러)로 바꿔서 검은 배경을 없애고 수식으로 변환
                body_text = body_text.replace('`', '$')
                body_text = body_text.replace('$', ' $ ') # 수식 앞뒤 띄어쓰기 확보
                
                # 3. 접이식 박스 출력
                with st.expander(f"STEP {i+1}: {title}", expanded=True):
                    st.markdown(body_text)
                    
                    if st.button(f"📊 이 단계({i+1}) 그래프 보기", key=f"btn_{method_id}_{i}"):
                        st.session_state.step_index = i + 1
            else:
                st.info("이 풀이 방법은 생성되지 않았습니다.")

# === [오른쪽: 그래프 창] ===
        with col_right:
            with st.container():
                st.markdown(f"### 📐 실시간 시각화 (Method {method_id} - Step {st.session_state.step_index})")
                try:
                    # 그래프 그리기 실행
                    exec_globals = {"np": np, "plt": plt, "patches": patches}
                    exec(final_code, exec_globals)
                    
                    if "draw" in exec_globals:
                        fig = exec_globals["draw"](method_id, st.session_state.step_index)
                        
                        # [수정] 양옆에 투명 벽을 세워서 사이즈를 강제로 50%로 줄임
                        # 비율 조절: [1(왼쪽공백) : 3(그래프) : 1(오른쪽공백)]
                        _, c_graph, _ = st.columns([1, 3, 1])
                        with c_graph:
                            st.pyplot(fig)
                            
                    else:
                        st.error("시각화 함수(draw)를 찾을 수 없습니다.")
                except Exception as e:
                    st.warning(f"아직 그래프가 생성되지 않았거나 오류가 발생했습니다.\n({e})")

    except Exception as e:
        st.error(f"분석 결과를 처리하는 중 오류가 발생했습니다: {e}")