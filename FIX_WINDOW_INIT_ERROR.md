# 🔧 Решение ошибки "Failed to get the value of variable window.init"

## ❌ Что означает эта ошибка

Эта ошибка возникает, когда программа пытается использовать **старый код** с QWebEngineView (встроенный браузер Qt) и JavaScript переменной `window.init`.

**Важно:** В текущей версии программы НЕТ этого кода! Если вы видите эту ошибку, значит:
- Запущена старая версия программы
- Есть кэшированные .pyc файлы от старой версии
- Установлены неправильные зависимости

## ✅ Решение (3 шага)

### Шаг 1: Проверьте версию программы

Запустите:
```bash
check_version.bat
```

Этот скрипт проверит файл `vk_finder.py` и покажет, есть ли в нём проблемные элементы.

**Правильная версия должна:**
- ✅ Содержать `vk_api`
- ❌ НЕ содержать `QWebEngine`
- ❌ НЕ содержать `window.init`
- ❌ НЕ содержать `vk_login.html`
- ❌ НЕ содержать `VKID`

### Шаг 2: Полная переустановка

Если проверка показала проблемы, запустите:
```bash
reinstall.bat
```

Этот скрипт:
1. Остановит все процессы Python
2. Удалит все кэши и старые файлы
3. Удалит данные авторизации VK
4. Переустановит все зависимости
5. Переустановит браузеры Playwright

### Шаг 3: Запуск программы

```bash
run_python.bat
```

**ВАЖНО:** Используйте **оранжевую кнопку "Войти по логину/паролю"**

Она работает через `vk_api` напрямую — без браузера, без JavaScript, без QWebEngineView.

## 🎯 Как работает правильная версия

### Оранжевая кнопка "Войти по логину/паролю"

```python
# Правильный код (в текущей версии):
vk_session = vk_api.VkApi(
    login=self.login,
    password=self.password,
    app_id=2685278
)

if self.code:
    def auth_handler():
        return self.code, True
    vk_session.auth_handler = auth_handler

vk_session.auth()  # Прямой запрос к API VK, без браузера!
```

Этот код:
- Отправляет запрос напрямую на серверы VK
- Не открывает браузер
- Не использует JavaScript
- Работает стабильно

### Синяя кнопка "Войти ВКонтакте"

```python
# Запасной вариант:
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(...)
    page = context.pages[0]
    page.goto("https://vk.com/login")
    # Пользователь входит вручную
    # Нажимает "✓ Я авторизовался"
```

Этот код:
- Открывает внешний браузер Chromium (через Playwright)
- НЕ использует QWebEngineView
- Требует ручного подтверждения

## ❌ Что НЕ должно быть в программе

Если вы видите эти элементы в коде — это **старая версия**:

```python
# НЕПРАВИЛЬНО:
from PyQt6.QtWebEngineWidgets import QWebEngineView

browser = QWebEngineView()
browser.load(QUrl("https://oauth.vk.com/..."))

# Попытка прочитать JavaScript переменную:
page.runJavaScript("window.init")
```

## 🔍 Как проверить, что у вас правильная версия

Откройте файл `vk_finder.py` в текстовом редакторе и проверьте:

**Должно быть:**
- ✅ `import vk_api`
- ✅ `from playwright.sync_api import sync_playwright`
- ✅ `vk_session = vk_api.VkApi(...)`
- ✅ `vk_session.auth()`

**НЕ должно быть:**
- ❌ `QWebEngineView`
- ❌ `window.init`
- ❌ `vk_login.html`
- ❌ `VKID`
- ❌ `oauth.vk.com`

## 🆘 Если проблема не решается

### Вариант 1: Ручная очистка

```bash
# Удалите все кэши вручную:
rd /s /q __pycache__
del /s /q *.pyc

# Удалите данные авторизации:
rd /s /q "%USERPROFILE%\.vk_finder_profile"

# Переустановите зависимости:
pip uninstall -y vk_api PyQt6 playwright openpyxl
pip install -r requirements.txt --force-reinstall
playwright install chromium
```

### Вариант 2: Скачайте программу заново

Если файлы повреждены, скачайте программу заново из надёжного источника.

### Вариант 3: Проверьте Python

```bash
python --version
```

Должна быть версия **3.10 или выше**.

## 📞 Поддержка

Если ничего не помогает:

1. Запустите `check_version.bat` и покажите результат
2. Запустите `reinstall.bat` и покажите логи
3. Откройте `vk_finder.py` и проверьте содержимое
4. Убедитесь, что используете оранжевую кнопку "Войти по логину/паролю"

## 🎯 Итог

**Правильная версия программы:**
- ✅ Использует `vk_api` для авторизации по логину/паролю
- ✅ Использует `playwright` для авторизации через браузер (запасной вариант)
- ❌ НЕ использует QWebEngineView
- ❌ НЕ использует VK ID SDK
- ❌ НЕ использует JavaScript переменные

Если вы видите ошибку `window.init` — запустите `reinstall.bat` для полной переустановки.
