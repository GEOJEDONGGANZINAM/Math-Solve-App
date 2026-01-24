import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (최승규 2호기 전용)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기")

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
        background-color: transparent !important; /* 배경색 투명 강제 */
    }
    /* 선택된 라디오 버튼 텍스트의 형광펜도 제거 */
    div[data-testid="stRadio"] div[role="radiogroup"] > div > label[data-baseweb="radio"] > div:last-child > p {
        background-color: transparent !important;
        color: #000000 !important;
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
    
    /* 앱 초기화 버튼 스타일링 */
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

    .streamlit-expanderContent p, .streamlit-expanderContent li {
        line-height: 1.7 !important; /* 줄간격 170% */
        margin-bottom: 1.2em !important; /* 문단 아래 여백 추가 */
    }
    /* 수식($$)이 있는 문단의 간격 조정 */
    .katex-display {
        margin: 1.5em 0 !important;
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
    st.title("최승규 2호기")
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
                    # [최종 확정] 무조건 Gemini 2.5 Flash 사용. 딴 거 안 씀.
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    prompt = """
                    너는 대한민국 1타 수학 강사야. 이 문제를 **3가지 방식**으로 풀이해.

                    **[제 1원칙: 절대 금지 사항 (Strict Rules)]**
                    1. **화살표 금지**: 텍스트에 `arrow_down`, `↓`, `->` 등 화살표를 뜻하는 어떤 기호나 단어도 쓰지 마.
                    2. **형광/코드블록 금지**: 백틱(`)이나 코드블록(```)을 텍스트 강조용으로 쓰지 마. 오직 **Bold**만 사용.
                    3. **단계 명시 금지**: 제목에 'Step 1', '1단계'라고 쓰지 마. (시스템이 자동으로 붙임)

                    **[제 2원칙: 형식 및 가독성]**
                    1. **수식 필수**: 모든 수식, 변수, 숫자는 무조건 LaTeX 포맷($...$)을 사용. (예: $f(x) = x^2$)
                    2. **개조식**: 문장은 `-` 로 시작.
                    3. **구분선 필수**: 단계(Step)가 끝날 때마다 반드시 `---` 만 있는 줄을 넣어.

                    **[풀이 구성]**
                    - Method 1: **정석 풀이** (논리적 서술)
                    - Method 2: **빠른 풀이** (실전 스킬)
                    - Method 3: **직관 풀이** (도형/그래프 해석)

                    **[시각화 코드 규칙 (엄수)]**
                    - `def draw(method, step):` 작성.
                    - **figsize=(6, 6)으로 고정할 것.** (절대 다른 사이즈로 변경 금지)
                    - **축 끝에 화살표 그리기 금지.** (단순 선만 사용)
                    - **한글 깨짐 방지를 위해 반드시 영어(English)로 텍스트 출력.**

                    **[출력 포맷 예시]**
                    #METHOD_1#
                    제목 (예: 점 A, B의 좌표 설정)
                    - 설명...
                    $$수식$$
                    ---
                    제목 (예: 두 번째 단계)
                    - 설명...
                    ---
                    ...
                    #METHOD_2#
                    ...
                    #METHOD_3#
                    ...
                    #CODE#
                    ```python
                    import matplotlib.pyplot as plt
                    import matplotlib.patches as patches
                    import numpy as np

                    def draw(method, step):
                        # [중요] 사이즈는 무조건 (6, 6)으로 고정
                        fig, ax = plt.subplots(figsize=(6, 6))
                        ax.set_title(f"Method {method} - Step {step}", fontsize=16)
                        # ... 그래프 그리는 코드 ...
                        return fig
                    ```
                    """
                    
                    response = model.generate_content([prompt, image])
                    st.session_state.analysis_result = response.text
                    st.rerun()
                    
                except Exception as e:
                    # 429 에러(과속) 발생 시 경고
                    if "429" in str(e):
                        st.error("🚨 구글 무료 서버 사용량이 꽉 찼습니다. (1분당 20회 제한)")
                        st.warning("약 1분 정도만 기다렸다가 다시 버튼을 눌러주세요!")
                    else:
                        st.error(f"분석 중 오류가 발생했습니다: {e}")
                        st.write(traceback.format_exc())

# [상태 3] 분석 결과 표시
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
                # 1. 원본 텍스트 가져오기
                raw_full_text = methods[method_id]

                # ==========================================================
                # [세탁기 가동] 형님, 여기서 문자열 자체를 조져버립니다.
                # ==========================================================
                
                # 1. [형광펜(백틱) 삭제]
                # 문장 전체에서 백틱(`) 기호를 아예 없애버립니다. (형광이 생길 수가 없음)
                cleaned_text = raw_full_text.replace("`", "").replace("```", "")

                # 2. [Arrow 삭제] 정규식 강화
                # .arrow_down, _arrow, arrow_down, :arrow: 등 모든 변종 패턴 삭제
                # (?i) : 대소문자 무시
                # [\.\s#_:-]* : 앞에 붙은 점(.), 공백, 샵, 언더바, 콜론 등 특수문자
                # arrow : 핵심 단어
                # [\w_-]* : 뒤에 붙는 글자들 (down, up, style 등)
                arrow_pattern = r'(?i)([\.\s#_:-]*arrow[\w_-]*[\.\s#_:-]*|[↓→])'
                cleaned_text = re.sub(arrow_pattern, '', cleaned_text)

                # 3. [잡동사니 삭제] 제목에 들어가는 대괄호 찌꺼기 등
                cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text)

                # ==========================================================

                # 2. 깨끗해진 텍스트를 단계(---)별로 분리
                steps_raw = cleaned_text.split("---")
                steps = [s.strip() for s in steps_raw if s.strip()]
                
                for i, step_text in enumerate(steps):
                    lines = step_text.split('\n')
                    
                    # 제목과 본문 분리
                    raw_title = lines[0].strip()
                    # 제목이 비었거나 이상하면 기본값
                    if not raw_title or len(raw_title) < 2: 
                        raw_title = "풀이 과정 및 해석"
                    
                    # 본문 합치기
                    body_lines = lines[1:]
                    body_text = '\n'.join(body_lines).strip()
                    
                    # [최종 확인 사살] 제목/본문에 혹시 남은 찌꺼기 제거
                    clean_title = raw_title.replace("step", "").replace("Step", "").strip()
                    
                    # [수식 보정] LaTeX($) 렌더링을 위해 $ 앞뒤에 공백 강제 주입
                    # (이게 없으면 수식이 텍스트랑 붙어서 깨져 보임)
                    body_text = re.sub(r'(?<!\$)\$(?!\$)', ' $ ', body_text)
                    
                    # UI 출력
                    with st.expander(f"STEP {i+1}: {clean_title}", expanded=True):
                        st.markdown(body_text)
                        
                        # 그래프 버튼
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
                    
                    # [그래프 사이즈 고정] 중앙 정렬
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