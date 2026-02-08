@echo off
echo Building Pixie AI executable...
echo.

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
pyinstaller pixie.spec

echo.
echo Build complete! Check the 'dist' folder for PixieAI.exe
pause
