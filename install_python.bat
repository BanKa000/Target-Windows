@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder - Установка
echo ==========================================
echo.

echo [1/4] Проверка Python...
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

echo [2/4] Очистка старых данных...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
if exist "%USERPROFILE%\.vk_finder_profile" (
    rd /s /q "%USERPROFILE%\.vk_finder_profile"
)
echo Готово.
echo.

echo [3/4] Установка зависимостей Python...
python -m pip install --upgrade pip
pip install --upgrade --force-reinstall -r requirements.txt
if %errorlevel% neq 0 (
    echo Ошибка установки зависимостей!
    pause
    exit /b 1
)
echo Готово.
echo.

echo [4/4] Установка браузеров Playwright...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo Ошибка установки браузеров!
    pause
    exit /b 1
)
echo Готово.

echo.
echo ==========================================
echo   Установка завершена успешно!
echo ==========================================
echo.
echo Теперь запустите программу:
echo   run_python.bat
echo.
pause
