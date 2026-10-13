@echo off
chcp 65001 >nul
echo ==========================================
echo   ПРОВЕРКА КОДА АВТОРИЗАЦИИ
echo ==========================================
echo.

echo Проверка файла vk_finder.py...
echo.

REM Проверяем наличие правильных вызовов VkApi (более гибкий поиск)
findstr /i "vk_api.VkApi" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Найден вызов vk_api.VkApi
    findstr /i "vk_api.VkApi" vk_finder.py
) else (
    echo ❌ НЕ найден вызов VkApi!
)

echo.

REM Проверяем наличие .auth()
findstr /i "vk_session.auth()" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Найден вызов vk_session.auth()
) else (
    echo ❌ НЕ найден вызов .auth()!
)

echo.

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
echo   ПРОВЕРКА СВЯЗИ КНОПКИ
echo ==========================================
echo.

REM Проверяем, к какой функции привязана кнопка
findstr /i "btn_api.clicked.connect" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Кнопка btn_api привязана к функции:
    findstr /i "btn_api.clicked.connect" vk_finder.py
) else (
    echo ❌ НЕ найдена привязка кнопки btn_api!
)

echo.
echo ==========================================
echo   РЕЗУЛЬТАТ
echo ==========================================
echo.
echo Если все проверки прошли успешно (✅),
echo то код авторизации правильный.
echo.
echo Правильная структура:
echo 1. vk_api.VkApi(login=..., password=...)
echo 2. vk_session.auth()
echo 3. Кнопка привязана к start_api_login
echo.
echo Если найдены проблемы (❌), запустите:
echo   clean_and_reinstall.bat
echo.
pause
