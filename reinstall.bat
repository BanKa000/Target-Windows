@echo off
chcp 65001 >nul
echo ==========================================
echo   ПОЛНАЯ ПЕРЕУСТАНОВКА ПРОГРАММЫ
echo ==========================================
echo.
echo Это удалит ВСЕ старые файлы и установит программу заново
echo.
pause

echo.
echo [1/7] Остановка всех процессов Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 /nobreak >nul
echo Готово.

echo.
echo [2/7] Удаление всех Python кэшей...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
del /s /q *.pyd 2>nul
echo Готово.

echo.
echo [3/7] Удаление всех старых файлов проекта...
rd /s /q node_modules 2>nul
rd /s /q src 2>nul
rd /s /q dist 2>nul
rd /s /q electron 2>nul
rd /s /q build 2>nul
rd /s /q release 2>nul
del /q package.json 2>nul
del /q package-lock.json 2>nul
del /q tsconfig.json 2>nul
del /q vite.config.js 2>nul
del /q vite.config.ts 2>nul
del /q index.html 2>nul
del /q vk_login.html 2>nul
echo Готово.

echo.
echo [4/7] Удаление данных авторизации VK...
if exist "%USERPROFILE%\.vk_finder_profile" (
    rd /s /q "%USERPROFILE%\.vk_finder_profile"
    echo Данные авторизации удалены.
) else (
    echo Данные авторизации не найдены.
)

echo.
echo [5/7] Удаление временных файлов...
del /q *.log 2>nul
del /q *.tmp 2>nul
del /q *.bak 2>nul
echo Готово.

echo.
echo [6/7] Переустановка зависимостей Python...
python -m pip uninstall -y vk_api PyQt6 playwright openpyxl 2>nul
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
if %errorlevel% neq 0 (
    echo Ошибка установки зависимостей!
    pause
    exit /b 1
)
echo Готово.

echo.
echo [7/7] Переустановка браузеров Playwright...
playwright uninstall --all 2>nul
playwright install chromium
if %errorlevel% neq 0 (
    echo Ошибка установки браузеров!
    pause
    exit /b 1
)
echo Готово.

echo.
echo ==========================================
echo   ПЕРЕУСТАНОВКА ЗАВЕРШЕНА!
echo ==========================================
echo.
echo Теперь запустите программу:
echo   run_python.bat
echo.
echo ВАЖНО: Используйте ОРАНЖЕВУЮ кнопку
echo "Войти по логину/паролю" - она работает
echo через vk_api напрямую, без браузера!
echo.
echo Если проблема повторится, проверьте:
echo 1. Python версии 3.10 или выше
echo 2. Все зависимости установлены
echo 3. Файл vk_finder.py не повреждён
echo.
pause
