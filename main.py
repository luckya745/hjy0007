import streamlit as st
import streamlit.components.v1 as components
import os

# 1. 페이지 레이아웃 설정: 여백 없이 전체 화면 사용
st.set_page_config(
    page_title="해동고승전 데이터베이스", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Streamlit 자체 디자인(흰색 여백, 상단바)을 강제로 제거
st.markdown("""
    <style>
    /* 전체 여백 제거 */
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    /* 상단 헤더 및 메뉴 숨기기 */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {display: none !important;}
    /* 배경색을 사이드바와 통일 (로딩 시 깜빡임 방지) */
    .main {
        background-color: #1a1a1a !important;
    }
    iframe {
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# 파일 읽기 함수 (UTF-8 인코딩 보장)
def get_file_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 필요한 파일 로드
html_layout = get_file_content("index.html")
css_style = get_file_content("styles.css")
js_data = get_file_content("data.js")  # 대용량 데이터 파일
js_app = get_file_content("app.js")    # 메인 로직 파일

# 3. 통합 HTML 구성: 로딩 순서가 중요합니다.
# data.js가 완전히 읽힌 후 app.js가 실행되도록 분리 배치합니다.
combined_html = f"""
<!DOCTYPE html>
<html style="margin: 0; padding: 0;">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    /* 외부 CSS 스타일 적용 */
    {css_style}
    
    /* iframe 내부 여백 제거 */
    body {{
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }}
    </style>
</head>
<body>
    {html_layout}

    <!-- [중요] 1. 대용량 데이터(data.js)를 메모리에 먼저 올림 -->
    <script>
    {js_data}
    </script>

    <!-- [중요] 2. 데이터 로드 완료 후 앱 로직(app.js) 실행 -->
    <script>
    // 데이터가 준비된 후 실행되도록 지연을 주거나 즉시 실행
    {js_app}
    </script>
</body>
</html>
"""

# 4. 화면 출력: 높이(height)는 실제 앱의 길이에 맞춰 1000~1500 사이로 조절하세요.
components.html(combined_html, height=1200, scrolling=True)
