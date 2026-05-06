import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="My Web App", layout="wide")

# index.html 파일 읽기
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Streamlit 앱에 HTML 삽입
components.html(html_content, height=800, scrolling=True)
