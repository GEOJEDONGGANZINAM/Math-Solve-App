import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import time

# ==========================================
# 0. 보안 시스템 (Gatekeeper)
# ==========================================
st.set_page_config(layout="wide", page_title="최승규 2호기 - 시크릿 모드")

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 로그인 화면
if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stTextInput > div > div > input { text-align: center; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 1호기 보안 시스템")
        st.write("승규형님 승인 코드 없이는 접근 불가합니다.")
        password = st.text_input("Access Code", type="password")
        
        if st.button("접속 승인 요청"):
            if password == "71140859":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("🚫 접근 거부: 코드가 일치하지 않습니다.")
    st.stop()

# ==========================================
# 1. 디자인 & 스타일 (Sticky Text Guide)
# ==========================================
st.markdown("""
<style>
    /* 폰트 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* 텍스트 스타일: 수학 문제집 해설 느낌 */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important;
        color: #333333 !important;
        margin-bottom: 0.8em !important;
    }
    
    /* 제목 스타일 */
    h1, h2, h3 {
        font-weight: 700 !important;
        color: #000000 !important;
        margin-top: 1.2em !important;
    }
    
    /* 수식 폰트 */
    .katex { font-size: 1.15em !important; }
    
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] { background-color: #00C4B4 !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }

    /* ====================================================================
       [Sticky 기능] 오른쪽 가이드가 스크롤 따라오게 설정
       ==================================================================== */
    [data-testid="stHorizontalBlock"] { align-items: flex-start !important; }

    /* #sticky-guide 아이디를 가진 박스를 고정 */
    div[data-testid="column"]:has(#sticky-guide) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 5rem !important;
        z-index: 1000 !important;
        height: fit-content !important;
        display: block !important;
    }
    
    /* 가이드 박스 디자인 */
    .guide-box {
        background-color: #f8f9fa;
        border-left: 5px solid #00C4B4;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
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
    # [설정] 창의성 0.0 -> 기계적인 검증 모드
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("⚠️ API 키 설정이 필요합니다.")

# ==========================================
# 3. 사이드바 (입력)
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.caption("Ver. Agentic Protocol")
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 사진 업로드", type=["jpg", "png", "jpeg"], key="problem_uploader")
    
    st.markdown("---")
    if st.button("🔄 초기화"):
        st.session_state.analysis_result = None
        st.rerun()

# ==========================================
# 4. 메인 로직 (5단계 검증 프로토콜 적용)
# ==========================================
if not uploaded_file:
    st.info("👈 문제 사진을 업로드하면 **'5단계 검증 프로토콜'**이 시작됩니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🔄 [Phase 1~4] 분석, 검증, 해결책 도출 중..."):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            
            # [형님이 지시한 5단계 검증 프로토콜 프롬프트]
            prompt = """
            너는 대한민국 최고의 수학 연구소의 '검증된 AI 조교'다. 
            단순히 답만 내지 말고, 아래의 **[5단계 검증 프로토콜]**을 내부적으로 거친 뒤, 최종 결과물만 출력해라.

            **[내부 사고 과정 (Internal Protocol)]**
            1. **Phase 1 (정보 수집)**: 문제의 조건, 그래프 개형, 수식 정보를 빠짐없이 스캔한다.
            2. **Phase 2 (초안 작성)**: 3가지 방식(정석, 빠른, 직관)으로 풀이 전략을 세운다.
            3. **Phase 3 (가설 검증)**: 세운 식과 답이 논리적 모순이 없는지 역산하여 확인한다.
            4. **Phase 4 (해결책 도출)**: 검증된 풀이를 **'수학 문제집 해설지 스타일'**로 정제한다.
            5. **Phase 5 (유효성 확인)**: 학생이 이 풀이를 보고 이해할 수 있는지 최종 점검한다.

            **[최종 출력 형식 (엄수)]**
            출력은 반드시 **두 부분**으로 나누어야 한다. 두 부분 사이에는 `|||SPLIT|||` 이라는 구분자를 넣어라.

            **[Part 1: 문제 해설]**
            - **스타일**: 블로그 글처럼 주저리주저리 쓰지 말고, **'수학 문제집 정답과 풀이'** 섹션처럼 깔끔하고 건조하게 작성해.
            - **구성**:
              1. **[정석 풀이]**: 논리적 서술 (교과서적 접근)
              2. **[빠른 풀이]**: 실전 스킬 위주
              3. **[직관 풀이]**: 그래프/기하적 해석
            - **가독성**: 
              - 문단 나눌 때 확실하게 나누고, 중요 수식은 별도 줄에 작성.
              - 분수는 `\\dfrac` 사용.
            
            `|||SPLIT|||`

            **[Part 2: 그래프 작도 가이드]**
            - **역할**: 학생이 연습장에 직접 그래프를 그릴 수 있도록 **말로 설명하는 가이드**다. 코드를 짜지 마.
            - **말투**: "~하세요.", "~찍으세요." 같은 지시형.
            - **내용**:
              1. x축, y축 그리기 범위 설정.
              2. 주요 함수($y=...$)를 어떻게 그리는지 설명 (증가/감소, 점근선 등).
              3. 핵심 점(A, B 등)의 대략적 위치 지정.
              4. 보조선을 어디에 그어야 하는지 지시.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.analysis_result = response.text
            st.rerun()
            
        except Exception as e:
            st.error(f"프로토콜 실행 중 오류 발생: {e}")
            st.stop()

# ==========================================
# 5. 결과 화면 (좌: 해설 / 우: Sticky 가이드)
# ==========================================
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    # 구분자로 텍스트 분리
    if "|||SPLIT|||" in full_text:
        parts = full_text.split("|||SPLIT|||")
        solution_text = parts[0].strip()
        guide_text = parts[1].strip()
    else:
        solution_text = full_text
        guide_text = "그래프 가이드 생성에 실패했습니다."

    # [레이아웃 2:1]
    col_text, col_guide = st.columns([2, 1])
    
    # 왼쪽: 문제 해설
    with col_text:
        st.markdown(solution_text)
        
    # 오른쪽: Sticky 그래프 가이드
    with col_guide:
        # [Sticky Target] CSS가 이 ID를 잡습니다.
        st.markdown('<div id="sticky-guide"></div>', unsafe_allow_html=True)
        
        # 가이드 박스 디자인 적용
        st.markdown(f"""
        <div class="guide-box">
            <h3 style="margin-top:0;">📝 그래프 작도 가이드</h3>
            <p style="font-size:14px; color:#666;">
                이 가이드를 보고 연습장에 직접 그래프를 그려보세요.<br>
                직접 그려야 실력이 늡니다.
            </p>
            <hr>
            {guide_text.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)