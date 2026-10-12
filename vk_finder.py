#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VK Community Finder - Поиск сообществ ВКонтакте
Десктопное приложение для Windows

Решение проблемы "Cannot switch to a different thread":
- Playwright создаётся ВНУТРИ каждого рабочего потока
- Cookies сохраняются на диск через persistent_context
- Авторизация делается один раз, потом переиспользуется
"""

import sys
import time
import re
import os
from pathlib import Path
from typing import List, Dict

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, 
                             QProgressBar, QMessageBox, QGroupBox, QSpinBox,
                             QComboBox, QCheckBox, QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from playwright.sync_api import sync_playwright
import openpyxl
from openpyxl.styles import Font, PatternFill


# Папка для сохранения cookies авторизации
USER_DATA_DIR = str(Path.home() / ".vk_finder_profile")


class LoginThread(QThread):
    """Поток для авторизации через vk.com/login"""
    success = pyqtSignal()
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    waiting_for_confirmation = pyqtSignal()
    
    def run(self):
        try:
            with sync_playwright() as p:
                self.status.emit("Запускаем браузер...")
                
                context = p.chromium.launch_persistent_context(
                    user_data_dir=USER_DATA_DIR,
                    headless=False,
                    args=['--start-maximized'],
                    viewport={'width': 1200, 'height': 800}
                )
                
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://vk.com/login", wait_until='domcontentloaded')
                
                self.status.emit("Войдите в аккаунт VK в браузере")
                self.waiting_for_confirmation.emit()
                
                # Ждём подтверждения от пользователя
                while not hasattr(self, '_user_confirmed'):
                    time.sleep(0.5)
                
                time.sleep(2)
                
                # Проверяем авторизацию через cookies
                cookies = context.cookies()
                has_auth = any(cookie['name'] in ['remixsid', 'remixlang'] for cookie in cookies)
                
                if has_auth:
                    self.status.emit("Авторизация успешна!")
                    time.sleep(1)
                    context.close()
                    self.success.emit()
                else:
                    # Альтернативная проверка
                    page.goto("https://vk.com/feed", wait_until='domcontentloaded', timeout=10000)
                    time.sleep(2)
                    
                    if 'login' not in page.url:
                        self.status.emit("Авторизация успешна!")
                        time.sleep(1)
                        context.close()
                        self.success.emit()
                    else:
                        context.close()
                        self.error.emit("Авторизация не удалась. Попробуйте снова.")
                
        except Exception as e:
            self.error.emit(f"Ошибка: {e}")
    
    def confirm_login(self):
        """Пользователь подтвердил авторизацию"""
        self._user_confirmed = True


class SearchThread(QThread):
    """Поток для поиска - создаёт СВОЙ Playwright"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, query: str, max_results: int, fetch_details: bool):
        super().__init__()
        self.query = query
        self.max_results = max_results
        self.fetch_details = fetch_details
        self._stop_flag = False
        
    def stop(self):
        self._stop_flag = True
    
    def run(self):
        try:
            # Playwright создаётся ВНУТРИ этого потока
            with sync_playwright() as p:
                self.progress.emit("Запускаем браузер...")
                
                # Используем сохранённые cookies
                context = p.chromium.launch_persistent_context(
                    user_data_dir=USER_DATA_DIR,
                    headless=False,
                    args=['--start-maximized'],
                    viewport={'width': 1920, 'height': 1080}
                )
                
                try:
                    # Поиск сообществ
                    communities = self._search_communities(context)
                    
                    if self._stop_flag:
                        return
                    
                    # Сбор контактов
                    if self.fetch_details and communities:
                        communities = self._fetch_all_details(context, communities)
                    
                    if not self._stop_flag:
                        self.finished.emit(communities)
                        
                finally:
                    context.close()
                    
        except Exception as e:
            self.error.emit(f"Ошибка: {e}")
    
    def _search_communities(self, context) -> List[Dict]:
        """Поиск сообществ VK"""
        self.progress.emit("Открываем страницу поиска...")
        
        page = context.new_page()
        
        try:
            url = f"https://vk.com/groups?q={self.query}"
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # Прокручиваем для загрузки
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                
                if self._stop_flag:
                    return []
            
            # Парсим результаты
            communities = []
            seen_ids = set()
            
            # Ищем ссылки на группы
            links = page.query_selector_all('a[href*="/club"]')
            
            for link in links:
                if self._stop_flag:
                    break
                
                try:
                    href = link.get_attribute('href') or ''
                    
                    match = re.search(r'/club(\d+)', href)
                    if not match:
                        continue
                    
                    group_id = int(match.group(1))
                    screen_name = f"club{group_id}"
                    
                    if group_id in seen_ids:
                        continue
                    seen_ids.add(group_id)
                    
                    # Получаем название
                    name = ''
                    # Пробуем разные селекторы для названия
                    for selector in ['span', '.group_row_title', 'div']:
                        name_elem = link.query_selector(selector)
                        if name_elem:
                            text = name_elem.inner_text().strip()
                            if text and len(text) > 2 and len(text) < 100:
                                name = text
                                break
                    
                    if not name:
                        name = screen_name
                    
                    communities.append({
                        'id': group_id,
                        'name': name,
                        'screen_name': screen_name,
                        'url': f"https://vk.com/{screen_name}",
                        'members': 0,
                        'phone': '',
                        'email': '',
                        'site': '',
                        'city': '',
                        'verified': False
                    })
                    
                    if len(communities) >= self.max_results:
                        break
                        
                except Exception:
                    continue
            
            # Если не нашли через /club, пробуем именные ссылки
            if not communities:
                self.progress.emit("Ищем именные сообщества...")
                links = page.query_selector_all('a[href^="/"]')
                
                for link in links:
                    if self._stop_flag:
                        break
                    
                    try:
                        href = link.get_attribute('href') or ''
                        if not href.startswith('/') or href.count('/') > 1:
                            continue
                        
                        screen_name = href.strip('/')
                        
                        # Пропускаем системные страницы
                        skip = ['login', 'register', 'restore', 'settings', 'feed', 
                                'messages', 'notifications', 'friends', 'groups', 
                                'search', 'im', 'mail', 'communities', 'ads', 
                                'developers', 'support', 'bugtracker', 'id', 'wall']
                        if screen_name in skip or screen_name.startswith(('id', 'wall')):
                            continue
                        
                        group_id = abs(hash(screen_name))
                        if group_id in seen_ids:
                            continue
                        seen_ids.add(group_id)
                        
                        name = link.inner_text().strip()
                        if not name or len(name) < 2 or len(name) > 100:
                            continue
                        
                        communities.append({
                            'id': group_id,
                            'name': name,
                            'screen_name': screen_name,
                            'url': f"https://vk.com/{screen_name}",
                            'members': 0,
                            'phone': '',
                            'email': '',
                            'site': '',
                            'city': '',
                            'verified': False
                        })
                        
                        if len(communities) >= self.max_results:
                            break
                            
                    except Exception:
                        continue
            
            self.progress.emit(f"Найдено {len(communities)} сообществ")
            return communities
            
        finally:
            page.close()
    
    def _fetch_all_details(self, context, communities: List[Dict]) -> List[Dict]:
        """Получить детали для всех сообществ"""
        total = len(communities)
        
        for i, community in enumerate(communities):
            if self._stop_flag:
                break
            
            self.progress.emit(f"Контакты: {i+1}/{total} - {community['name']}")
            
            try:
                details = self._fetch_community_details(context, community['screen_name'])
                community.update(details)
            except Exception:
                pass
            
            if i < total - 1:
                time.sleep(1.5)
        
        return communities
    
    def _fetch_community_details(self, context, screen_name: str) -> Dict:
        """Получить детали конкретного сообщества"""
        page = context.new_page()
        
        try:
            url = f"https://vk.com/{screen_name}"
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            time.sleep(2)
            
            details = {}
            body_text = page.inner_text('body')
            
            # Телефон
            phone_elem = page.query_selector('a[href^="tel:"]')
            if phone_elem:
                href = phone_elem.get_attribute('href')
                if href:
                    details['phone'] = href.replace('tel:', '').strip()
            else:
                # Ищем телефон в тексте
                phone_match = re.search(
                    r'([\+]?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})',
                    body_text
                )
                if phone_match:
                    details['phone'] = phone_match.group(1).strip()
            
            # Email
            email_match = re.search(r'([\w.+-]+@[\w.-]+\.\w{2,})', body_text)
            if email_match:
                email = email_match.group(1)
                if 'vk.com' not in email and 'vk.ru' not in email:
                    details['email'] = email
            
            # Сайт
            site_elem = page.query_selector('a[href^="http"]:not([href*="vk.com"]):not([href*="vk.ru"])')
            if site_elem:
                href = site_elem.get_attribute('href')
                if href and 'vk.com' not in href and 'vk.ru' not in href:
                    details['site'] = href
            
            # Участники
            members_match = re.search(r'(\d[\d\s]*)\s*(?:участник|подписчик|человек)', body_text, re.I)
            if members_match:
                details['members'] = int(members_match.group(1).replace(' ', ''))
            
            # Город
            city_patterns = [
                r'город[:\s]+([^,\n]+)',
                r'г\.\s*([^,\n]+)',
                r'Город\s*([^,\n]+)'
            ]
            for pattern in city_patterns:
                match = re.search(pattern, body_text, re.I)
                if match:
                    city = match.group(1).strip()
                    if len(city) > 1 and len(city) < 50:
                        details['city'] = city
                        break
            
            # Верификация
            if page.query_selector('[class*="verified"]'):
                details['verified'] = True
            
            return details
            
        finally:
            page.close()


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VK Community Finder - Поиск сообществ ВКонтакте")
        self.setGeometry(100, 100, 1400, 900)
        
        self.communities = []
        self.login_thread = None
        self.search_thread = None
        self.is_logged_in = False
        
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Группа авторизации
        auth_group = QGroupBox("Авторизация")
        auth_layout = QHBoxLayout()
        
        self.btn_login = QPushButton("Войти ВКонтакте")
        self.btn_login.clicked.connect(self.start_login)
        self.btn_login.setStyleSheet("background-color: #0077FF; color: white; font-weight: bold; padding: 8px 20px;")
        auth_layout.addWidget(self.btn_login)
        
        self.btn_confirm_login = QPushButton("✓ Я авторизовался")
        self.btn_confirm_login.clicked.connect(self.confirm_login)
        self.btn_confirm_login.setEnabled(False)
        self.btn_confirm_login.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 20px;")
        auth_layout.addWidget(self.btn_confirm_login)
        
        self.lbl_auth_status = QLabel("Статус: Не авторизован")
        self.lbl_auth_status.setStyleSheet("color: red; font-weight: bold;")
        auth_layout.addWidget(self.lbl_auth_status)
        
        auth_layout.addStretch()
        
        # Кнопка сброса авторизации
        self.btn_reset_auth = QPushButton("Сбросить авторизацию")
        self.btn_reset_auth.clicked.connect(self.reset_auth)
        self.btn_reset_auth.setVisible(False)
        auth_layout.addWidget(self.btn_reset_auth)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Группа поиска
        search_group = QGroupBox("Параметры поиска")
        search_layout = QVBoxLayout()
        
        # Строка поиска
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Поисковый запрос:"))
        self.input_query = QLineEdit()
        self.input_query.setPlaceholderText("Введите ключевые слова (например: автосервис, доставка, салон красоты)")
        self.input_query.returnPressed.connect(self.start_search)
        search_row.addWidget(self.input_query)
        
        self.btn_search = QPushButton("Найти")
        self.btn_search.clicked.connect(self.start_search)
        self.btn_search.setEnabled(False)
        self.btn_search.setMinimumWidth(120)
        search_row.addWidget(self.btn_search)
        
        search_layout.addLayout(search_row)
        
        # Настройки
        settings_row = QHBoxLayout()
        
        settings_row.addWidget(QLabel("Тип:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Все", "Группы", "Публичные страницы", "Встречи"])
        settings_row.addWidget(self.combo_type)
        
        settings_row.addWidget(QLabel("Макс. результатов:"))
        self.spin_max = QSpinBox()
        self.spin_max.setRange(10, 500)
        self.spin_max.setValue(50)
        settings_row.addWidget(self.spin_max)
        
        self.check_details = QCheckBox("Собирать контакты (телефон, email, сайт)")
        self.check_details.setChecked(True)
        settings_row.addWidget(self.check_details)
        
        settings_row.addStretch()
        search_layout.addLayout(settings_row)
        
        # Подсказка
        hint = QLabel("💡 Совет: чем конкретнее запрос, тем точнее результаты")
        hint.setStyleSheet("color: #888; font-style: italic;")
        search_layout.addWidget(hint)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_status)
        
        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "№", "Название", "Ссылка", "Участники", "Телефон", 
            "Email", "Сайт", "Город", "Верифицировано"
        ])
        self.table.setAlternatingRowColors(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        # Кнопки экспорта
        export_layout = QHBoxLayout()
        
        self.lbl_count = QLabel("Найдено: 0")
        self.lbl_count.setStyleSheet("font-weight: bold;")
        export_layout.addWidget(self.lbl_count)
        
        export_layout.addStretch()
        
        self.btn_export = QPushButton("📊 Экспорт в Excel")
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_export.setEnabled(False)
        self.btn_export.setMinimumWidth(180)
        export_layout.addWidget(self.btn_export)
        
        self.btn_clear = QPushButton("🗑 Очистить")
        self.btn_clear.clicked.connect(self.clear_results)
        export_layout.addWidget(self.btn_clear)
        
        layout.addLayout(export_layout)
        
        # Проверяем есть ли сохранённая авторизация
        self.check_saved_auth()
    
    def check_saved_auth(self):
        """Проверяем есть ли сохранённая авторизация"""
        if os.path.exists(USER_DATA_DIR):
            self.lbl_auth_status.setText("Статус: Есть сохранённая сессия")
            self.lbl_auth_status.setStyleSheet("color: orange; font-weight: bold;")
            self.btn_search.setEnabled(True)
            self.btn_reset_auth.setVisible(True)
    
    def start_login(self):
        """Начать авторизацию"""
        self.btn_login.setEnabled(False)
        self.btn_confirm_login.setEnabled(False)
        self.lbl_auth_status.setText("Статус: Запуск браузера...")
        self.lbl_auth_status.setStyleSheet("color: orange; font-weight: bold;")
        
        self.login_thread = LoginThread()
        self.login_thread.success.connect(self.on_login_success)
        self.login_thread.error.connect(self.on_login_error)
        self.login_thread.status.connect(self.on_login_status)
        self.login_thread.waiting_for_confirmation.connect(self.on_waiting_for_confirmation)
        self.login_thread.start()
    
    def on_waiting_for_confirmation(self):
        """Браузер открыт, ждём подтверждения от пользователя"""
        self.btn_confirm_login.setEnabled(True)
        self.lbl_auth_status.setText("Статус: Войдите в VK в браузере, затем нажмите 'Я авторизовался'")
        self.lbl_auth_status.setStyleSheet("color: orange; font-weight: bold;")
    
    def confirm_login(self):
        """Пользователь подтвердил что авторизовался"""
        if self.login_thread and self.login_thread.isRunning():
            self.btn_confirm_login.setEnabled(False)
            self.lbl_auth_status.setText("Статус: Проверяем авторизацию...")
            self.lbl_auth_status.setStyleSheet("color: orange; font-weight: bold;")
            self.login_thread.confirm_login()
    
    def on_login_status(self, message: str):
        """Обновление статуса авторизации"""
        self.lbl_auth_status.setText(f"Статус: {message}")
    
    def on_login_success(self):
        """Авторизация успешна"""
        self.is_logged_in = True
        self.lbl_auth_status.setText("Статус: Авторизован ✓")
        self.lbl_auth_status.setStyleSheet("color: green; font-weight: bold;")
        self.btn_search.setEnabled(True)
        self.btn_login.setEnabled(True)
        self.btn_confirm_login.setEnabled(False)
        self.btn_reset_auth.setVisible(True)
        
        QMessageBox.information(
            self, 
            "Успех", 
            "Авторизация успешна!\n\n"
            "Сессия сохранена - при следующем запуске\n"
            "авторизоваться не потребуется."
        )
    
    def on_login_error(self, error: str):
        """Ошибка авторизации"""
        self.lbl_auth_status.setText(f"Статус: Ошибка")
        self.lbl_auth_status.setStyleSheet("color: red; font-weight: bold;")
        self.btn_login.setEnabled(True)
        self.btn_confirm_login.setEnabled(False)
        QMessageBox.critical(self, "Ошибка авторизации", error)
    
    def reset_auth(self):
        """Сбросить сохранённую авторизацию"""
        reply = QMessageBox.question(
            self,
            "Сброс авторизации",
            "Удалить сохранённую сессию VK?\n\n"
            "Потребуется повторная авторизация.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import shutil
            try:
                if os.path.exists(USER_DATA_DIR):
                    shutil.rmtree(USER_DATA_DIR)
                self.is_logged_in = False
                self.lbl_auth_status.setText("Статус: Не авторизован")
                self.lbl_auth_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_search.setEnabled(False)
                self.btn_reset_auth.setVisible(False)
                QMessageBox.information(self, "Готово", "Сессия удалена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")
    
    def start_search(self):
        """Начать поиск"""
        query = self.input_query.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите поисковый запрос")
            return
        
        # Очищаем таблицу
        self.table.setRowCount(0)
        self.communities = []
        
        # Настраиваем UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.btn_search.setEnabled(False)
        self.btn_login.setEnabled(False)
        self.lbl_status.setText("Поиск...")
        self.lbl_status.setStyleSheet("color: blue; font-weight: bold;")
        
        # Запускаем поток поиска
        self.search_thread = SearchThread(
            query=query,
            max_results=self.spin_max.value(),
            fetch_details=self.check_details.isChecked()
        )
        self.search_thread.progress.connect(self.on_search_progress)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()
    
    def on_search_progress(self, message: str):
        """Обновление прогресса поиска"""
        self.lbl_status.setText(message)
        self.lbl_status.setStyleSheet("color: blue; font-weight: bold;")
    
    def on_search_finished(self, communities: List[Dict]):
        """Поиск завершён"""
        self.communities = communities
        self.progress_bar.setVisible(False)
        self.btn_search.setEnabled(True)
        self.btn_login.setEnabled(True)
        
        self.lbl_status.setText(f"✅ Найдено {len(communities)} сообществ")
        self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        self.lbl_count.setText(f"Найдено: {len(communities)}")
        
        # Обновляем таблицу
        self.table.setRowCount(len(communities))
        
        for i, community in enumerate(communities):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(community['name']))
            self.table.setItem(i, 2, QTableWidgetItem(community['url']))
            self.table.setItem(i, 3, QTableWidgetItem(str(community.get('members', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(community.get('phone', '')))
            self.table.setItem(i, 5, QTableWidgetItem(community.get('email', '')))
            self.table.setItem(i, 6, QTableWidgetItem(community.get('site', '')))
            self.table.setItem(i, 7, QTableWidgetItem(community.get('city', '')))
            self.table.setItem(i, 8, QTableWidgetItem("✓" if community.get('verified') else ""))
        
        self.btn_export.setEnabled(len(communities) > 0)
    
    def on_search_error(self, error: str):
        """Ошибка поиска"""
        self.progress_bar.setVisible(False)
        self.btn_search.setEnabled(True)
        self.btn_login.setEnabled(True)
        self.lbl_status.setText(f"❌ Ошибка: {error}")
        self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
        QMessageBox.critical(self, "Ошибка поиска", error)
    
    def export_to_excel(self):
        """Экспорт в Excel"""
        if not self.communities:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить Excel файл",
            f"vk_communities_{time.strftime('%Y-%m-%d')}.xlsx",
            "Excel файлы (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Сообщества"
            
            # Заголовки
            headers = ["№", "Название", "Ссылка", "Участники", "Телефон", 
                      "Email", "Сайт", "Город", "Верифицировано"]
            ws.append(headers)
            
            # Стиль заголовков
            header_fill = PatternFill(start_color="4C75A3", end_color="4C75A3", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
            
            # Данные
            for i, community in enumerate(self.communities, 1):
                ws.append([
                    i,
                    community['name'],
                    community['url'],
                    community.get('members', ''),
                    community.get('phone', ''),
                    community.get('email', ''),
                    community.get('site', ''),
                    community.get('city', ''),
                    "Да" if community.get('verified') else "Нет"
                ])
            
            # Ширина колонок
            ws.column_dimensions['A'].width = 5
            ws.column_dimensions['B'].width = 40
            ws.column_dimensions['C'].width = 35
            ws.column_dimensions['D'].width = 12
            ws.column_dimensions['E'].width = 18
            ws.column_dimensions['F'].width = 25
            ws.column_dimensions['G'].width = 30
            ws.column_dimensions['H'].width = 15
            ws.column_dimensions['I'].width = 12
            
            # Лист сводки
            ws2 = wb.create_sheet("Сводка")
            ws2.append(["Параметр", "Значение"])
            ws2.append(["Всего сообществ", len(self.communities)])
            ws2.append(["С телефонами", sum(1 for c in self.communities if c.get('phone'))])
            ws2.append(["С email", sum(1 for c in self.communities if c.get('email'))])
            ws2.append(["С сайтами", sum(1 for c in self.communities if c.get('site'))])
            ws2.append(["Верифицированные", sum(1 for c in self.communities if c.get('verified'))])
            ws2.append(["Общее число участников", sum(c.get('members', 0) for c in self.communities)])
            ws2.append(["Дата экспорта", time.strftime('%Y-%m-%d %H:%M')])
            
            ws2.column_dimensions['A'].width = 25
            ws2.column_dimensions['B'].width = 20
            
            wb.save(file_path)
            QMessageBox.information(self, "Успех", f"Файл сохранён:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
    
    def clear_results(self):
        """Очистить результаты"""
        self.table.setRowCount(0)
        self.communities = []
        self.btn_export.setEnabled(False)
        self.lbl_status.setText("")
        self.lbl_count.setText("Найдено: 0")
    
    def closeEvent(self, event):
        """Закрытие приложения"""
        # Останавливаем потоки
        if self.login_thread and self.login_thread.isRunning():
            self.login_thread.quit()
            self.login_thread.wait(3000)
        
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.stop()
            self.search_thread.quit()
            self.search_thread.wait(3000)
        
        event.accept()


def main():
    """Точка входа"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Тёмная тема
    palette = app.palette()
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
