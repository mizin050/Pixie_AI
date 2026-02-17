@echo off
REM setup_ultimate.bat - One-click setup for Pixie Ultimate

echo ========================================
echo   PIXIE ULTIMATE - Setup Script
echo ========================================
echo.

echo Installing Python packages...
python -m pip install --upgrade pip
python -m pip install pyautogui pillow google-generativeai --quiet

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure GEMINI_API_KEY is set in .env file
echo 2. Run: python main.py
echo 3. Click "Pixie UI" in system tray
echo 4. Try complex tasks like:
echo    - "Build me a calculator app"
echo    - "Open Chrome and search for pizza"
echo    - "Create a Python web scraper"
echo.
pause
