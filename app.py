import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sympy as sp
import re
import traceback

# ==========================================
# 1. 디자인 & 스타일 (Masterpiece CSS - 최종_진짜_최종.ver)
# ==========================================
st.set_page_config(layout="wide", page_title="2호기: 수학의 정점")

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }

    /* 전체 배경 및 폰트 설정 */
    .stApp { background-color: #ffffff !important; }
    html, body, [class*="css"] {
        font-size: 13px !important; 
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* 제목 스타일 */
    h1, h2, h3, h4 {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #000000 !important;
        margin-bottom: 0.5rem !important;
    }

    /* 본문 텍스트 */
    .stMarkdown p, li {
        font-size: 13px !important;
        line-height: 1.7 !important;
        color: #374151 !important;
    }

    /* 사이드바 스타일 (민트색 배경) */
    section[data-testid="stSidebar"] {
        background-color: #00C4B4 !important;
        border-right: 1px solid #e5e7eb;
    }
    
    /* 사이드바 안의 기본 글씨는 흰색 */
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* 상단 헤더 */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 1px solid #e5e7eb !important;
    }

    /* 입력 UI 커스텀 */
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

    /* 라디오 버튼 선택 글씨 강조 */
    div[data-testid="stRadio"] label p {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* 버튼 스타일 (기본) */
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
    
    /* [수정 1] 앱 초기화 버튼: 볼드체 제거(400) + 검은색 유지 */
    section[data-testid="stSidebar"] .stButton button p {
        color: #000000 !important;
        font-weight: 400 !important; /* 굵기: Normal */
    }
    /* 혹시 p 태그가 아닌 경우 대비 */
    section[data-testid="stSidebar"] .stButton button {
        color: #000000 !important;
    }

    /* [수정 2] 분석 중(스피너) 문구 검은색 강제 적용 */
    div[data-testid="stSpinner"] * {
        color: #000000 !important;
    }

    /* Expander 스타일 */
    .streamlit-expanderHeader {
        background-color: #f9fafb !important;
        border-radius: 8px !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 핵심 로직 & 함수
# ==========================================

# 상태 초기화
if 'step_index' not in st.session_state:
    st.session_state.step_index = 1
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# API 키 설정 (Secrets 사용)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except FileNotFoundError:
    st.sidebar.error("⚠️ secrets.toml 파일을 찾을 수 없습니다.")
except KeyError:
    st.sidebar.error("⚠️ GOOGLE_API_KEY가 설정되지 않았습니다.")

# 인터랙티브 수학 연구소 (Sympy)
def interactive_math_lab():
    st.markdown("---")
    st.markdown("### 🧪 인터랙티브 수학 연구소 (Interactive Lab)")
    
    if 'math_expr' not in st.session_state:
        st.session_state.math_expr = "x**2 - 4*x + 3"

    col_input, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("🎲 랜덤 예제"):
            import random
            examples = ["x**2 - 2*x - 3", "sin(x) + cos(x)", "(x + 1) / (x - 2)", "a * x**2 + b"]
            st.session_state.math_expr = random.choice(examples)
            st.rerun()

    with col_input:
        expr_input = st.text_input("함수식 입력 f(x) =", value=st.session_state.math_expr)

    try:
        x = sp.symbols('x')
        expr = sp.sympify(expr_input)
        free_symbols = sorted(list(expr.free_symbols), key=lambda s: s.name)
        params = {s: 1.0 for s in free_symbols if s.name != 'x'}
        
        if params:
            cols = st.columns(len(params))
            for i, (sym, val) in enumerate(params.items()):
                with cols[i]:
                    params[sym] = st.slider(f"${sym.name}$", -10.0, 10.0, 1.0, 0.1)
        
        final_expr = expr.subs(params)
        f_func = sp.lambdify(x, final_expr, "numpy")
        
        c_left, c_right = st.columns([1, 1.5])
        with c_left:
            st.latex(f"f(x) = {sp.latex(final_expr)}")
            st.write(f"도함수: $f'(x) = {sp.latex(sp.diff(final_expr, x))}$")
        with c_right:
            fig, ax = plt.subplots(figsize=(6, 3))
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f_func(x_vals)
            y_vals[y_vals > 20] = np.nan
            y_vals[y_vals < -20] = np.nan
            ax.plot(x_vals, y_vals, color='#00C4B4')
            ax.grid(True, linestyle='--', alpha=0.5)
            st.pyplot(fig)
    except Exception:
        pass

# ==========================================
# 3. 사이드바 UI
# ==========================================
with st.sidebar:
    st.title("최승규 2호기")
    st.write("수학 문제 해결의 새로운 기준")
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

# [상태 1] 파일 없음
if not uploaded_file:
    st.info("👈 왼쪽 사이드바에서 문제 사진을 업로드해주세요.")
    st.markdown("#### ✨ 2호기 업데이트 내역")
    st.markdown("- **디자인:** 민트 & 화이트 톤의 고급스러운 UI")
    st.markdown("- **가독성:** 수식 자동 띄어쓰기 및 단계별 박스 UI 적용")
    st.markdown("- **시각화:** 그래프 사이즈 최적화 (중앙 정렬)")
    st.stop()

# [상태 2] 파일 있음 & 분석 전
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
                    # [수정] 모델 이름을 고정하지 않고, 현재 사용 가능한 최신 모델(Flash/Pro)을 자동으로 찾습니다.
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    
                    # 1순위: Flash (빠름), 2순위: Pro (똑똑함), 3순위: 아무거나
                    model_name = next((m for m in available_models if 'flash' in m), 
                                      next((m for m in available_models if 'pro' in m), available_models[0]))
                    
                    model = genai.GenerativeModel(model_name)
                    
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
                        fig, ax = plt.subplots(figsize=(6, 5))
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

# [상태 3] 분석 결과 표시 (좌측: 풀이 / 우측: 그래프)
if st.session_state.analysis_result:
    full_text = st.session_state.analysis_result
    
    try:
        # 1. 데이터 파싱 (본문과 코드 분리)
        parts = full_text.split("#CODE#")
        text_full = parts[0]
        code_part = parts[1] if len(parts) > 1 else ""
        
        # 2. 풀이 방법 추출
        methods = {}
        pattern = r"#METHOD_(\d)#(.*?)(?=#METHOD_|\Z)"
        matches = re.findall(pattern, text_full, re.DOTALL)
        for m_id, content in matches:
            methods[int(m_id)] = content.strip()
            
        # 3. 파이썬 코드 추출
        code_match = re.search(r"```python(.*?)```", code_part, re.DOTALL)
        final_code = code_match.group(1).strip() if code_match else code_part.strip()
        
        # 4. 화면 분할 (여기가 핵심!)
        # [1.2 (텍스트) : 1 (그래프)] 비율로 나누어 왼쪽/오른쪽 배치
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
            
# [수정] 화살표 텍스트 & 형광펜(검은 배경) 제거 코드
            if method_id in methods:
                steps_raw = methods[method_id].split("---")
                steps = [s.strip() for s in steps_raw if s.strip()]
                
                for i, step_text in enumerate(steps):
                    lines = step_text.split('\n')
                    
                    # 1. 제목 처리: arrow_down 글씨 강제 삭제
                    raw_title = lines[0].strip().replace('[', '').replace(']', '')
                    # 대소문자 변형까지 싹 다 지워서 깔끔하게 만듦
                    for trash in ['arrow_down', 'Arrow_down', ':arrow_down:', '_']:
                        raw_title = raw_title.replace(trash, '')
                    
                    title = raw_title.strip()
                    title = title.replace('$', ' $ ') # 수식 띄어쓰기
                    
                    # 2. 본문 처리: 형광펜(백틱 `)을 수식($)으로 변환
                    body_lines = lines[1:]
                    body_text = '\n'.join(body_lines).strip()
                    
                    # 여기가 핵심: ` 기호를 $ 로 바꾸면 검은 배경이 사라지고 흰 수식이 됨
                    body_text = body_text.replace('`', '$')
                    body_text = body_text.replace('$', ' $ ') # 수식 가독성 확보
                    
                    # 3. 화면 출력
                    with st.expander(f"STEP {i+1}: {title}", expanded=True):
                        st.markdown(body_text)
                        
                        # 그래프 버튼
                        if st.button(f"📊 그래프 보기 (Step {i+1})", key=f"btn_{method_id}_{i}"):
                            st.session_state.step_index = i + 1
            else:
                st.warning("이 풀이 방법은 생성되지 않았습니다.")

        # === [오른쪽 패널: 그래프 시각화] ===
        with col_right:
            # 상단 여백을 살짝 줘서 텍스트와 높이를 맞춤
            st.markdown(f"### 📐 시각화 (M{method_id}-S{st.session_state.step_index})")
            
            try:
                # 그래프 코드 실행
                exec_globals = {"np": np, "plt": plt, "patches": patches}
                exec(final_code, exec_globals)
                
                if "draw" in exec_globals:
                    fig = exec_globals["draw"](method_id, st.session_state.step_index)
                    
                    # [그래프 사이즈 및 위치 조정]
                    # 오른쪽 패널 안에서도 중앙에 예쁘게 뜨도록 여백(Columns) 사용
                    # [1:5:1] 비율로 설정하여 너무 크지 않고 적당하게 중앙 정렬
                    _, c_graph, _ = st.columns([0.5, 3, 0.5]) 
                    with c_graph:
                        st.pyplot(fig)
                else:
                    st.error("그래프 함수를 찾을 수 없습니다.")
            except Exception as e:
                # 그래프 생성 전이거나 오류 시 조용히 대기
                st.info("그래프를 생성하려면 왼쪽에서 단계를 선택하세요.")

    except Exception as e:
        st.error("결과 처리 중 오류가 발생했습니다.")
        st.write(e)