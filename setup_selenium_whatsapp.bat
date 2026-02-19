@echo off
echo ========================================
echo   WhatsApp Selenium Setup
echo ========================================
echo.

echo Installing Selenium...
pip install selenium webdriver-manager --quiet

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: python test_selenium_whatsapp.py
echo 2. Scan QR code (first time only)
echo 3. After that, it works automatically!
echo.
echo Usage in Pixie:
echo   "Send WhatsApp message to +1234567890 saying hello"
echo.
pause
