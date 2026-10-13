@echo off
chcp 65001 >nul
echo ==========================================
echo   ДИАГНОСТИКА ЗАПУСКА ПРОГРАММЫ
echo ==========================================
echo.

echo [1/4] Проверка Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python не найден!
    pause
    exit /b 1
)
echo ✅ Python найден
echo.

echo [2/4] Проверка синтаксиса vk_finder.py...
python -m py_compile vk_finder.py
if %errorlevel% neq 0 (
    echo ❌ Ошибка синтаксиса в vk_finder.py!
    pause
    exit /b 1
)
echo ✅ Синтаксис правильный
echo.

echo [3/4] Проверка импортов...
python -c "import sys; import PyQt6; import vk_api; import playwright; import openpyxl; print('✅ Все модули импортированы')"
if %errorlevel% neq 0 (
    echo ❌ Ошибка импорта модулей!
    echo.
    echo Попробуйте переустановить зависимости:
    echo   fix_dependencies.bat
    pause
    exit /b 1
)
echo.

echo [4/4] Попытка запуска программы...
echo.
echo Если программа не запускается, скопируйте ошибку выше
echo и покажите её разработчику.
echo.
python vk_finder.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Программа завершилась с ошибкой!
    echo.
    echo Возможные решения:
    echo 1. Запустите fix_dependencies.bat
    echo 2. Запустите clean_and_reinstall.bat
    echo 3. Проверьте логи выше
    pause
) else (
    echo.
    echo ✅ Программа завершилась нормально
    pause
)
