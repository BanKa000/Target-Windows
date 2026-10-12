@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder - Сборка в .exe
echo ==========================================
echo.

echo [1/2] Установка PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo Ошибка установки PyInstaller!
    pause
    exit /b 1
)

echo.
echo [2/2] Сборка .exe файла...
pyinstaller --onefile --windowed --name "VK_Community_Finder" --icon=NONE vk_finder.py

if %errorlevel% neq 0 (
    echo Ошибка сборки!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Сборка завершена!
echo ==========================================
echo.
echo Готовый .exe файл находится в папке:
echo   dist\VK_Community_Finder.exe
echo.
echo ВАЖНО: Для работы .exe нужны браузеры Playwright.
echo Они установятся автоматически при первом запуске.
echo.
pause
