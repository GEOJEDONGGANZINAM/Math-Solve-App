import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (형님이 주신 코드 100% 유지)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기")

st.markdown("""
<style>
    /* 폰트 설정 (유지) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* 텍스트 스타일 (유지) */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important;
        color: inherit !important;
        margin-bottom: 1em !important;
    }
    
    /* 제목 스타일 (유지) */
    h1, h2, h3 {
        font-size: 20px !important; 
        font-weight: 700 !important;
        color: inherit !important;
        margin-top: 1.5em !important;
        margin-bottom: 0.5em !important;
    }
    
    /* 수식 폰트 크기 (형님이 원하신 1.1em 적용) */
    .katex { 
        font-size: 1.1em !important; 
        line-height: 1.5 !important;
        color: inherit !important; 
    }
    
    section[data-testid="stSidebar"] { background-color: #00C4B4 !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }

    /* ====================================================================
       [형님이 주신 완벽한 스크롤 고정 CSS]
       ==================================================================== */
    
    /* 1. 강제 스크롤 설정 삭제됨 (유지) */

    /* 2. 가로 컨테이너가 자식 높이를 억지로 늘리지 않게 함 (필수 유지) */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* 3. Sticky 타겟 설정 (유지) */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(#sticky-anchor),
    div[data-testid="stVerticalBlock"]:has(#sticky-anchor),
    div[data-testid="column"]:has(#sticky-anchor),
    div[data-testid="stColumn"]:has(#sticky-anchor) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 5rem !important; /* 상단 메뉴바 아래에 고정 */
        z-index: 1000 !important;
        
        height: fit-content !important;
        align-self: flex-start !important; 
        display: block !important;
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
            
            # [수정 1] 본문 줄바꿈 강제 명령 추가
            prompt = """
            너는 대한민국 1타 수학 강사야. 이 문제를 학생에게 설명하듯이 **3가지 방식**으로 친절하고 명확하게 풀이해줘.

            **[작성 원칙]**
            1. **시작**: 서론, 인사말 절대 금지. **무조건 '# Method 1: 정석 풀이'로 시작해.**
            2. **구조 (제목 정확히 준수)**:
               - **# Method 1: 정석 풀이**
               - **# Method 2: 빠른 풀이**
               - **# Method 3: 직관 풀이**
            3. **형식**: 
               - LaTeX($...$) 사용.
               - **[핵심] 분수는 무조건 `\\dfrac` (Display Fraction) 사용.** (글씨 크게)
               - 개조식(-), 'Step' 단어 금지.
            4. **[줄바꿈 필수 - 매우 중요]**: 
               - 가독성을 위해 **모든 문장이 끝날 때마다(마침표 뒤) 무조건 줄바꿈**을 해. 
               - 절대 문장을 옆으로 이어서 쓰지 마. (엔터 두 번 쳐서 간격 벌려도 좋아)

            **[그래프 코드 요청 - 오류 절대 금지]**
            풀이 맨 마지막에 **반드시** 그래프를 그리는 Python 코드를 작성해.
            - 코드는 `#CODE_START#` 와 `#CODE_END#` 로 감싸줘.
            - 함수 이름: `def draw():` (인자 없음)
            
            **[Python 코드 작성 시 절대 주의사항]**
            1. **[ValueError 방지]**: Numpy 배열을 `if array:` 조건문에 바로 쓰지 마. 
               - 반드시 `if array.size > 0:` 또는 `if len(array) > 0:` 사용.
            2. **비율 고정**: `ax.set_aspect('equal')` 필수.
            3. **크기**: `plt.figure(figsize=(6, 6))`
            4. **식 표시**: 그래프 식은 범례 대신 선 근처에 텍스트로 표시 (Offset 사용).
            5. **글씨 크기**: `fontsize=9` 통일.
            6. **언어**: 영어(English)만 사용.
            
            자, 바로 # Method 1: 정석 풀이부터 시작해.
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
    # Method 1 앞의 잡설 제거 (정규식)
    match = re.search(r'(#+\s*Method\s*1.*)', text_content, re.IGNORECASE)
    if match:
        text_content = text_content[match.start():]

    # [레이아웃 2:1]
    col_text, col_graph = st.columns([2, 1])
    
    with col_text:
        st.markdown(text_content)
        
    with col_graph:
        # [핵심] Sticky Anchor 심기 (CSS가 이 ID를 찾아서 고정함)
        st.markdown('<div id="sticky-anchor"></div>', unsafe_allow_html=True)
        
        st.markdown("### 📐 최종 시각화")
        
        if code_content:
            try:
                clean_code = code_content.replace("```python", "").replace("```", "").strip()
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                plt.close('all')
                exec(clean_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"]()
                    # [수정 2] 그래프 크기 원상복구 (1.png처럼 꽉 차게)
                    # use_container_width=True로 변경하여 컬럼 너비에 맞춤
                    st.pyplot(fig, use_container_width=True)
                else:
                    st.warning("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                # 에러 메시지를 좀 더 부드럽게 출력
                st.error("그래프 생성 중 코드가 꼬였습니다. 다시 시도해주세요.")
                st.write(e)
        else:
            st.info("시각화 코드가 생성되지 않았습니다.")