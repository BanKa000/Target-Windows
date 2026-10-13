@echo off
chcp 65001 >nul
echo ==========================================
echo   Очистка кэша и данных авторизации
echo ==========================================
echo.

echo [1/3] Очистка Python кэша...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (*.pyc) do @if exist "%%d" del /q "%%d"
echo Готово.

echo.
echo [2/3] Очистка данных авторизации VK...
if exist "%USERPROFILE%\.vk_finder_profile" (
    rd /s /q "%USERPROFILE%\.vk_finder_profile"
    echo Данные авторизации удалены.
) else (
    echo Данные авторизации не найдены.
)

echo.
echo [3/3] Очистка временных файлов...
if exist "*.log" del /q *.log
echo Готово.

echo.
echo ==========================================
echo   Очистка завершена!
echo ==========================================
echo.
echo Теперь запустите программу заново:
echo   run_python.bat
echo.
pause
