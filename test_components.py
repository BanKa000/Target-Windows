#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки всех компонентов
"""

import sys

print("=" * 50)
print("ТЕСТ КОМПОНЕНТОВ ПРОГРАММЫ")
print("=" * 50)
print()

# Тест 1: Python версия
print("[1/6] Проверка Python...")
print(f"Версия: {sys.version}")
print(f"Путь: {sys.executable}")
print("✅ Python работает")
print()

# Тест 2: PyQt6
print("[2/6] Проверка PyQt6...")
try:
    from PyQt6.QtWidgets import QApplication
    print("✅ PyQt6 импортирован")
except Exception as e:
    print(f"❌ Ошибка PyQt6: {e}")
    sys.exit(1)
print()

# Тест 3: vk_api
print("[3/6] Проверка vk_api...")
try:
    import vk_api
    print(f"Версия: {vk_api.__version__ if hasattr(vk_api, '__version__') else 'неизвестна'}")
    print("✅ vk_api импортирован")
except Exception as e:
    print(f"❌ Ошибка vk_api: {e}")
    sys.exit(1)
print()

# Тест 4: playwright
print("[4/6] Проверка playwright...")
try:
    from playwright.sync_api import sync_playwright
    print("✅ playwright импортирован")
except Exception as e:
    print(f"❌ Ошибка playwright: {e}")
    sys.exit(1)
print()

# Тест 5: openpyxl
print("[5/6] Проверка openpyxl...")
try:
    import openpyxl
    print(f"Версия: {openpyxl.__version__}")
    print("✅ openpyxl импортирован")
except Exception as e:
    print(f"❌ Ошибка openpyxl: {e}")
    sys.exit(1)
print()

# Тест 6: Синтаксис vk_finder.py
print("[6/6] Проверка синтаксиса vk_finder.py...")
try:
    with open('vk_finder.py', 'r', encoding='utf-8') as f:
        code = f.read()
    compile(code, 'vk_finder.py', 'exec')
    print("✅ Синтаксис правильный")
except SyntaxError as e:
    print(f"❌ Ошибка синтаксиса: {e}")
    sys.exit(1)
print()

print("=" * 50)
print("✅ ВСЕ КОМПОНЕНТЫ РАБОТАЮТ")
print("=" * 50)
print()
print("Теперь запустите программу:")
print("  run_python.bat")
