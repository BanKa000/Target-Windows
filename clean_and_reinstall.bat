@echo off
chcp 65001 >nul
echo ==========================================
echo   ПОЛНАЯ ОЧИСТКА И ПЕРЕУСТАНОВКА
echo ==========================================
echo.
echo Этот скрипт удалит ВСЕ старые файлы и переустановит программу
echo.
pause

echo.
echo [1/6] Остановка всех процессов Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 /nobreak >nul
echo Готово.

echo.
echo [2/6] Удаление всех кэшей Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo Готово.

echo.
echo [3/6] Удаление данных авторизации VK...
if exist "%USERPROFILE%\.vk_finder_profile" (
    rd /s /q "%USERPROFILE%\.vk_finder_profile"
    echo Данные авторизации удалены.
) else (
    echo Данные авторизации не найдены.
)

echo.
echo [4/6] Удаление временных файлов...
del /q *.log 2>nul
del /q *.tmp 2>nul
echo Готово.

echo.
echo [5/6] Переустановка зависимостей Python...
python -m pip uninstall -y vk_api PyQt6 playwright openpyxl 2>nul
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall --no-cache-dir
if %errorlevel% neq 0 (
    echo Ошибка установки зависимостей!
    pause
    exit /b 1
)
echo Готово.

echo.
echo [6/6] Переустановка браузеров Playwright...
playwright uninstall --all 2>nul
python -m playwright install chromium
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
echo "Войти по логину/паролю"
echo.
pause
