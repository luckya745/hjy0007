import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# 1. 페이지 설정
st.set_page_config(page_title="해동고승전", layout="wide")

# 2. Streamlit 기본 여백 제거 및 배경색 설정
st.markdown("""
    <style>
    .block-container { padding: 0rem !important; }
    header, footer { display: none !important; }
    .main { background-color: #1a1a1a !important; }
    iframe { border: none !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

def get_file_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 파일 로드
html_layout = get_file_content("index.html")
css_style = get_file_content("styles.css")
js_data = get_file_content("data.js")
js_app = get_file_content("app.js")

# 3. 데이터와 앱 로직을 각각의 Base64 스크립트로 변환 (안정성 확보)
data_b64 = base64.b64encode(js_data.encode('utf-8')).decode('utf-8')
app_b64 = base64.b64encode(js_app.encode('utf-8')).decode('utf-8')

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

    <!-- 1. 대용량 데이터를 메모리에 먼저 주입 (Base64 방식) -->
    <script src="data:text/javascript;base64,{data_b64}"></script>

    <!-- 2. 데이터 로드 확인 후 앱 실행 -->
    <script>
    (function() {{
        function init() {{
            // data.js 내의 전역 변수가 로드되었는지 확인 (변수명이 data가 아닐 경우 수정 필요)
            const script = document.createElement('script');
            script.src = "data:text/javascript;base64,{app_b64}";
            document.body.appendChild(script);
            console.log("App script injected.");
        }}

        if (document.readyState === 'complete') {{
            init();
        }} else {{
            window.addEventListener('load', init);
        }}
    }})();
    </script>
</body>
</html>
"""

# 4. 출력 (높이는 콘텐츠 양에 따라 1500 이상으로 넉넉히 잡으셔도 됩니다)
components.html(combined_html, height=1500, scrolling=True)
