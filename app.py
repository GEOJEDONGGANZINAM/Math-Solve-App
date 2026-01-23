import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (절대 안 건드림)
# ==========================================
st.set_page_config(layout="wide", page_title="2호기: 수학의 정점")

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }

    .stApp { background-color: #ffffff !important; }
    html, body, [class*="css"] {
        font-size: 13px !important; 
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    h1, h2, h3, h4 {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #000000 !important;
        margin-bottom: 0.5rem !important;
    }

    .stMarkdown p, li {
        font-size: 13px !important;
        line-height: 1.7 !important;
        color: #374151 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important;
        border-right: 1px solid #e5e7eb;
    }
    
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 1px solid #e5e7eb !important;
    }

    input[type="text"], input[type="password"], div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
    }
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border: none !important;
    }
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
    }

    div[data-testid="stRadio"] label p {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    .stButton > button {
        background-color: white;
        border: 1px solid #d1d5db;
        color: #374151 !important;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #f3f4f6;
        border-color: #00C4B4;
        color: #00C4B4 !important;
    }
    
    section[data-testid="stSidebar"] .stButton button p {
        color: #000000 !important;
        font-weight: 400 !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        color: #000000 !important;
    }

    div[data-testid="stSpinner"] * {
        color: #000000 !important;
    }

    .streamlit-expanderHeader {
        background-color: #f9fafb !important;
        border-radius: 8px !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 핵심 로직
# ==========================================
if 'step_index' not in st.session_state:
    st.session_state.step_index = 1
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바 UI
# ==========================================
with st.sidebar:
    st.title("Math AI 2호기")
    st.write("수학 문제 해결의 정점")
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"])
    
    st.markdown("---")
    if st.button("🔄 앱 초기화 (Reset)"):
        st.session_state.step_index = 1
        st.session_state.analysis_result = None
        st.rerun()

# ==========================================
# 4. 메인 분석 로직
# ==========================================
if not uploaded_file:
    st.info("👈 왼쪽 사이드바에서 문제 사진을 업로드해주세요.")
    st.stop()

if uploaded_file and st.session_state.analysis_result is None:
    image = Image.open(uploaded_file)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(image, caption="Uploaded Problem", use_container_width=True)
    with c2:
        st.markdown("### 🧠 AI 분석 준비 완료")
        if st.button("🚀 3가지 관점으로 완벽 분석 시작", type="primary"):
            with st.spinner("🕵️ 1타 강사의 시선으로 분석 중입니다..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = next((m for m in available_models if 'flash' in m), 
                                      next((m for m in available_models if 'pro' in m), available_models[0]))
                    
                    model = genai.GenerativeModel(model_name)
                    
                    # 프롬프트: 그래프 aspect ratio 정사각형(6,6)으로 고정 요청
                    prompt = """
                    너는 대한민국 1타 수학 강사야. 이 문제를 **3가지 방식**으로 풀이해.
                    
                    **[제 1원칙: 가독성 및 형식]**
                    1. **개조식 사용**: 문장은 `-` 로 시작하고 간결하게 끊어.
                    2. **수식 강조**: 중요 수식은 별도 줄에 `$$ 수식 $$` 사용.
                    3. **텍스트 스타일**: 코드 블록(```)이나 백틱(`)을 텍스트 강조용으로 쓰지 마. 오직 **Bold**만 사용.
                    4. **띄어쓰기**: `$수식$` 앞뒤는 반드시 띄어쓰기 (예: 값이 $x$ 다).
                    
                    **[풀이 구성]**
                    - Method 1: **정석 풀이** (논리적 서술)
                    - Method 2: **빠른 풀이** (실전 스킬)
                    - Method 3: **직관 풀이** (도형/그래프 해석)
                    
                    **[시각화 코드 규칙 (엄수)]**
                    - `def draw(method, step):` 작성.
                    - **figsize=(6, 6)으로 고정할 것.** (정사각형 비율 유지)
                    - **한글 깨짐 방지를 위해 반드시 영어(English)로 텍스트 출력.**
                    - **그래프 제목 폰트 크기: 16, 내부 텍스트: 12.**
                    - 중요 포인트는 빨강/파랑 색상 활용.
                    
                    **[출력 포맷]**
                    #METHOD_1#
                    [1단계 제목]
                    - 설명...
                    $$수식$$
                    ---
                    [2단계 제목]
                    ...
                    #METHOD_2#
                    ...
                    #METHOD_3#
                    ...
                    #CODE#
                    ```python
                    def draw(method, step):
                        fig, ax = plt.subplots(figsize=(6, 6))
                        ax.set_title(f"Method {method} - Step {step}", fontsize=16)
                        return fig
                    ```
                    """
                    
                    response = model.generate_content([prompt, image])
                    st.session_state.analysis_result = response.text
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {e}")
                    st.write(traceback.format_exc())

# [상태 3] 분석 결과 표시 (좌: 풀이 / 우: 그래프)
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    try:
        parts = full_text.split("#CODE#")
        text_full = parts[0]
        code_part = parts[1] if len(parts) > 1 else ""
        
        methods = {}
        pattern = r"#METHOD_(\d)#(.*?)(?=#METHOD_|\Z)"
        matches = re.findall(pattern, text_full, re.DOTALL)
        for m_id, content in matches:
            methods[int(m_id)] = content.strip()
            
        code_match = re.search(r"```python(.*?)```", code_part, re.DOTALL)
        final_code = code_match.group(1).strip() if code_match else code_part.strip()
        
        # 화면 분할 (1.2 : 1 비율)
        col_left, col_right = st.columns([1.2, 1])
        
        # === [왼쪽 패널: 풀이 설명] ===
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
            
            if method_id in methods:
                steps_raw = methods[method_id].split("---")
                steps = [s.strip() for s in steps_raw if s.strip()]
                
                for i, step_text in enumerate(steps):
                    lines = step_text.split('\n')
                    
                    # 1. [제목 수술] 화살표(arrow_down) 글씨를 빈칸으로 치환해서 삭제
                    raw_title = lines[0].strip()
                    # 정규식(re)을 사용해 arrow_down, 대괄호[], 밑줄(_) 등을 깨끗하게 지움
                    import re
                    clean_title = re.sub(r'(?i)(arrow_down|:arrow_down:|_|step|\[.*?\])', '', raw_title).strip()
                    
                    # 2. [본문 수술] 형광펜(백틱) 제거 + 2.png 스타일 수식 적용
                    body_lines = lines[1:]
                    body_text = '\n'.join(body_lines).strip()
                    
                    # ★ 핵심 마법: ` (백틱)을 $ (달러)로 바꿉니다.
                    # 이러면 '검은 박스'가 사라지고 -> '2.png 같은 예쁜 수식'으로 변합니다.
                    body_text = body_text.replace('`', '$')
                    
                    # [안전장치] 수식 렌더링이 깨지지 않게 $ 기호 앞뒤로 띄어쓰기를 줍니다.
                    body_text = body_text.replace('$', ' $ ') 
                    
                    # 화면 출력
                    with st.expander(f"STEP {i+1}: {clean_title}", expanded=True):
                        st.markdown(body_text)
                        
                        if st.button(f"📊 그래프 보기 (Step {i+1})", key=f"btn_{method_id}_{i}"):
                            st.session_state.step_index = i + 1
            else:
                st.warning("이 풀이 방법은 생성되지 않았습니다.")

        # === [오른쪽 패널: 그래프 시각화] ===
        with col_right:
            st.markdown(f"### 📐 시각화 (M{method_id}-S{st.session_state.step_index})")
            try:
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                exec(final_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"](method_id, st.session_state.step_index)
                    
                    # [그래프 사이즈 60% 고정]
                    # 1(여백) : 3(그래프) : 1(여백) 비율 = 전체 5중의 3 = 딱 60%
                    _, c_graph, _ = st.columns([1, 3, 1])
                    with c_graph:
                        st.pyplot(fig)
                else:
                    st.error("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                st.info("그래프를 생성하려면 왼쪽에서 단계를 선택하세요.")

    except Exception as e:
        st.error("결과 처리 중 오류가 발생했습니다.")
        st.write(e)