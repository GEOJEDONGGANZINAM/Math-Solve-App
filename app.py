import streamlit as st
import google.generativeai as genai
from PIL import Image

import time # 시간차를 두기 위해 필요함

# ==========================================
# 0. 기본 설정 & 보안 시스템 (사모님 우대 에디션)
# ==========================================
st.set_page_config(layout="centered", page_title="최승규 2호기")

# [명단 관리]
# 사모님 아이디는 특별하게 관리합니다.
USER_DB = {
    "seungkyu": "951026",     # 형님 (관리자)
    "junhee": "8135",          # <--- [여기] 사모님 아이디 (바꾸세요)
    "student": "1234567", 
    "seungyun": "2512", 
    "seunghyun": "0450", 
    "chanmin": "0822", 
    "jiwoong": "8758", 
    "hyokyeong": "6972", 
    "chanwoo": "6763", 
    "donghan": "0977", 
    "minju": "6566", 
    "juyeon": "9396", 
    "wonjun": "2464", 
    "yeongmin": "2083", 
    "siyoun": "2965", 
    "siwan": "9724", 
    "hyungseok": "3189", 
    "mibunganueng": "7658", 
    "yena": "5000", 
    "nayoung": "2162", 
    "mystory0010": "5463", 
    "chaeyeon": "8326", 
    "jaeseong": "5334", 
    "soorin": "2604", 
    "kyoungjun": "2557", 
    "seongwon": "9382", 
    "dohyun": "0289", 
    "junhoo": "7524", 
    "dongwi": "8449", 
    "sungah": "8597", 
    "juyoung": "1275", 
    "sanghyeon": "3272", 
    "hyunsuk": "3505", 
    "yunji": "4079", 
    "juhyeong": "3913", 
    "seonyeong": "7499", 
    "haheun": "4665", 
    "minchan": "8386", 
    "hayoon": "3983", 
    "saerom": "5325", 
    "geunwoo": "9056", 
    "yeonwoo": "0659", 
    "eunsol": "8550", 
    "yeowon": "5696", 
    "student5": "1234", 
    "student6": "1234", 
    "student3": "1234", 
    "student5": "1234", 
    "student6": "1234", 
    "student5": "1234", 
    "student5": "1234", 
    "student6": "1234", 
    "student5": "1234", 
    "student5": "1234", 
    "student6": "1234", 
    "student5": "1234", 
    "student5": "1234", 
    "student6": "1234", 
    "student5": "1234", 
    "student6": "1234", 
    "student5": "1234", 
    "student6": "1234", 
}

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# [보안] 로그인 화면
if not st.session_state.authenticated:
    st.markdown("<br><br><h2 style='text-align: center; color: white;'>🔒 최승규 2호기</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        input_id = st.text_input("아이디 (ID)", placeholder="아이디 입력")
        input_pw = st.text_input("비밀번호 (PW)", type="password", placeholder="비밀번호 입력")
        
        if st.button("로그인 (Login)", use_container_width=True):
            if input_id in USER_DB and USER_DB[input_id] == input_pw:
                st.session_state.authenticated = True
                
                # [여기가 핵심] 자본주(사모님) 전용 환영식
                if input_id == "junhee": # 사모님 아이디라면?
                    st.balloons() # 🎈 화면 가득 풍선 날리기 (축포)
                    st.markdown("""
                    <div style='background-color: #FFD700; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                        <h3 style='color: #000000; margin: 0;'>👑 실질적 소유주님, 입장하십니다! 👑</h3>
                        <p style='color: #000000; margin: 0;'>예쁘고 똑똑한 마누라, 충성충성^^7</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.toast("🙇‍♀️ 주니쨔, 어서 오세용~ 대기 오지게 박고 있었습니다!")
                    time.sleep(3) # 사모님이 풍선 감상하실 시간 3초 드림
                    st.rerun()
                    
                else: # 형님이나 학생들 (일반인)
                    st.success(f"환영합니다, {input_id}님!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("🚫 접근 거부: 아이디 또는 비밀번호를 확인하세요.")
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
    st.caption("최승규T 스타일 문제풀이 사이트")
    st.caption("이해되지 않는 부분은 최승규T 에게")
    st.caption("질문 1회당 비용이 듭니다. 필요한 것만, 알차게 씁시다")
    st.markdown("---")
    
    if not target_model:
        st.error("🚫 **3.0 Pro 모델 없음**\n\n형님 계정에서 3.0 모델을 찾을 수 없습니다.")
        st.stop()
        
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
    st.info(f"👈 문제 사진을 올려주세요. **최승규 2호기**가 대기 중입니다.")
    st.stop()

image = Image.open(uploaded_file)

if st.session_state.analysis_result is None:
    with st.spinner("🧠 ***최승규 2호기* 가 문제를 푸는中**"):
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

            **[0. 절대 금지 및 필수 사항 (Start Rule)]**
              * **[필수] 풀이 방법은 무조건 2가지 이상 제시해.** (Method 1 하나만 쓰면 절대 안 됨. Method 2. Method 3까지 필수. Method 4 부터는 풀이 방법이 존재 할 경우 보여줄 것. 만약 어길 시, 제미나이 쓰지 않고 챗지피티 쓸 예정)
              * Method 1: 정석 풀이 (교과서적 개념)
              * Method 2: 실전/빠른 풀이 (공식, 그래프 성질 등)
            * 서론, 인사말, 분석 시작 멘트 전부 생략해.
            * **무조건 첫 줄은 '### Method 1: ...' 제목으로 시작해.**

            **[1. 제목 및 구조 (Header Style)]**
            * `### Method 1: [핵심 개념] (정석 풀이)`
            * `### Method 2: [빠른 풀이 공식/스킬]` 
            * `### Method 3: [직관/그래프 해석]`
            * 제목에는 반드시 **핵심 수학 개념**을 포함해.
              * 예: **### Method 1: 차함수와 인수정리 활용**
              * 예: **### Method 2: 비율 관계를 이용한 빠른 풀이**
              * 예: **### Method 3: 그래프의 대칭성을 이용한 풀이**

            **[2. 본문 서술 방식 (Bullet Points)]**
            * 줄글로 길게 늘어쓰지 마. (가독성 떨어짐)
            * **반드시 `Step` 별로 나누고, 그 안에서 `글머리 기호(Bullet point)`를 사용해.**
            * **핵심 논리 위주**: "개형은 알지? 바로 조건 (가)를 보자." 같은 뉘앙스로, **조건 해석 -> 식 세우기** 과정을 군더더기 없이 연결해.
            * 예시:
              **Step 1: 조건 해석**
              * $g(x)$가 불연속일 가능성 체크...
              * 따라서 $f(x)$는 여기서 접해야 함.
            * 구구절절한 문장보다는 명사형 종결(~함, ~임)이나 간결한 문장 사용.
            
            **[3. 수식 표현 (LaTeX Layout)]**
            * 문장 중간의 변수나 간단한 식은 `$ f(x) $` 와 같이 인라인으로 써.
            * **크기 통일**: 문장 속에 들어가는 간단한 변수($x$) 외에, **모든 계산 식과 등식은 반드시 `$$ ... $$` (Display Math)를 사용해 중앙에 크게 배치해.** (그래야 분수가 커 보임)
            * **분수**: 무조건 `\dfrac` 사용.
            * **[핵심 치트키]**: 모든 수식의 맨 앞에는 습관적으로 `\displaystyle` 명령어를 붙여. (예: `$\displaystyle \dfrac{1}{2}$`) 이렇게 하면 분수가 절대 작아지지 않아.
            * 수식 위아래로 빈 줄을 하나씩 둬서 시원시원하게 보이게 해.
            * **[중요] 수식 줄바꿈**: 
              * 한 줄에 수식이 너무 길어지면 **절대 옆으로 늘어뜨리지 마.**
              * 등호(`=`)를 기준으로 **줄을 바꿔서(`\\`)** 아래로 내려 써.
              * 예시:
                $$
                \begin{aligned} 
                f(x) &= x^3 + 3x^2 + a \\ 
                     &= (x+1)^3 - 1 
                \end{aligned}
                $$

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