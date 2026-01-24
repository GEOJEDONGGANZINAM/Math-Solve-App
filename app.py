import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (심플 순정 모드)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기")

st.markdown("""
<style>
    /* 폰트 설정 (유지) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* [핵심 수정] 배경색/글자색 강제 고정 제거 */
    /* 기존의 .stApp { background-color: #ffffff !important; } 같은 코드를 삭제하여
       스트림릿이 알아서 다크/라이트 모드를 판단하게 합니다. */
    
    /* 본문 텍스트 스타일 */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important;
        /* color: #1a1a1a !important;  <-- 삭제: 테마에 따라 자동 적용 */
        color: inherit !important; /* 부모 요소(배경)의 색상에 맞춰 자동 조절 */
        margin-bottom: 1em !important;
    }
    
    /* 수식 스타일 */
    .katex { font-size: 1.1em !important; color: inherit !important; }
    
    /* 헤더 스타일 */
    h1, h2, h3 {
        /* color: #000000 !important; <-- 삭제 */
        color: inherit !important; /* 테마에 맞게 자동 조절 */
        font-weight: 700 !important;
    }
    
    /* 버튼 스타일 (테마 반응형으로 수정) */
    .stButton > button {
        border-radius: 8px;
        /* 테두리, 배경, 글자색을 테마 변수로 변경 */
        border: 1px solid var(--default-textColor) !important;
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        transition: all 0.2s ease;
    }
    /* 버튼 호버 효과 (사이드바 포인트 컬러 활용) */
    .stButton > button:hover {
        border-color: #00C4B4 !important;
        color: #00C4B4 !important;
    }

    /* (선택사항) 사이드바는 포인트 컬러라 유지하거나, 원하시면 테마를 따르게 바꿀 수 있습니다. 
       현재는 기존 포인트 컬러(청록색) 배경에 흰 글씨를 유지합니다. */
    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important;
    }
    section[data-testid="stSidebar"] * {
         color: #ffffff !important;
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
    # 스트림릿 시크릿에서 키를 가져옵니다.
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바 (입력)
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.caption("여러분들 검색할 때마다 내 돈은 감소중")
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"])
    
    st.markdown("---")
    if st.button("🔄 새로운 문제 풀기 (Reset)"):
        st.session_state.analysis_result = None
        st.session_state.graph_method = 1
        st.rerun()

# ==========================================
# 4. 메인 로직
# ==========================================
if not uploaded_file:
    st.info("👈 왼쪽에서 문제 사진을 업로드하면 바로 풀이가 시작됩니다.")
    st.stop()

# 이미지 로드
image = Image.open(uploaded_file)

# 분석 요청 (결과가 없으면 실행)
if st.session_state.analysis_result is None:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(image, caption="업로드된 문제", use_container_width=True)
    with c2:
        if st.button("🚀 최승규의 풀이 시작", type="primary"):
            with st.spinner("열심히 푸는중 조금만 기다려라"):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # [프롬프트] 순정 모드 요청
                    prompt = """
                    너는 대한민국 1타 수학 강사야. 이 문제를 학생에게 설명하듯이 **3가지 방식**으로 친절하고 명확하게 풀이해줘.

                    **[작성 원칙]**
                    1. **가독성**: 줄글보다는 개조식(-)을 사용하고, 문단 간격을 넉넉히 둬.
                    2. **수식**: 모든 수식은 LaTeX 형식($...$)을 사용해. (예: 함수 $f(x) = x^2$)
                    3. **금지**: 'Step 1', '화살표 기호(arrow)', '백틱(`) 강조'는 절대 쓰지 마. **Bold**만 사용해.
                    4. **구조**:
                       - **Method 1: 정석 풀이** (논리적 서술)
                       - **Method 2: 빠른 풀이** (실전 스킬)
                       - **Method 3: 직관 풀이** (도형/그래프 해석)

                    **[그래프 코드 요청]**
                    풀이 맨 마지막에 **반드시** 그래프를 그리는 Python 코드를 작성해.
                    - 코드는 `#CODE_START#` 와 `#CODE_END#` 라는 단어로 감싸줘. (이건 내가 분리해서 실행할 거야)
                    - 함수 이름: `def draw(method):` (method 번호를 받아서 해당 그래프를 그림)
                    - `figsize=(6, 6)` 고정.
                    - 한글 대신 영어 사용.
                    
                    자, 이제 풀이를 시작해.
                    """
                    
                    response = model.generate_content([prompt, image])
                    st.session_state.analysis_result = response.text
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")

# ==========================================
# 5. 결과 화면 (순정 모드 출력)
# ==========================================
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    # 1. 텍스트와 코드 분리
    text_content = full_text
    code_content = ""
    
    if "#CODE_START#" in full_text:
        parts = full_text.split("#CODE_START#")
        text_content = parts[0] # 설명 부분
        
        if "#CODE_END#" in parts[1]:
            code_content = parts[1].split("#CODE_END#")[0] # 코드 부분
            # 코드 뒤에 설명이 더 있다면 붙이기
            if len(parts[1].split("#CODE_END#")) > 1:
                text_content += parts[1].split("#CODE_END#")[1]

    # [최소한의 세탁] 백틱(`)과 arrow_down 텍스트만 제거
    text_content = text_content.replace("`", "")
    text_content = text_content.replace("arrow_down", "")

    # ==========================================
    # 화면 레이아웃
    # ==========================================
    col_text, col_graph = st.columns([1.2, 1])
    
    with col_text:
        st.markdown("### 📝 최승규의 풀이")
        st.markdown("---")
        # 제미나이 답변 그대로 출력
        st.markdown(text_content)
        
    with col_graph:
        st.markdown("### 📐 그래프 시각화")
        
        # 그래프 선택 버튼
        m1, m2, m3 = st.columns(3)
        if m1.button("Method 1"): st.session_state.graph_method = 1
        if m2.button("Method 2"): st.session_state.graph_method = 2
        if m3.button("Method 3"): st.session_state.graph_method = 3
        
        st.caption(f"현재 보여주는 그래프: Method {st.session_state.graph_method}")

        # 코드 실행 및 그래프 그리기
        if code_content:
            try:
                # 코드 정리
                clean_code = code_content.replace("```python", "").replace("```", "").strip()
                
                # 실행 환경
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                plt.close('all')
                exec(clean_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"](st.session_state.graph_method)
                    st.pyplot(fig)
                else:
                    st.warning("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                st.error("그래프 생성 중 오류가 발생했습니다.")
                st.write(e) # 구체적인 에러 내용 표시
        else:
            st.info("이 문제에 대한 시각화 코드가 생성되지 않았습니다.")