@echo off
chcp 65001 >nul
echo ==========================================
echo   Установка Go и зависимостей
echo ==========================================
echo.

echo [1/4] Проверка Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Go не установлен!
    echo.
    echo Скачайте и установите Go с сайта:
    echo https://go.dev/dl/
    echo.
    pause
    exit /b 1
)

echo Go найден:
go version
echo.

echo [2/4] Синхронизация зависимостей...
go mod tidy
if %errorlevel% neq 0 (
    echo Ошибка синхронизации зависимостей!
    pause
    exit /b 1
)
echo Готово.
echo.

echo [3/4] Загрузка библиотек...
go mod download
if %errorlevel% neq 0 (
    echo Ошибка загрузки библиотек!
    pause
    exit /b 1
)
echo Готово.
echo.

echo [4/4] Сборка программы...
go build -o vk_finder.exe vk_finder.go
if %errorlevel% neq 0 (
    echo Ошибка сборки!
    pause
    exit /b 1
)
echo Готово.
echo.

echo ==========================================
echo   Установка завершена!
echo ==========================================
echo.
echo Создан файл: vk_finder.exe
echo.
echo Запустите программу:
echo   run_go.bat
echo.
pause
