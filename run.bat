@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder - Быстрый запуск
echo ==========================================
echo.
echo Запуск приложения без установки...
echo.

REM Проверяем наличие dist папки
if not exist "dist" (
    echo Папка dist не найдена!
    echo Сначала соберите приложение: build.bat
    pause
    exit /b 1
)

REM Запускаем Electron
npx electron electron/main.js

if %errorlevel% neq 0 (
    echo.
    echo Ошибка запуска!
    echo Убедитесь что установлены зависимости: npm install
    pause
)
