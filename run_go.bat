@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder на Go
echo ==========================================
echo.

if not exist "vk_finder.exe" (
    echo Программа не собрана!
    echo Сначала запустите: install_go.bat
    echo.
    pause
    exit /b 1
)

vk_finder.exe

pause
