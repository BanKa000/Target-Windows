#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VK Community Finder - Поиск сообществ ВКонтакте
Десктопное приложение для Windows
"""

import sys
import time
import re
from typing import List, Dict
from threading import Thread

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, 
                             QProgressBar, QMessageBox, QGroupBox, QSpinBox,
                             QComboBox, QCheckBox, QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from playwright.sync_api import sync_playwright, Browser
import openpyxl
from openpyxl.styles import Font, PatternFill


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VK Community Finder - Поиск сообществ ВКонтакте")
        self.setGeometry(100, 100, 1400, 900)
        
        # Playwright инициализируется один раз
        self.playwright = None
        self.browser = None
        self.communities = []
        
        self.init_ui()
        
        # Таймер для обновления GUI во время парсинга
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_parsing_status)
        
    def init_ui(self):
        """Инициализация интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Группа авторизации
        auth_group = QGroupBox("Авторизация")
        auth_layout = QHBoxLayout()
        
        self.btn_login = QPushButton("Войти ВКонтакте")
        self.btn_login.clicked.connect(self.login_to_vk)
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
        
        # Статус парсинга
        self.parsing_active = False
        self.parsing_thread = None
        
    def login_to_vk(self):
        """Авторизация ВКонтакте"""
        try:
            self.lbl_auth_status.setText("Статус: Запускаем браузер...")
            QApplication.processEvents()
            
            # Инициализируем Playwright один раз
            if not self.playwright:
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch(
                    headless=False,
                    args=['--start-maximized']
                )
            
            # Открываем страницу входа
            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            page.goto("https://vk.com/login")
            
            self.lbl_auth_status.setText("Статус: Войдите в аккаунт ВКонтакте в открывшемся окне")
            self.lbl_auth_status.setStyleSheet("color: orange;")
            
            # Ждём пока пользователь войдёт
            QMessageBox.information(
                self, 
                "Авторизация", 
                "Войдите в свой аккаунт ВКонтакте в открывшемся браузере.\n\n"
                "После успешного входа нажмите OK."
            )
            
            # Проверяем что авторизация успешна
            current_url = page.url
            if 'login' not in current_url:
                self.lbl_auth_status.setText("Статус: Авторизован ✓")
                self.lbl_auth_status.setStyleSheet("color: green;")
                self.btn_search.setEnabled(True)
                
                # Закрываем страницу входа, но оставляем браузер
                page.close()
                context.close()
                
                QMessageBox.information(self, "Успех", "Авторизация успешна! Теперь вы можете искать сообщества.")
            else:
                self.lbl_auth_status.setText("Статус: Авторизация не завершена")
                self.lbl_auth_status.setStyleSheet("color: red;")
                page.close()
                context.close()
                
        except Exception as e:
            self.lbl_auth_status.setText("Статус: Ошибка")
            self.lbl_auth_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Ошибка авторизации", f"Не удалось авторизоваться:\n{e}")
    
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
        self.progress_bar.setRange(0, 0)
        self.btn_search.setEnabled(False)
        self.lbl_status.setText("Поиск...")
        self.parsing_active = True
        
        # Запускаем парсинг в отдельном потоке
        self.parsing_thread = Thread(
            target=self.do_parsing,
            args=(query, self.spin_max.value(), self.check_details.isChecked()),
            daemon=True
        )
        self.parsing_thread.start()
        
        # Запускаем таймер для обновления GUI
        self.update_timer.start(100)
    
    def do_parsing(self, query: str, max_results: int, fetch_details: bool):
        """Выполнить парсинг (в отдельном потоке)"""
        try:
            # Ищем сообщества
            self.lbl_status.setText("Открываем страницу поиска...")
            communities = self.search_communities(query, max_results)
            
            if not communities:
                self.lbl_status.setText("Сообщества не найдены")
                self.parsing_active = False
                return
            
            # Собираем детали если нужно
            if fetch_details:
                communities = self.fetch_all_details(communities)
            
            self.communities = communities
            self.lbl_status.setText(f"Найдено {len(communities)} сообществ")
            
        except Exception as e:
            self.lbl_status.setText(f"Ошибка: {e}")
        finally:
            self.parsing_active = False
    
    def search_communities(self, query: str, max_results: int) -> List[Dict]:
        """Поиск сообществ VK"""
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # Правильный URL для поиска групп
            url = f"https://vk.com/groups?q={query}"
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Прокручиваем страницу для загрузки результатов
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
            
            # Парсим результаты
            communities = []
            seen_ids = set()
            
            # Ищем все ссылки на группы
            links = page.query_selector_all('a[href*="/club"], a[href^="/"][class*="group"]')
            
            for link in links:
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
                    
                    if len(communities) >= max_results:
                        break
                        
                except Exception:
                    continue
            
            return communities
            
        finally:
            page.close()
            context.close()
    
    def fetch_all_details(self, communities: List[Dict]) -> List[Dict]:
        """Получить детали для всех сообществ"""
        total = len(communities)
        
        for i, community in enumerate(communities):
            self.lbl_status.setText(f"Собираем контакты: {i+1}/{total} - {community['name']}")
            
            try:
                details = self.fetch_community_details(community['screen_name'])
                community.update(details)
            except Exception:
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
    
    def check_parsing_status(self):
        """Проверка статуса парсинга и обновление GUI"""
        if not self.parsing_active:
            self.update_timer.stop()
            self.progress_bar.setVisible(False)
            self.btn_search.setEnabled(True)
            
            # Обновляем таблицу
            self.update_table()
    
    def update_table(self):
        """Обновить таблицу результатов"""
        self.table.setRowCount(len(self.communities))
        
        for i, community in enumerate(self.communities):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(community['name']))
            self.table.setItem(i, 2, QTableWidgetItem(community['url']))
            self.table.setItem(i, 3, QTableWidgetItem(str(community.get('members', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(community.get('phone', '')))
            self.table.setItem(i, 5, QTableWidgetItem(community.get('email', '')))
            self.table.setItem(i, 6, QTableWidgetItem(community.get('site', '')))
            self.table.setItem(i, 7, QTableWidgetItem(community.get('city', '')))
            self.table.setItem(i, 8, QTableWidgetItem("✓" if community.get('verified') else ""))
        
        self.btn_export.setEnabled(len(self.communities) > 0)
    
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
        # Закрываем браузер
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        
        # Останавливаем Playwright
        if self.playwright:
            try:
                self.playwright.stop()
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
