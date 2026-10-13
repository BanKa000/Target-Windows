@echo off
chcp 65001 >nul
echo ==========================================
echo   ПОЛНАЯ ОЧИСТКА ПРОЕКТА
echo ==========================================
echo.

echo [1/5] Удаление Python кэша...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo Готово.

echo.
echo [2/5] Удаление Node.js файлов (если есть)...
rd /s /q node_modules 2>nul
del /q package.json 2>nul
del /q package-lock.json 2>nul
del /q tsconfig.json 2>nul
del /q vite.config.js 2>nul
del /q vite.config.ts 2>nul
echo Готово.

echo.
echo [3/5] Удаление старых веб-файлов...
del /q vk_login.html 2>nul
del /q index.html 2>nul
rd /s /q src 2>nul
rd /s /q dist 2>nul
rd /s /q electron 2>nul
rd /s /q build 2>nul
rd /s /q release 2>nul
echo Готово.

echo.
echo [4/5] Очистка данных авторизации VK...
if exist "%USERPROFILE%\.vk_finder_profile" (
    rd /s /q "%USERPROFILE%\.vk_finder_profile"
    echo Данные авторизации удалены.
) else (
    echo Данные авторизации не найдены.
)

echo.
echo [5/5] Очистка временных файлов...
del /q *.log 2>nul
del /q *.tmp 2>nul
echo Готово.

echo.
echo ==========================================
echo   ОЧИСТКА ЗАВЕРШЕНА!
echo ==========================================
echo.
echo Теперь переустановите зависимости:
echo   install_python.bat
echo.
echo Затем запустите программу:
echo   run_python.bat
echo.
echo ВАЖНО: Используйте ОРАНЖЕВУЮ кнопку
echo "Войти по логину/паролю" - она работает
echo через vk_api напрямую, без браузера!
echo.
pause
