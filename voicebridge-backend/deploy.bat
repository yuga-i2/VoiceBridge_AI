@echo off
setlocal
cd /d "c:\Users\ranan\Desktop\voiceBridge Ai"
call .venv\Scripts\activate.bat
cd voicebridge-backend
zappa update dev
