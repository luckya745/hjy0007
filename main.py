import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="해동고승전 데이터베이스", layout="wide")

# 각 파일의 내용을 읽어오는 함수
def get_file_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# HTML, CSS, JS 읽기
html_layout = get_file_content("index.html")
css_style = get_file_content("styles.css")
js_data = get_file_content("data.js")
js_app = get_file_content("app.js")

# 통합 HTML 생성 (CSS와 JS를 HTML 내부에 주입)
combined_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
    {css_style}
    </style>
</head>
<body>
    {html_layout}
    <script>
    {js_data}
    {js_app}
    </script>
</body>
</html>
"""

# 화면에 표시
components.html(combined_html, height=1000, scrolling=True)
