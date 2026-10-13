@echo off
chcp 65001 >nul
echo ==========================================
echo   Проверка компиляции VK Finder
echo ==========================================
echo.

echo Проверяю наличие Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Go не установлен!
    echo.
    echo Скачайте и установите Go с сайта:
    echo https://go.dev/dl/
    echo.
    echo ВАЖНО: При установке отметьте "Add to PATH"
    echo.
    pause
    exit /b 1
)

echo Go найден:
go version
echo.

echo Синхронизирую зависимости...
go mod tidy
if %errorlevel% neq 0 (
    echo Ошибка синхронизации зависимостей!
    pause
    exit /b 1
)
echo Готово.
echo.

echo Компилирую программу...
go build -o vk_finder.exe vk_finder.go
if %errorlevel% neq 0 (
    echo.
    echo Ошибка компиляции!
    echo.
    echo Попробуйте:
    echo 1. Удалить папку go.sum
    echo 2. Запустить install_go.bat
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Компиляция успешна!
echo ==========================================
echo.
echo Файл vk_finder.exe создан.
echo.
echo Запустите программу:
echo   run_go.bat
echo.
pause
