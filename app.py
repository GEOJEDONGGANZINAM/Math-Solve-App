import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (1호기의 필사적인 수정)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기 - 순정")

st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* [기존 유지] 텍스트 스타일 */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important;
        color: inherit !important;
        margin-bottom: 1em !important;
    }
    
    /* [기존 유지] 제목 스타일 (20px, Bold) */
    h1, h2, h3 {
        font-size: 20px !important; 
        font-weight: 700 !important;
        color: inherit !important;
        margin-top: 1.5em !important;
        margin-bottom: 0.5em !important;
        letter-spacing: -0.5px !important;
    }
    
    /* [기존 유지] 기타 스타일 */
    .katex { font-size: 1.1em !important; color: inherit !important; }
    
    .stButton > button {
        border-radius: 8px;
        border: 1px solid var(--default-textColor) !important;
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #00C4B4 !important;
        color: #00C4B4 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important;
    }
    section[data-testid="stSidebar"] * {
         color: #ffffff !important;
    }
    
    /* ====================================================================
       [형님 구출 코드 v2] 스크롤 따라오기 (Sticky) - 잠금 완전 해제
       ==================================================================== */
    
    /* 1. 최상위 컨테이너의 스크롤 잠금 해제 (이게 막혀있으면 sticky가 안됩니다) */
    [data-testid="stAppViewContainer"] {
        overflow-y: scroll !important;
        overflow-x: hidden !important;
    }
    [data-testid="stMainBlock"] {
        overflow: visible !important;
    }
    
    /* 2. 가로 배치 컨테이너가 자식 높이를 억지로 늘리지 못하게 함 (필수) */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* 3. 'sticky-target' 표식이 있는 오른쪽 컬럼을 타겟팅 */
    /* top: 5rem은 화면 상단 메뉴바를 피해서 고정하는 위치입니다 */
    div[data-testid="column"]:has(#sticky-target) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 5rem !important; 
        
        /* [핵심] 높이를 내용물만큼만 잡아야 움직일 공간이 생김 */
        height: fit-content !important; 
        
        z-index: 999 !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 초기화 및 설정
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'graph_method' not in st.session_state:
    st.session_state.graph_method = 1  # 기본값 Method 1

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바 (입력)
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.caption("Pure Gemini Mode")
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"], key="problem_uploader")
    
    st.markdown("---")
    if st.button("🔄 새로운 문제 풀기 (Reset)"):
        st.session_state.analysis_result = None
        st.session_state.graph_method = 1
        st.rerun()

# ==========================================
# 4. 메인 로직 (자동 분석 시작)
# ==========================================
if not uploaded_file:
    st.info("👈 왼쪽 사이드바에서 문제 사진을 업로드하면 **즉시 풀이가 시작**됩니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🕵️‍♂️ 1타 강사가 문제를 분석하고 있습니다... 잠시만 기다려주세요."):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # [프롬프트 수정] 비율 고정(equal) & 길이 표시 & 겹침 방지
            prompt = """
            너는 대한민국 1타 수학 강사야. 이 문제를 학생에게 설명하듯이 **3가지 방식**으로 친절하고 명확하게 풀이해줘.

            **[작성 원칙]**
            1. **시작**: 서론, 인사말, 문제 요약 절대 하지 마. **무조건 '# Method 1'로 바로 시작해.** (반드시 # 하나만 써서 제목으로 만들어)
            2. **가독성**: 줄글보다는 개조식(-)을 사용하고, 문단 간격을 넉넉히 둬.
            3. **수식**: 모든 수식은 LaTeX 형식($...$)을 사용해. (예: 함수 $f(x) = x^2$)
            4. **금지**: 'Step 1', '화살표 기호(arrow)', '백틱(`) 강조'는 절대 쓰지 마. **Bold**만 사용해.
            5. **구조**:
               - **# Method 1: 정석 풀이** (논리적 서술)
               - **# Method 2: 빠른 풀이** (실전 스킬)
               - **# Method 3: 직관 풀이** (도형/그래프 해석)

            **[그래프 코드 요청 - 생명줄]**
            풀이 맨 마지막에 **반드시** 그래프를 그리는 Python 코드를 작성해.
            - 코드는 `#CODE_START#` 와 `#CODE_END#` 로 감싸줘.
            - 함수 이름: `def draw(method):`
            - **[중요 1]** 각 Method의 '최종 결과(Final State)' 그래프 하나만 그려. (중간 과정 X)
            - **[중요 2 - 비율 고정]**: 코드 안에 반드시 `ax.set_aspect('equal')`을 넣어서 그래프가 찌그러지거나 늘어나지 않게 정사각형 비율을 유지해.
            - **[중요 3 - 표현 규칙]**:
                - **좌표 및 식**: 주요 점과 함수 식을 표시해.
                - **길이 표시(필수)**: 선분의 길이(예: AB=8, BC=2루트2 등)를 계산해서 그래프 위에 텍스트로 꼭 표시해줘.
                - **글씨 겹침 방지**: `plt.text` 사용 시 `ha`, `va` 옵션과 좌표 오프셋(+0.2 등)을 조절해서 선이나 점과 글씨가 겹치지 않게 해.
            - **[중요 4 - 글씨 크기]**: 그래프 내부의 모든 텍스트는 **반드시 `fontsize=9`로 통일**해.
            - `figsize=(6, 6)` 고정.
            - 한글 대신 영어 사용.
            
            자, 바로 # Method 1부터 시작해.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.analysis_result = response.text
            st.rerun()
            
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {e}")
            st.stop()

# ==========================================
# 5. 결과 화면
# ==========================================
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    # 분리
    text_content = full_text
    code_content = ""
    
    if "#CODE_START#" in full_text:
        parts = full_text.split("#CODE_START#")
        text_content = parts[0]
        
        if "#CODE_END#" in parts[1]:
            code_content = parts[1].split("#CODE_END#")[0]
            if len(parts[1].split("#CODE_END#")) > 1:
                text_content += parts[1].split("#CODE_END#")[1]

    # 세탁
    text_content = text_content.replace("`", "")
    text_content = text_content.replace("arrow_down", "")
    
    # 인사말 제거
    match = re.search(r'(#+\s*Method\s*1|\*{2}Method\s*1|Method\s*1:)', text_content, re.IGNORECASE)
    if match:
        text_content = text_content[match.start():]

    # ==========================================
    # 화면 레이아웃 (2:1 비율 유지)
    # ==========================================
    col_text, col_graph = st.columns([2, 1])
    
    with col_text:
        st.markdown(text_content)
        
    with col_graph:
        # [핵심] 닻(Anchor) 심기 - CSS가 이놈을 찾아서 고정합니다.
        st.markdown('<div id="sticky-target"></div>', unsafe_allow_html=True)
        
        # [Sticky 적용됨]
        st.markdown("### 📐 그래프 시각화")
        
        m1, m2, m3 = st.columns(3)
        if m1.button("Method 1"): st.session_state.graph_method = 1
        if m2.button("Method 2"): st.session_state.graph_method = 2
        if m3.button("Method 3"): st.session_state.graph_method = 3
        
        st.caption(f"현재 보여주는 그래프: Method {st.session_state.graph_method} (최종 결과)")

        if code_content:
            try:
                clean_code = code_content.replace("```python", "").replace("```", "").strip()
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                plt.close('all')
                exec(clean_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"](st.session_state.graph_method)
                    # [수정] use_container_width=True를 쓰되, 
                    # 프롬프트에서 ax.set_aspect('equal')을 줬기 때문에 찌그러지지 않고 비율 유지됨
                    st.pyplot(fig, use_container_width=True)
                else:
                    st.warning("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                st.error("그래프 생성 중 오류가 발생했습니다.")
                st.write(e)
        else:
            st.info("이 문제에 대한 시각화 코드가 생성되지 않았습니다.")