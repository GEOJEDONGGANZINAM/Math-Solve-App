import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 0. 기본 설정 & 보안 시스템
# ==========================================
st.set_page_config(layout="centered", page_title="최승규 2호기 - Gemini 3.0 Only")

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# [보안] 로그인 화면
if not st.session_state.authenticated:
    st.markdown("<br><br><h2 style='text-align: center; color: white;'>🔒 접근 승인 요청</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Access Code", type="password", label_visibility="collapsed", placeholder="비밀번호 입력")
        if st.button("Login", use_container_width=True):
            if password == "71140859": 
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("🚫 접근 거부")
    st.stop()

# ==========================================
# 1. 디자인 & 스타일 (제미나이 원본 '맛' 살리기)
# ==========================================
st.markdown("""
<style>
    /* 폰트: 프리텐다드 (구글 산스와 가장 유사한 고품질 폰트) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }
    
    /* [배경] 리얼 블랙 (#131314) */
    .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }
    
    /* [가독성] 줄간격과 폰트 크기 조정 (11.png 처럼 빽빽하지 않게) */
    .stMarkdown p, .stMarkdown li {
        font-size: 16px !important;
        line-height: 1.8 !important; /* 줄간격 넓힘 */
        color: #e3e3e3 !important;
        margin-bottom: 0.8em !important;
    }
    
    /* 제목 스타일 (흰색 강조) */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        margin-top: 1.5em !important;
        margin-bottom: 1em !important;
    }
    
    /* [수식] LaTeX 완전 흰색 & 크기 조정 */
    .katex {
        font-size: 1.15em !important;
        color: #ffffff !important; 
    }
    
    /* 강조 구문 (Bold) 색상 */
    strong {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] { background-color: #00C4B4 !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* 버튼 */
    div.stButton > button {
        background-color: #333333;
        color: white;
        border: 1px solid #555555;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 설정 및 [형님 명령] 3.0 Pro 강제 선택 로직
# ==========================================
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

target_model = None

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # [형님 명령] 3.0 Pro 계열만 찾아내는 필터
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 우선순위 1: 3.0 Pro Preview (현재 사용 가능)
    # 우선순위 2: 3.0 Pro (미래에 출시될 정식 버전)
    for m in all_models:
        if 'gemini-3-pro-preview' in m: # 3-pro-preview
            target_model = m
            break
        if 'gemini-3.0-pro' in m: # 3.0-pro
            target_model = m
            break
            
except Exception as e:
    st.sidebar.error("⚠️ API 키 오류")
    st.stop()

# ==========================================
# 3. 사이드바 (모델 상태 표시)
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.markdown("---")
    
    if target_model:
        st.success(f"✅ **{target_model}**\n\n모델이 고정되었습니다.")
    else:
        st.error("🚫 **3.0 Pro 모델 없음**\n\n형님 계정에서 3.0 모델을 찾을 수 없습니다.")
        st.stop() # 3.0 없으면 아예 작동 중지 (형님 명령)
        
    st.markdown("---")
    uploaded_file = st.file_uploader("문제 업로드", type=["jpg", "png", "jpeg"], key="problem_uploader")
    
    st.markdown("---")
    if st.button("🔄 초기화 (Reset)"):
        st.session_state.analysis_result = None
        st.rerun()

# ==========================================
# 4. 메인 로직
# ==========================================
if not uploaded_file:
    st.info(f"👈 문제 사진을 올려주세요. **Gemini 3.0 Pro**가 대기 중입니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🧠 **Gemini 3.0 Pro 가동 중... (1타 강사 빙의)**"):
        try:
            # 설정: 창의성 0.0 (기계적 정확함)
            generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
            
            # 모델 로딩
            model = genai.GenerativeModel(target_model, generation_config=generation_config)
            
            # [프롬프트 대수술] 원본 1.png ~ 6.png 스타일 강제 주입
            prompt = """
            너는 대한민국 수능 수학 1타 강사야. 
            주어진 문제를 **반드시 아래 가이드라인에 맞춰서** 풀이해.
            형식은 제미나이 웹사이트의 깔끔한 출력 방식을 완벽하게 따라해야 해.

            **[1. 제목 및 구조 (Header Style)]**
            * 각 풀이 방법은 `### Method 1: ...` (헤더 3)를 사용하여 굵고 크게 표시해.
            * 제목에는 반드시 **핵심 수학 개념**을 포함해.
              * 예: **### Method 1: 차함수와 인수정리 활용 (정석 & 추천)**
              * 예: **### Method 2: 비율 관계를 이용한 빠른 풀이**

            **[2. 본문 서술 방식 (Bullet Points)]**
            * 줄글로 길게 늘어쓰지 마. (가독성 떨어짐)
            * **반드시 `Step` 별로 나누고, 그 안에서 `글머리 기호(Bullet point)`를 사용해.**
            * 예시:
              **Step 1: 조건 해석**
              * 조건 (가)에 따르면 $f(x)$는...
              * 따라서 그래프의 개형은...
            
            **[3. 수식 표현 (LaTeX Layout)]**
            * 문장 중간의 변수나 간단한 식은 `$ f(x) $` 와 같이 인라인으로 써.
            * **계산 과정, 중요 방정식, 최종 정답은 반드시 `$$ ... $$` (Display Math)를 써서 별도 줄에 중앙 정렬해.**
            * 분수는 무조건 `\\dfrac`을 사용해서 크게 보여줘.
            * 수식 위아래로 빈 줄을 하나씩 둬서 시원시원하게 보이게 해.

            **[4. 내용 검증]**
            * 풀이는 논리적 비약 없이 정확해야 해.
            * 그래프를 그리는 코드는 작성하지 마. (텍스트로만 설명)
            * 최종 정답은 마지막에 확실하게 명시해.
            """
            
            response = model.generate_content([prompt, image])
            st.session_state.analysis_result = response.text
            st.rerun()
            
        except Exception as e:
            st.error(f"⚠️ **오류 발생**: {e}")
            st.stop()

# ==========================================
# 5. 결과 화면
# ==========================================
if st.session_state.analysis_result:
    st.markdown(st.session_state.analysis_result)