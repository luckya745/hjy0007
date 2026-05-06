import streamlit as st
import streamlit.components.v1 as components
import os

# 페이지 기본 설정
st.set_page_config(page_title="해동고승전 데이터베이스", layout="wide")

# Streamlit 고유 여백 및 배경색 제거
st.markdown("""
    <style>
    .block-container { padding: 0rem !important; }
    header, footer { display: none !important; }
    .main { background-color: #1a1a1a !important; }
    iframe { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

def get_file_content(file_path):
    """파일을 UTF-8로 읽어오는 안전 함수"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 파일 로드 (summaries.js 포함)
html_layout = get_file_content("index.html")
css_style = get_file_content("styles.css")
js_data = get_file_content("data.js")
js_summaries = get_file_content("summaries.js")
js_app = get_file_content("app.js")

# 통합 HTML 생성
combined_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
    {css_style}
    body {{ margin: 0; padding: 0; background-color: #1a1a1a; }}
    </style>
</head>
<body>
    {html_layout}

    <script>
    // 1. 데이터 주입 (try-catch로 문법 에러 시에도 중단 방지)
    try {{
        {js_data}
        console.log("data.js 주입 완료");
    }} catch(e) {{ console.error("data.js 문법 에러:", e); }}

    try {{
        {js_summaries}
        console.log("summaries.js 주입 완료");
    }} catch(e) {{ console.error("summaries.js 문법 에러:", e); }}

    // 2. 앱 실행 (데이터가 로드된 후 0.5초 뒤 실행)
    window.onload = function() {{
        setTimeout(function() {{
            try {{
                {js_app}
                console.log("app.js 실행 완료");
            }} catch(e) {{ console.error("app.js 실행 에러:", e); }}
        }}, 500);
    }};
    </script>
</body>
</html>
"""

# 화면 출력
components.html(combined_html, height=1500, scrolling=True)
