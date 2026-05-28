@echo off
cd /d "C:\Users\richi\Desktop\UniMedi-Trend"
call .venv\Scripts\activate.bat
streamlit run Dashboard\app.py --server.headless true --server.port 8501