@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder - Запуск
echo ==========================================
echo.

python vk_finder.py

if %errorlevel% neq 0 (
    echo.
    echo Ошибка запуска программы!
    echo.
    echo Если это первый запуск, выполните:
    echo   install_python.bat
    echo.
    pause
)
