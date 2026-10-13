@echo off
chcp 65001 >nul
echo ==========================================
echo   ПРОВЕРКА ВЕРСИИ ПРОГРАММЫ
echo ==========================================
echo.

echo [1/3] Проверка файла vk_finder.py...
if not exist "vk_finder.py" (
    echo ОШИБКА: Файл vk_finder.py не найден!
    pause
    exit /b 1
)
echo Файл vk_finder.py найден.

echo.
echo [2/3] Проверка содержимого файла...
echo.
echo Поиск проблемных элементов:
echo.

findstr /i "QWebEngine" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: QWebEngine - это старая версия!
    echo    Запустите reinstall.bat для переустановки
) else (
    echo ✅ QWebEngine не найден - хорошо
)

findstr /i "window.init" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: window.init - это старая версия!
    echo    Запустите reinstall.bat для переустановки
) else (
    echo ✅ window.init не найден - хорошо
)

findstr /i "vk_login.html" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: vk_login.html - это старая версия!
    echo    Запустите reinstall.bat для переустановки
) else (
    echo ✅ vk_login.html не найден - хорошо
)

findstr /i "VKID" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ НАЙДЕН: VKID - это старая версия!
    echo    Запустите reinstall.bat для переустановки
) else (
    echo ✅ VKID не найден - хорошо
)

findstr /i "vk_api" vk_finder.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ vk_api найден - это правильная версия
) else (
    echo ❌ vk_api НЕ найден - неправильная версия!
    echo    Запустите reinstall.bat для переустановки
)

echo.
echo [3/3] Проверка размера файла...
for %%A in ("vk_finder.py") do echo Размер: %%~zA байт

echo.
echo ==========================================
echo   РЕЗУЛЬТАТ ПРОВЕРКИ
echo ==========================================
echo.
echo Если все проверки прошли успешно (✅),
echo то у вас правильная версия программы.
echo.
echo Если найдены проблемы (❌), запустите:
echo   reinstall.bat
echo.
echo Правильная версия программы:
echo - Использует vk_api для авторизации
echo - НЕ использует QWebEngine
echo - НЕ использует window.init
echo - НЕ использует VK ID SDK
echo.
pause
