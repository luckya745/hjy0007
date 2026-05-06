import streamlit as st
import streamlit.components.v1 as components
import os

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="해동고승전 데이터베이스", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Streamlit 고유 여백 및 배경색 강제 제거 (최신 브라우저 대응)
st.markdown("""
    <style>
    /* 전체 화면 여백 제거 */
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    header, footer, #MainMenu {
        display: none !important;
    }
    /* 배경색 동기화 (검은색 사이드바와 어울리도록) */
    .main {
        background-color: #1a1a1a !important;
    }
    iframe {
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# 파일 읽기 함수
def get_file_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 각 소스 파일 로드
html_layout = get_file_content("index.html")
css_style = get_file_content("styles.css")
js_data = get_file_content("data.js")
js_app = get_file_content("app.js")

# 3. 통합 HTML 구성 (비동기 로딩 방지 로직 포함)
combined_html = f"""
<!DOCTYPE html>
<html style="margin: 0; padding: 0;">
<head>
    <meta charset="utf-8">
    <style>
    {css_style}
    body {{ margin: 0; padding: 0; background-color: #1a1a1a; }}
    </style>
</head>
<body>
    {html_layout}

    <!-- 1. 데이터 주입 -->
    <script>
    {js_data}
    </script>

    <!-- 2. 데이터 확인 후 앱 실행 로직 -->
    <script>
    (function() {{
        function startApp() {{
            // 'data' 변수 혹은 data.js에서 정의한 핵심 변수명이 존재하는지 체크
            if (typeof data !== 'undefined' || window.data) {{
                console.log("데이터 로드 완료. 앱을 시작합니다.");
                {js_app}
            }} else {{
                console.log("데이터를 기다리는 중...");
                setTimeout(startApp, 100); // 0.1초 후에 다시 확인
            }}
        }}

        // 페이지 로드 후 실행 시작
        if (document.readyState === 'complete') {{
            startApp();
        }} else {{
            window.addEventListener('load', startApp);
        }}
    }})();
    </script>
</body>
</html>
"""

# 4. 출력 (높이는 필요에 따라 1200~1500으로 조절)
components.html(combined_html, height=1200, scrolling=True)
