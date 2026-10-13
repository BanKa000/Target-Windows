# ⚡ БЫСТРОЕ РЕШЕНИЕ ПРОБЛЕМ

## Ошибка "Failed to get the value of variable window.init"

### Что делать прямо сейчас:

```bash
# Шаг 1: Полная переустановка
reinstall.bat

# Шаг 2: Запуск программы
run_python.bat

# Шаг 3: Авторизация
# Используйте ОРАНЖЕВУЮ кнопку "Войти по логину/паролю"
```

### Если не помогло:

```bash
# Проверьте версию программы
check_version.bat
```

### Подробные инструкции:

- [FIX_WINDOW_INIT_ERROR.md](FIX_WINDOW_INIT_ERROR.md) — полное руководство
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — решение других проблем
- [README.md](README.md) — основная документация

## Важные файлы:

- `reinstall.bat` — полная переустановка (удаляет ВСЁ и устанавливает заново)
- `check_version.bat` — проверка версии программы
- `clean.bat` — быстрая очистка кэша
- `run_python.bat` — запуск программы

## Правильная версия программы:

✅ Использует `vk_api` для авторизации  
✅ Использует `playwright` для парсинга  
❌ НЕ использует QWebEngineView  
❌ НЕ использует window.init  
❌ НЕ использует VK ID SDK  

Если видите ошибку `window.init` — у вас старая версия! Запустите `reinstall.bat`.
