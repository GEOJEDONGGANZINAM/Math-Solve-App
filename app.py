import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (1호기의 필살 구출 작전)
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
    }
    
    /* [기존 유지] 기타 스타일 */
    .katex { font-size: 1.1em !important; color: inherit !important; }
    .stButton > button {
        border: 1px solid var(--default-textColor) !important;
        background-color: var(--background-color) !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important;
    }
    section[data-testid="stSidebar"] * {
         color: #ffffff !important;
    }
    
    /* ====================================================================
       [형님 구출 코드 v3] 스크롤 따라오기 - 'Inner Sticky' 기술
       ==================================================================== */
    
    /* 1. 최상위 스크롤 잠금 해제 (필수) */
    [data-testid="stAppViewContainer"] {
        overflow-y: scroll !important;
        overflow-x: hidden !important;
    }
    
    /* 2. 기둥들이 화면 끝까지 늘어나도록 둠 (Stretch 유지) */
    /* 이렇게 해야 '트랙'이 길게 형성되어 스크롤 할 공간이 생깁니다 */
    [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }

    /* 3. 오른쪽 기둥 자체가 아니라, 그 '내용물(알맹이)'을 고정시킴 */
    /* 표식(#sticky-target)을 가진 컬럼의 '첫 번째 자식 div'를 타겟팅 */
    div[data-testid="column"]:has(#sticky-target) > div {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 5rem !important; /* 상단 메뉴바 아래에 착 붙음 */
        z-index: 999 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 초기화 및 설정
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

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
        st.rerun()

# ==========================================
# 4. 메인 로직
# ==========================================
if not uploaded_file:
    st.info("👈 왼쪽 사이드바에서 문제 사진을 업로드하면 **즉시 풀이가 시작**됩니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🕵️‍♂️ 1타 강사가 문제를 분석하고 있습니다... 잠시만 기다려주세요."):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # [프롬프트] 글씨 겹침 해결 & 비율 고정 명령 강화
            prompt = """
            너는 대한민국 1타 수학 강사야. 이 문제를 학생에게 설명하듯이 **3가지 방식**으로 친절하고 명확하게 풀이해줘.

            **[작성 원칙]**
            1. **시작**: 서론, 인사말 절대 금지. **무조건 '# Method 1'로 시작해.**
            2. **구조**:
               - **# Method 1: 정석 풀이**
               - **# Method 2: 빠른 풀이**
               - **# Method 3: 직관 풀이**
            3. **형식**: LaTeX($...$) 사용, 개조식(-), 'Step' 단어 금지.

            **[그래프 코드 요청 - 형님을 위한 완벽한 그래프]**
            풀이 맨 마지막에 **반드시** 그래프를 그리는 Python 코드를 작성해.
            - 코드는 `#CODE_START#` 와 `#CODE_END#` 로 감싸줘.
            - 함수 이름: `def draw():` (인자 없음)
            
            **[그래프 필수 조건 - 절대 어기지 마]**
            1. **비율 고정**: 코드에 `ax.set_aspect('equal')`을 꼭 넣어서 정사각형 비율 유지.
            2. **크기**: `plt.figure(figsize=(6, 6))`
            3. **내용**: 문제의 **최종 정답 상태**를 그려.
            4. **[핵심] 글씨 겹침 방지 (Offset)**: 
               - 점의 좌표나 길이를 표시할 때 `plt.text(x, y, ...)`를 쓰되, **x, y 좌표에 +0.4 또는 -0.4 정도 오프셋**을 줘서 점이나 선이랑 겹치지 않게 해.
               - `ha='left'`, `va='bottom'` 등을 상황에 맞게 조절해.
            5. **글씨 크기**: 모든 텍스트는 `fontsize=9`로 통일.
            6. **영어 사용**: 한글 깨짐 방지를 위해 모든 텍스트는 영어로 작성.
            
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
    match = re.search(r'(#+\s*Method\s*1|\*{2}Method\s*1|Method\s*1:)', text_content, re.IGNORECASE)
    if match:
        text_content = text_content[match.start():]

    # [레이아웃 2:1]
    col_text, col_graph = st.columns([2, 1])
    
    with col_text:
        st.markdown(text_content)
        
    with col_graph:
        # [Sticky Target]
        st.markdown('<div id="sticky-target"></div>', unsafe_allow_html=True)
        
        # 제목
        st.markdown("### 📐 최종 시각화")
        
        if code_content:
            try:
                clean_code = code_content.replace("```python", "").replace("```", "").strip()
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                plt.close('all')
                exec(clean_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"]()
                    
                    # [핵심] use_container_width=False로 해야 강제 늘림 없이 
                    # figsize=(6,6) 크기(정사각형) 그대로 나옵니다.
                    st.pyplot(fig, use_container_width=False)
                else:
                    st.warning("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                st.error("그래프 생성 중 오류가 발생했습니다.")
                st.write(e)
        else:
            st.info("시각화 코드가 생성되지 않았습니다.")