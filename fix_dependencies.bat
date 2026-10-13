@echo off
chcp 65001 >nul
echo ==========================================
echo   УСТАНОВКА СОВМЕСТИМЫХ ВЕРСИЙ
echo ==========================================
echo.

echo Проверка версии Python...
python --version
echo.

echo Обновление pip...
python -m pip install --upgrade pip
echo.

echo Установка совместимых версий зависимостей...
echo.

echo [1/5] greenlet (обновление для Python 3.15)...
pip install --upgrade greenlet
if %errorlevel% neq 0 (
    echo Ошибка установки greenlet!
    pause
    exit /b 1
)

echo [2/5] PyQt6...
pip install --upgrade PyQt6
if %errorlevel% neq 0 (
    echo Ошибка установки PyQt6!
    pause
    exit /b 1
)

echo [3/5] playwright...
pip install --upgrade playwright
if %errorlevel% neq 0 (
    echo Ошибка установки playwright!
    pause
    exit /b 1
)

echo [4/5] openpyxl...
pip install --upgrade openpyxl
if %errorlevel% neq 0 (
    echo Ошибка установки openpyxl!
    pause
    exit /b 1
)

echo [5/5] vk_api...
pip install --upgrade vk_api
if %errorlevel% neq 0 (
    echo Ошибка установки vk_api!
    pause
    exit /b 1
)

echo.
echo Установка браузеров Playwright...
playwright install chromium
if %errorlevel% neq 0 (
    echo Ошибка установки браузеров!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   УСТАНОВКА ЗАВЕРШЕНА!
echo ==========================================
echo.
echo Все зависимости обновлены до совместимых версий.
echo.
echo Теперь запустите программу:
echo   run_python.bat
echo.
pause
