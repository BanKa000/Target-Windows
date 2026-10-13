@echo off
chcp 65001 >nul
echo ==========================================
echo   ПРОВЕРКА КОДА АВТОРИЗАЦИИ
echo ==========================================
echo.

echo Проверка файла vk_finder.py...
echo.

REM Проверяем наличие правильных вызовов VkApi
findstr /i "vk_api.VkApi(login=" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Найден правильный вызов: vk_api.VkApi(login=...)
) else (
    echo ❌ НЕ найден правильный вызов VkApi!
)

REM Проверяем отсутствие проблемных аргументов
findstr /i "auth_token_code" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: auth_token_code - это старая версия!
    echo    Запустите clean_and_reinstall.bat
) else (
    echo ✅ auth_token_code не найден - хорошо
)

findstr /i "token_only" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: token_only - это старая версия!
    echo    Запустите clean_and_reinstall.bat
) else (
    echo ✅ token_only не найден - хорошо
)

findstr /i "QWebEngine" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: QWebEngine - это старая версия!
    echo    Запустите clean_and_reinstall.bat
) else (
    echo ✅ QWebEngine не найден - хорошо
)

findstr /i "window.init" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: window.init - это старая версия!
    echo    Запустите clean_and_reinstall.bat
) else (
    echo ✅ window.init не найден - хорошо
)

echo.
echo ==========================================
echo   РЕЗУЛЬТАТ
echo ==========================================
echo.
echo Если все проверки прошли успешно (✅),
echo то код авторизации правильный.
echo.
echo Если найдены проблемы (❌), запустите:
echo   clean_and_reinstall.bat
echo.
pause
