@echo off
start cmd /k "cd /D D:\chatbot && venv\Scripts\activate && python app.py"
start cmd /k "cd /D D:\chatbot\frontend && npm start"
timeout 5
start http://localhost:3000