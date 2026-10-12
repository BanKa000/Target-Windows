#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VK Community Finder - Поиск сообществ ВКонтакте
Десктопное приложение для Windows
"""

import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QTableWidget, QTableWidgetItem, 
                             QProgressBar, QMessageBox, QGroupBox, QSpinBox,
                             QComboBox, QCheckBox, QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from playwright.sync_api import sync_playwright, Page, Browser
import openpyxl
from openpyxl.styles import Font, PatternFill


class VKParserThread(QThread):
    """Поток для парсинга VK без блокировки GUI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, browser: Browser, query: str, max_results: int, 
                 group_type: str, fetch_details: bool):
        super().__init__()
        self.browser = browser
        self.query = query
        self.max_results = max_results
        self.group_type = group_type
        self.fetch_details = fetch_details
        self.running = True
        
    def stop(self):
        self.running = False
        
    def run(self):
        try:
            communities = self.search_communities()
            if self.running and self.fetch_details:
                communities = self.fetch_all_details(communities)
            if self.running:
                self.finished.emit(communities)
        except Exception as e:
            self.error.emit(str(e))
    
    def search_communities(self) -> List[Dict]:
        """Поиск сообществ VK"""
        self.progress.emit("Открываем страницу поиска...")
        
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # Правильный URL для поиска групп
            url = f"https://vk.com/groups?q={self.query}"
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Прокручиваем страницу для загрузки результатов
            self.progress.emit("Загружаем результаты поиска...")
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
            
            # Парсим результаты
            communities = []
            seen_ids = set()
            
            # Ищем все ссылки на группы
            links = page.query_selector_all('a[href*="/club"], a[href^="/"][class*="group"]')
            
            for link in links:
                if not self.running:
                    break
                    
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Извлекаем ID или название
                    if '/club' in href:
                        match = re.search(r'/club(\d+)', href)
                        if match:
                            group_id = int(match.group(1))
                            screen_name = f"club{group_id}"
                        else:
                            continue
                    else:
                        screen_name = href.strip('/')
                        group_id = hash(screen_name)
                    
                    if group_id in seen_ids:
                        continue
                    seen_ids.add(group_id)
                    
                    # Получаем название
                    name_elem = link.query_selector('span, div')
                    name = name_elem.inner_text() if name_elem else screen_name
                    name = name.strip()
                    
                    if not name or len(name) < 2:
                        continue
                    
                    communities.append({
                        'id': group_id,
                        'name': name,
                        'screen_name': screen_name,
                        'url': f"https://vk.com/{screen_name}",
                        'members': 0,
                        'description': '',
                        'phone': '',
                        'email': '',
                        'site': '',
                        'city': '',
                        'verified': False
                    })
                    
                    if len(communities) >= self.max_results:
                        break
                        
                except Exception as e:
                    continue
            
            self.progress.emit(f"Найдено {len(communities)} сообществ")
            return communities
            
        finally:
            page.close()
            context.close()
    
    def fetch_all_details(self, communities: List[Dict]) -> List[Dict]:
        """Получить детали для всех сообществ"""
        total = len(communities)
        
        for i, community in enumerate(communities):
            if not self.running:
                break
                
            self.progress.emit(f"Собираем контакты: {i+1}/{total} - {community['name']}")
            
            try:
                details = self.fetch_community_details(community['screen_name'])
                community.update(details)
            except Exception as e:
                pass
            
            # Задержка чтобы не перегружать VK
            if i < total - 1:
                time.sleep(1.5)
        
        return communities
    
    def fetch_community_details(self, screen_name: str) -> Dict:
        """Получить детали конкретного сообщества"""
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            url = f"https://vk.com/{screen_name}"
            page.goto(url, wait_until='networkidle', timeout=15000)
            time.sleep(1)
            
            details = {}
            
            # Извлекаем телефон
            phone_elem = page.query_selector('a[href^="tel:"]')
            if phone_elem:
                href = phone_elem.get_attribute('href')
                if href:
                    details['phone'] = href.replace('tel:', '').strip()
            
            # Извлекаем email
            email_pattern = r'[\w.+-]+@[\w.-]+\.\w{2,}'
            emails = page.evaluate(f'document.body.innerText.match(/{email_pattern}/g) || []')
            for email in emails:
                if 'vk.com' not in email and 'vk.ru' not in email:
                    details['email'] = email
                    break
            
            # Извлекаем сайт
            site_elem = page.query_selector('a[href^="http"]:not([href*="vk.com"])')
            if site_elem:
                href = site_elem.get_attribute('href')
                if href and 'vk.com' not in href:
                    details['site'] = href
            
            # Извлекаем количество участников
            members_text = page.inner_text('body')
            match = re.search(r'(\d[\d\s]*)\s*(?:участник|подписчик|человек)', members_text, re.I)
            if match:
                details['members'] = int(match.group(1).replace(' ', ''))
            
            # Извлекаем город
            city_patterns = [
                r'город[:\s]+([^,\n]+)',
                r'г\.\s*([^,\n]+)'
            ]
            for pattern in city_patterns:
                match = re.search(pattern, members_text, re.I)
                if match:
                    details['city'] = match.group(1).strip()
                    break
            
            # Проверяем верификацию
            if page.query_selector('[class*="verified"]'):
                details['verified'] = True
            
            return details
            
        finally:
            page.close()
            context.close()


class LoginWindow(QWidget):
    """Окно авторизации VK"""
    login_success = pyqtSignal(object)  # Передаём browser
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация ВКонтакте")
        self.setGeometry(100, 100, 1200, 800)
        self.browser = None
        self.playwright = None
        
        layout = QVBoxLayout()
        
        # Инструкция
        info = QLabel(
            "<h3>Авторизация ВКонтакте</h3>"
            "<p>1. Войдите в свой аккаунт ВКонтакте в открывшемся окне</p>"
            "<p>2. После успешной авторизации нажмите кнопку 'Завершить вход'</p>"
            "<p>3. Сессия сохранится для дальнейшей работы</p>"
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_open_vk = QPushButton("Открыть ВКонтакте")
        self.btn_open_vk.clicked.connect(self.open_vk)
        btn_layout.addWidget(self.btn_open_vk)
        
        self.btn_finish = QPushButton("Завершить вход")
        self.btn_finish.clicked.connect(self.finish_login)
        self.btn_finish.setEnabled(False)
        btn_layout.addWidget(self.btn_finish)
        
        layout.addLayout(btn_layout)
        
        # Статус
        self.status = QLabel("Статус: Ожидание...")
        layout.addWidget(self.status)
        
        self.setLayout(layout)
        
    def open_vk(self):
        """Открыть VK в браузере"""
        try:
            self.status.setText("Статус: Запускаем браузер...")
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=['--start-maximized']
            )
            
            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            page.goto("https://vk.com/login")
            
            self.status.setText("Статус: Войдите в аккаунт ВКонтакте")
            self.btn_finish.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить браузер:\n{e}")
    
    def finish_login(self):
        """Завершить авторизацию"""
        if self.browser:
            self.status.setText("Статус: Авторизация завершена")
            self.login_success.emit(self.browser)
            self.close()
    
    def closeEvent(self, event):
        """Закрыть браузер при закрытии окна"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass
        event.accept()


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VK Community Finder - Поиск сообществ ВКонтакте")
        self.setGeometry(100, 100, 1400, 900)
        
        self.browser = None
        self.parser_thread = None
        self.communities = []
        
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
        self.btn_login.clicked.connect(self.show_login_window)
        auth_layout.addWidget(self.btn_login)
        
        self.lbl_auth_status = QLabel("Статус: Не авторизован")
        self.lbl_auth_status.setStyleSheet("color: red;")
        auth_layout.addWidget(self.lbl_auth_status)
        
        auth_layout.addStretch()
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Группа поиска
        search_group = QGroupBox("Параметры поиска")
        search_layout = QVBoxLayout()
        
        # Строка поиска
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Поисковый запрос:"))
        self.input_query = QLineEdit()
        self.input_query.setPlaceholderText("Введите ключевые слова (например: автосервис, доставка)")
        search_row.addWidget(self.input_query)
        
        self.btn_search = QPushButton("Найти")
        self.btn_search.clicked.connect(self.start_search)
        self.btn_search.setEnabled(False)
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
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)
        
        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "№", "Название", "Ссылка", "Участники", "Телефон", 
            "Email", "Сайт", "Город", "Верифицировано"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        # Кнопки экспорта
        export_layout = QHBoxLayout()
        
        self.btn_export = QPushButton("Экспорт в Excel")
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_export.setEnabled(False)
        export_layout.addWidget(self.btn_export)
        
        self.btn_clear = QPushButton("Очистить")
        self.btn_clear.clicked.connect(self.clear_results)
        export_layout.addWidget(self.btn_clear)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
    def show_login_window(self):
        """Показать окно авторизации"""
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, browser):
        """Обработка успешной авторизации"""
        self.browser = browser
        self.lbl_auth_status.setText("Статус: Авторизован ✓")
        self.lbl_auth_status.setStyleSheet("color: green;")
        self.btn_search.setEnabled(True)
        QMessageBox.information(self, "Успех", "Авторизация успешна! Теперь вы можете искать сообщества.")
    
    def start_search(self):
        """Начать поиск"""
        query = self.input_query.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите поисковый запрос")
            return
        
        if not self.browser:
            QMessageBox.warning(self, "Ошибка", "Сначала авторизуйтесь ВКонтакте")
            return
        
        # Очищаем таблицу
        self.table.setRowCount(0)
        self.communities = []
        
        # Настраиваем UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределённый прогресс
        self.btn_search.setEnabled(False)
        self.lbl_status.setText("Поиск...")
        
        # Запускаем поток парсинга
        self.parser_thread = VKParserThread(
            browser=self.browser,
            query=query,
            max_results=self.spin_max.value(),
            group_type=self.combo_type.currentText(),
            fetch_details=self.check_details.isChecked()
        )
        self.parser_thread.progress.connect(self.update_status)
        self.parser_thread.finished.connect(self.on_search_finished)
        self.parser_thread.error.connect(self.on_search_error)
        self.parser_thread.start()
    
    def update_status(self, message: str):
        """Обновить статус"""
        self.lbl_status.setText(message)
    
    def on_search_finished(self, communities: List[Dict]):
        """Поиск завершён"""
        self.communities = communities
        self.progress_bar.setVisible(False)
        self.btn_search.setEnabled(True)
        self.lbl_status.setText(f"Найдено {len(communities)} сообществ")
        
        # Заполняем таблицу
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
        self.lbl_status.setText(f"Ошибка: {error}")
        QMessageBox.critical(self, "Ошибка поиска", error)
    
    def export_to_excel(self):
        """Экспорт в Excel"""
        if not self.communities:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить Excel файл",
            f"vk_communities_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
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
    
    def closeEvent(self, event):
        """Закрытие приложения"""
        if self.parser_thread and self.parser_thread.isRunning():
            self.parser_thread.stop()
            self.parser_thread.wait()
        
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        
        event.accept()


def main():
    """Точка входа"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
