# 🔧 РЕШЕНИЕ ПРОБЛЕМЫ "ПРОГРАММА НЕ ЗАПУСКАЕТСЯ"

## Шаг 1: Проверьте код авторизации

```bash
check_auth.bat
```

Должно показать:
- ✅ Найден вызов vk_api.VkApi
- ✅ Найден вызов .auth()
- ✅ Кнопка btn_api привязана к start_api_login

## Шаг 2: Запустите диагностику

```bash
diagnose.bat
```

Этот скрипт проверит:
- Python установлен
- Синтаксис vk_finder.py правильный
- Все модули импортируются
- Попытается запустить программу

## Шаг 3: Тест компонентов

```bash
python test_components.py
```

Проверит каждый модуль отдельно:
- PyQt6
- vk_api
- playwright
- openpyxl

## Шаг 4: Если ничего не помогает

```bash
clean_and_reinstall.bat
```

Полная переустановка всех зависимостей.

## Возможные ошибки и решения

### Ошибка: "ModuleNotFoundError: No module named '...'"
**Решение:**
```bash
fix_dependencies.bat
```

### Ошибка: "SyntaxError: invalid syntax"
**Решение:** Проверьте файл vk_finder.py на синтаксические ошибки

### Ошибка: "Permission denied" или "Access is denied"
**Решение:** Запустите командную строку от имени администратора

### Ошибка: "greenlet not compatible with Python 3.15"
**Решение:**
```bash
fix_dependencies.bat
```

### Программа запускается, но сразу закрывается
**Решение:** Запустите через `diagnose.bat` и скопируйте ошибку

## Порядок действий

1. `check_auth.bat` - проверка кода
2. `diagnose.bat` - диагностика
3. `python test_components.py` - тест модулей
4. `fix_dependencies.bat` - обновление зависимостей
5. `clean_and_reinstall.bat` - полная переустановка
6. `run_python.bat` - запуск программы

## Если проблема не решена

Скопируйте вывод всех команд и покажите разработчику:
1. Вывод `check_auth.bat`
2. Вывод `diagnose.bat`
3. Вывод `python test_components.py`
4. Текст ошибки при запуске `run_python.bat`
