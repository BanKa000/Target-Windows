@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder - Сборка приложения
echo ==========================================
echo.

echo [1/4] Установка зависимостей...
call npm install
if %errorlevel% neq 0 (
    echo Ошибка установки зависимостей!
    pause
    exit /b 1
)

echo.
echo [2/4] Сборка веб-приложения...
call npm run build
if %errorlevel% neq 0 (
    echo Ошибка сборки веб-приложения!
    pause
    exit /b 1
)

echo.
echo [3/4] Подготовка ресурсов...
if not exist "build" mkdir build
if not exist "build\icon.ico" (
    echo.
    echo ВНИМАНИЕ: Иконка не найдена!
    echo Создайте файл build\icon.ico (256x256 или 512x512)
    echo Или используйте стандартную иконку Electron.
    echo.
)

echo.
echo [4/4] Сборка Windows приложения (.exe)...
echo Это может занять несколько минут...
call npx electron-builder --win --x64
if %errorlevel% neq 0 (
    echo.
    echo Ошибка сборки приложения!
    echo.
    echo Возможные причины:
    echo - Не установлен Node.js 18+
    echo - Нет прав администратора
    echo - Антивирус блокирует создание .exe
    echo - Недостаточно места на диске
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Сборка завершена успешно!
echo ==========================================
echo.
echo Готовый установщик находится в папке:
echo   %cd%\release\
echo.
echo Файл: VK Community Finder-1.0.0-Setup.exe
echo.
echo Можете запустить установщик для установки программы.
echo.
pause
