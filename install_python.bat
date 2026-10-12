@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder - Установка
echo ==========================================
echo.

echo [1/3] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не установлен!
    echo.
    echo Скачайте и установите Python с сайта:
    echo https://www.python.org/downloads/
    echo.
    echo ВАЖНО: При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Python найден:
python --version
echo.

echo [2/3] Установка зависимостей Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Ошибка установки зависимостей!
    pause
    exit /b 1
)

echo.
echo [3/3] Установка браузеров Playwright...
playwright install chromium
if %errorlevel% neq 0 (
    echo Ошибка установки браузеров!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Установка завершена успешно!
echo ==========================================
echo.
echo Теперь запустите программу:
echo   run.bat
echo.
pause
