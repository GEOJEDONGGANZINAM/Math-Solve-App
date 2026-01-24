import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (스크롤 따라오기 & 순정 모드)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기 - 순정")

st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* [핵심] 다크/라이트 모드 자동 대응 */
    
    /* 본문 텍스트 스타일 */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important;
        color: inherit !important;
        margin-bottom: 1em !important;
    }
    
    /* 수식 스타일 */
    .katex { font-size: 1.1em !important; color: inherit !important; }
    
    /* 헤더 스타일 */
    h1, h2, h3 {
        color: inherit !important;
        font-weight: 700 !important;
    }
    
    /* 버튼 스타일 */
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

    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important;
    }
    section[data-testid="stSidebar"] * {
         color: #ffffff !important;
    }
    
    /* [NEW] 스크롤 따라오기 (Sticky Graph) 강력 적용 */
    /* 1. 먼저 가로 컨테이너(Row)가 자식 높이를 꽉 채우지 않도록 설정 (stretch 방지) */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }
    
    /* 2. 두 번째 컬럼(오른쪽 그래프)을 화면 상단에 고정 */
    /* nth-of-type(2)는 가로 배치된 요소 중 두 번째(그래프 컬럼)를 뜻함 */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-of-type(2) {
        position: sticky !important;
        top: 3rem !important; /* 상단 여백 확보 */
        z-index: 999; /* 다른 요소보다 위에 보이도록 */
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
    # 파일 업로드 즉시 분석
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

# 이미지 로드
image = Image.open(uploaded_file)

# 분석 결과가 없으면 실행
if st.session_state.analysis_result is None:
    with st.spinner("🕵️‍♂️ 1타 강사가 문제를 분석하고 있습니다... 잠시만 기다려주세요."):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # [프롬프트 수정] 인사말 금지 및 Method 1 시작 강제
            prompt = """
            너는 대한민국 1타 수학 강사야. 이 문제를 학생에게 설명하듯이 **3가지 방식**으로 친절하고 명확하게 풀이해줘.

            **[작성 원칙]**
            1. **시작**: 서론, 인사말, 문제 요약 절대 하지 마. **무조건 '# Method 1'로 바로 시작해.**
            2. **가독성**: 줄글보다는 개조식(-)을 사용하고, 문단 간격을 넉넉히 둬.
            3. **수식**: 모든 수식은 LaTeX 형식($...$)을 사용해. (예: 함수 $f(x) = x^2$)
            4. **금지**: 'Step 1', '화살표 기호(arrow)', '백틱(`) 강조'는 절대 쓰지 마. **Bold**만 사용해.
            5. **구조**:
               - **Method 1: 정석 풀이** (논리적 서술)
               - **Method 2: 빠른 풀이** (실전 스킬)
               - **Method 3: 직관 풀이** (도형/그래프 해석)

            **[그래프 코드 요청]**
            풀이 맨 마지막에 **반드시** 그래프를 그리는 Python 코드를 작성해.
            - 코드는 `#CODE_START#` 와 `#CODE_END#` 로 감싸줘.
            - 함수 이름: `def draw(method):`
            - **[중요]** 각 Method의 '최종 결과(Final State)' 그래프 하나만 그려. (중간 과정 X)
            - `figsize=(6, 6)` 고정.
            - 한글 대신 영어 사용.
            
            자, 바로 Method 1부터 시작해.
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
    
    # 텍스트와 코드 분리
    text_content = full_text
    code_content = ""
    
    if "#CODE_START#" in full_text:
        parts = full_text.split("#CODE_START#")
        text_content = parts[0]
        
        if "#CODE_END#" in parts[1]:
            code_content = parts[1].split("#CODE_END#")[0]
            if len(parts[1].split("#CODE_END#")) > 1:
                text_content += parts[1].split("#CODE_END#")[1]

    # [세탁 1] 백틱, arrow 제거
    text_content = text_content.replace("`", "")
    text_content = text_content.replace("arrow_down", "")
    
    # [세탁 2] 인사말 강제 삭제 (Method 1 앞부분 날리기)
    # AI가 혹시라도 인사말을 넣었으면, 'Method 1' 글자 앞을 다 잘라버립니다.
    # # Method 1, ## Method 1, **Method 1 등 다양한 패턴 감지
    match = re.search(r'(#+\s*Method\s*1|\*{2}Method\s*1|Method\s*1:)', text_content, re.IGNORECASE)
    if match:
        text_content = text_content[match.start():]

    # ==========================================
    # 화면 레이아웃 (3:2 비율)
    # ==========================================
    # [요청 1 반영] 텍스트(3) : 그래프(2) 비율 (1.5 : 1)
    col_text, col_graph = st.columns([1.5, 1])
    
    with col_text:
        st.markdown("### 📝 1타 강사 풀이")
        st.markdown("---")
        st.markdown(text_content)
        
    with col_graph:
        # [요청 3 반영] 이 컬럼은 CSS에 의해 스크롤을 따라다닙니다(Sticky).
        st.markdown("### 📐 그래프 시각화")
        
        # 그래프 선택 버튼
        m1, m2, m3 = st.columns(3)
        if m1.button("Method 1"): st.session_state.graph_method = 1
        if m2.button("Method 2"): st.session_state.graph_method = 2
        if m3.button("Method 3"): st.session_state.graph_method = 3
        
        st.caption(f"현재 보여주는 그래프: Method {st.session_state.graph_method} (최종 결과)")

        # 코드 실행 및 그래프 그리기
        if code_content:
            try:
                clean_code = code_content.replace("```python", "").replace("```", "").strip()
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                plt.close('all')
                exec(clean_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"](st.session_state.graph_method)
                    st.pyplot(fig, use_container_width=True)
                else:
                    st.warning("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                st.error("그래프 생성 중 오류가 발생했습니다.")
                st.write(e)
        else:
            st.info("이 문제에 대한 시각화 코드가 생성되지 않았습니다.")