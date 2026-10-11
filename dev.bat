@echo off
chcp 65001 >nul
echo ==========================================
echo   VK Community Finder - Режим разработки
echo ==========================================
echo.

echo Запуск Vite dev-сервера...
start "Vite Dev Server" cmd /k "npm run dev"

echo.
echo Ожидание запуска сервера (3 секунды)...
timeout /t 3 /nobreak >nul

echo.
echo Запуск Electron...
npx electron electron/dev.js

pause
