#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VK Community Finder - Поиск сообществ ВКонтакте
"""

import sys
import time
import re
import os
from pathlib import Path
from typing import List, Dict

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QProgressBar, 
                             QMessageBox, QGroupBox, QSpinBox, QComboBox, 
                             QCheckBox, QFileDialog, QHeaderView, QDialog, 
                             QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from playwright.sync_api import sync_playwright
import openpyxl
from openpyxl.styles import Font, PatternFill
import vk_api


USER_DATA_DIR = str(Path.home() / ".vk_finder_profile")


class LoginDialog(QDialog):
    """Диалог ввода логина/пароля"""
    
    def __init__(self, parent=None, need_code=False):
        super().__init__(parent)
        self.setWindowTitle("Двухфакторная авторизация" if need_code else "Вход ВКонтакте")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        if need_code:
            layout.addWidget(QLabel("Введите код из приложения:"))
            form = QFormLayout()
            self.code_input = QLineEdit()
            form.addRow("Код:", self.code_input)
            layout.addLayout(form)
            self.code_input.setFocus()
        else:
            layout.addWidget(QLabel("Введите данные для входа:"))
            form = QFormLayout()
            
            self.login_input = QLineEdit()
            self.login_input.setPlaceholderText("Телефон или email")
            form.addRow("Логин:", self.login_input)
            
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Пароль:", self.password_input)
            
            layout.addLayout(form)
            self.login_input.setFocus()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_credentials(self):
        if hasattr(self, 'code_input'):
            return '', '', self.code_input.text().strip()
        return self.login_input.text().strip(), self.password_input.text(), ''


class BrowserLoginThread(QThread):
    """Авторизация через браузер"""
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
                
                self.status.emit("Войдите в VK в браузере")
                self.waiting_for_confirmation.emit()
                
                while not hasattr(self, '_user_confirmed'):
                    time.sleep(0.5)
                
                time.sleep(2)
                
                cookies = context.cookies()
                has_auth = any(c['name'] in ['remixsid', 'remixlang'] for c in cookies)
                
                if has_auth:
                    context.close()
                    self.success.emit()
                else:
                    page.goto("https://vk.com/feed", wait_until='domcontentloaded', timeout=10000)
                    time.sleep(2)
                    
                    if 'login' not in page.url:
                        context.close()
                        self.success.emit()
                    else:
                        context.close()
                        self.error.emit("Авторизация не удалась")
                
        except Exception as e:
            self.error.emit(f"Ошибка: {e}")
    
    def confirm_login(self):
        self._user_confirmed = True


class ApiLoginThread(QThread):
    """Авторизация через VK API"""
    success = pyqtSignal()
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    need_2fa = pyqtSignal()
    
    def __init__(self, login: str, password: str, code: str = ''):
        super().__init__()
        self.login = login
        self.password = password
        self.code = code
        
    def run(self):
        try:
            self.status.emit("Авторизация через VK API...")
            
            vk_session = vk_api.VkApi(
                login=self.login,
                password=self.password,
                app_id=2685278,
                auth_token_code=self.code if self.code else None
            )
            vk_session.auth(token_only=False)
            
            token = vk_session.token['access_token']
            token_file = Path(USER_DATA_DIR) / 'api_token.txt'
            token_file.parent.mkdir(parents=True, exist_ok=True)
            token_file.write_text(token)
            
            self.success.emit()
            
        except vk_api.AuthError as e:
            if '2fa' in str(e).lower():
                self.need_2fa.emit()
            else:
                self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Ошибка: {e}")


class SearchThread(QThread):
    """Поиск сообществ"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, query: str, max_results: int, fetch_details: bool):
        super().__init__()
        self.query = query
        self.max_results = max_results
        self.fetch_details = fetch_details
        self._stop = False
        
    def stop(self):
        self._stop = True
    
    def run(self):
        try:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=USER_DATA_DIR,
                    headless=False,
                    viewport={'width': 1920, 'height': 1080}
                )
                
                try:
                    communities = self._search(context)
                    
                    if not self._stop and self.fetch_details and communities:
                        communities = self._fetch_details(context, communities)
                    
                    if not self._stop:
                        self.finished.emit(communities)
                finally:
                    context.close()
                    
        except Exception as e:
            self.error.emit(str(e))
    
    def _search(self, context) -> List[Dict]:
        self.progress.emit("Поиск сообществ...")
        
        page = context.new_page()
        try:
            page.goto(f"https://vk.com/groups?q={self.query}", wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                if self._stop:
                    return []
            
            communities = []
            seen = set()
            
            for link in page.query_selector_all('a[href*="/club"]'):
                if self._stop:
                    break
                
                href = link.get_attribute('href') or ''
                match = re.search(r'/club(\d+)', href)
                if not match:
                    continue
                
                group_id = int(match.group(1))
                if group_id in seen:
                    continue
                seen.add(group_id)
                
                name_elem = link.query_selector('span, div')
                name = name_elem.inner_text().strip() if name_elem else f"club{group_id}"
                
                if not name or len(name) < 2:
                    continue
                
                communities.append({
                    'id': group_id,
                    'name': name,
                    'screen_name': f"club{group_id}",
                    'url': f"https://vk.com/club{group_id}",
                    'members': 0,
                    'phone': '',
                    'email': '',
                    'site': '',
                    'city': '',
                    'verified': False
                })
                
                if len(communities) >= self.max_results:
                    break
            
            self.progress.emit(f"Найдено {len(communities)} сообществ")
            return communities
            
        finally:
            page.close()
    
    def _fetch_details(self, context, communities: List[Dict]) -> List[Dict]:
        total = len(communities)
        
        for i, community in enumerate(communities):
            if self._stop:
                break
            
            self.progress.emit(f"Контакты: {i+1}/{total}")
            
            try:
                details = self._get_details(context, community['screen_name'])
                community.update(details)
            except:
                pass
            
            if i < total - 1:
                time.sleep(1.5)
        
        return communities
    
    def _get_details(self, context, screen_name: str) -> Dict:
        page = context.new_page()
        try:
            page.goto(f"https://vk.com/{screen_name}", wait_until='domcontentloaded', timeout=15000)
            time.sleep(2)
            
            details = {}
            text = page.inner_text('body')
            
            # Телефон
            phone = page.query_selector('a[href^="tel:"]')
            if phone:
                details['phone'] = phone.get_attribute('href').replace('tel:', '').strip()
            else:
                match = re.search(r'([\+]?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})', text)
                if match:
                    details['phone'] = match.group(1).strip()
            
            # Email
            match = re.search(r'([\w.+-]+@[\w.-]+\.\w{2,})', text)
            if match and 'vk.com' not in match.group(1):
                details['email'] = match.group(1)
            
            # Сайт
            site = page.query_selector('a[href^="http"]:not([href*="vk.com"])')
            if site:
                href = site.get_attribute('href')
                if href and 'vk.com' not in href:
                    details['site'] = href
            
            # Участники
            match = re.search(r'(\d[\d\s]*)\s*(?:участник|подписчик)', text, re.I)
            if match:
                details['members'] = int(match.group(1).replace(' ', ''))
            
            # Город
            match = re.search(r'город[:\s]+([^,\n]+)', text, re.I)
            if match:
                details['city'] = match.group(1).strip()
            
            # Верификация
            if page.query_selector('[class*="verified"]'):
                details['verified'] = True
            
            return details
            
        finally:
            page.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VK Community Finder")
        self.setGeometry(100, 100, 1400, 900)
        
        self.communities = []
        self.browser_thread = None
        self.api_thread = None
        self.search_thread = None
        
        self.init_ui()
        self.check_saved_auth()
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Авторизация
        auth_group = QGroupBox("Авторизация")
        auth_layout = QHBoxLayout()
        
        self.btn_browser = QPushButton("Войти ВКонтакте")
        self.btn_browser.clicked.connect(self.start_browser_login)
        self.btn_browser.setStyleSheet("background-color: #0077FF; color: white; font-weight: bold; padding: 8px 20px;")
        auth_layout.addWidget(self.btn_browser)
        
        self.btn_api = QPushButton("Войти по логину/паролю")
        self.btn_api.clicked.connect(self.start_api_login)
        self.btn_api.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px 20px;")
        auth_layout.addWidget(self.btn_api)
        
        self.btn_confirm = QPushButton("✓ Я авторизовался")
        self.btn_confirm.clicked.connect(self.confirm_login)
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 20px;")
        auth_layout.addWidget(self.btn_confirm)
        
        self.lbl_status = QLabel("Статус: Не авторизован")
        self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
        auth_layout.addWidget(self.lbl_status)
        
        auth_layout.addStretch()
        
        self.btn_reset = QPushButton("Сбросить")
        self.btn_reset.clicked.connect(self.reset_auth)
        self.btn_reset.setVisible(False)
        auth_layout.addWidget(self.btn_reset)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Поиск
        search_group = QGroupBox("Поиск")
        search_layout = QVBoxLayout()
        
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Запрос:"))
        self.input_query = QLineEdit()
        self.input_query.setPlaceholderText("Введите ключевые слова...")
        self.input_query.returnPressed.connect(self.start_search)
        search_row.addWidget(self.input_query)
        
        self.btn_search = QPushButton("Найти")
        self.btn_search.clicked.connect(self.start_search)
        self.btn_search.setEnabled(False)
        self.btn_search.setMinimumWidth(120)
        search_row.addWidget(self.btn_search)
        
        search_layout.addLayout(search_row)
        
        settings_row = QHBoxLayout()
        settings_row.addWidget(QLabel("Макс:"))
        self.spin_max = QSpinBox()
        self.spin_max.setRange(10, 500)
        self.spin_max.setValue(50)
        settings_row.addWidget(self.spin_max)
        
        self.check_details = QCheckBox("Собирать контакты")
        self.check_details.setChecked(True)
        settings_row.addWidget(self.check_details)
        
        settings_row.addStretch()
        search_layout.addLayout(settings_row)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Прогресс
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        self.lbl_progress = QLabel("")
        layout.addWidget(self.lbl_progress)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["№", "Название", "Ссылка", "Участники", "Телефон", "Email", "Сайт", "Город", "✓"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Экспорт
        export_layout = QHBoxLayout()
        
        self.lbl_count = QLabel("Найдено: 0")
        self.lbl_count.setStyleSheet("font-weight: bold;")
        export_layout.addWidget(self.lbl_count)
        
        export_layout.addStretch()
        
        self.btn_export = QPushButton("Экспорт в Excel")
        self.btn_export.clicked.connect(self.export_excel)
        self.btn_export.setEnabled(False)
        export_layout.addWidget(self.btn_export)
        
        self.btn_clear = QPushButton("Очистить")
        self.btn_clear.clicked.connect(self.clear)
        export_layout.addWidget(self.btn_clear)
        
        layout.addLayout(export_layout)
    
    def check_saved_auth(self):
        if os.path.exists(USER_DATA_DIR):
            self.lbl_status.setText("Статус: Есть сохранённая сессия")
            self.lbl_status.setStyleSheet("color: orange;")
            self.btn_search.setEnabled(True)
            self.btn_reset.setVisible(True)
    
    def start_browser_login(self):
        self.btn_browser.setEnabled(False)
        self.btn_api.setEnabled(False)
        self.btn_confirm.setEnabled(False)
        self.lbl_status.setText("Запуск браузера...")
        self.lbl_status.setStyleSheet("color: orange;")
        
        self.browser_thread = BrowserLoginThread()
        self.browser_thread.success.connect(self.on_login_success)
        self.browser_thread.error.connect(self.on_login_error)
        self.browser_thread.status.connect(self.update_status)
        self.browser_thread.waiting_for_confirmation.connect(self.on_waiting)
        self.browser_thread.start()
    
    def start_api_login(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            login, password, code = dialog.get_credentials()
            
            self.btn_browser.setEnabled(False)
            self.btn_api.setEnabled(False)
            self.lbl_status.setText("Авторизация...")
            self.lbl_status.setStyleSheet("color: orange;")
            
            self.api_thread = ApiLoginThread(login, password, code)
            self.api_thread.success.connect(self.on_login_success)
            self.api_thread.error.connect(self.on_login_error)
            self.api_thread.status.connect(self.update_status)
            self.api_thread.need_2fa.connect(self.on_need_2fa)
            self.api_thread.start()
    
    def on_need_2fa(self):
        dialog = LoginDialog(self, need_code=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            login, password, code = dialog.get_credentials()
            
            self.api_thread = ApiLoginThread(login, password, code)
            self.api_thread.success.connect(self.on_login_success)
            self.api_thread.error.connect(self.on_login_error)
            self.api_thread.status.connect(self.update_status)
            self.api_thread.need_2fa.connect(self.on_need_2fa)
            self.api_thread.start()
        else:
            self.btn_browser.setEnabled(True)
            self.btn_api.setEnabled(True)
    
    def on_waiting(self):
        self.btn_confirm.setEnabled(True)
        self.lbl_status.setText("Войдите в VK, затем нажмите 'Я авторизовался'")
    
    def confirm_login(self):
        if self.browser_thread and self.browser_thread.isRunning():
            self.btn_confirm.setEnabled(False)
            self.lbl_status.setText("Проверка...")
            self.browser_thread.confirm_login()
    
    def update_status(self, msg):
        self.lbl_status.setText(msg)
    
    def on_login_success(self):
        self.lbl_status.setText("Авторизован ✓")
        self.lbl_status.setStyleSheet("color: green;")
        self.btn_search.setEnabled(True)
        self.btn_browser.setEnabled(True)
        self.btn_api.setEnabled(True)
        self.btn_confirm.setEnabled(False)
        self.btn_reset.setVisible(True)
        QMessageBox.information(self, "Успех", "Авторизация успешна!")
    
    def on_login_error(self, error):
        self.lbl_status.setText("Ошибка")
        self.lbl_status.setStyleSheet("color: red;")
        self.btn_browser.setEnabled(True)
        self.btn_api.setEnabled(True)
        self.btn_confirm.setEnabled(False)
        QMessageBox.critical(self, "Ошибка", error)
    
    def reset_auth(self):
        if QMessageBox.question(self, "Сброс", "Удалить сессию?") == QMessageBox.StandardButton.Yes:
            import shutil
            try:
                if os.path.exists(USER_DATA_DIR):
                    shutil.rmtree(USER_DATA_DIR)
                self.lbl_status.setText("Не авторизован")
                self.lbl_status.setStyleSheet("color: red;")
                self.btn_search.setEnabled(False)
                self.btn_reset.setVisible(False)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def start_search(self):
        query = self.input_query.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите запрос")
            return
        
        self.table.setRowCount(0)
        self.communities = []
        
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_search.setEnabled(False)
        self.lbl_progress.setText("Поиск...")
        
        self.search_thread = SearchThread(query, self.spin_max.value(), self.check_details.isChecked())
        self.search_thread.progress.connect(self.update_progress)
        self.search_thread.finished.connect(self.on_search_done)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()
    
    def update_progress(self, msg):
        self.lbl_progress.setText(msg)
    
    def on_search_done(self, communities):
        self.communities = communities
        self.progress.setVisible(False)
        self.btn_search.setEnabled(True)
        self.lbl_progress.setText(f"Найдено {len(communities)}")
        self.lbl_count.setText(f"Найдено: {len(communities)}")
        
        self.table.setRowCount(len(communities))
        for i, c in enumerate(communities):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(c['name']))
            self.table.setItem(i, 2, QTableWidgetItem(c['url']))
            self.table.setItem(i, 3, QTableWidgetItem(str(c.get('members', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(c.get('phone', '')))
            self.table.setItem(i, 5, QTableWidgetItem(c.get('email', '')))
            self.table.setItem(i, 6, QTableWidgetItem(c.get('site', '')))
            self.table.setItem(i, 7, QTableWidgetItem(c.get('city', '')))
            self.table.setItem(i, 8, QTableWidgetItem("✓" if c.get('verified') else ""))
        
        self.btn_export.setEnabled(len(communities) > 0)
    
    def on_search_error(self, error):
        self.progress.setVisible(False)
        self.btn_search.setEnabled(True)
        self.lbl_progress.setText(f"Ошибка: {error}")
        QMessageBox.critical(self, "Ошибка", error)
    
    def export_excel(self):
        if not self.communities:
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", f"vk_{time.strftime('%Y-%m-%d')}.xlsx", "Excel (*.xlsx)")
        if not path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Сообщества"
            
            headers = ["№", "Название", "Ссылка", "Участники", "Телефон", "Email", "Сайт", "Город", "Верифицировано"]
            ws.append(headers)
            
            fill = PatternFill(start_color="4C75A3", end_color="4C75A3", fill_type="solid")
            font = Font(bold=True, color="FFFFFF")
            
            for cell in ws[1]:
                cell.fill = fill
                cell.font = font
            
            for i, c in enumerate(self.communities, 1):
                ws.append([i, c['name'], c['url'], c.get('members', ''), c.get('phone', ''), 
                          c.get('email', ''), c.get('site', ''), c.get('city', ''), 
                          "Да" if c.get('verified') else "Нет"])
            
            for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
                ws.column_dimensions[col].width = 15 if col != 'B' else 40
            
            wb.save(path)
            QMessageBox.information(self, "Успех", f"Сохранено:\n{path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def clear(self):
        self.table.setRowCount(0)
        self.communities = []
        self.btn_export.setEnabled(False)
        self.lbl_progress.setText("")
        self.lbl_count.setText("Найдено: 0")
    
    def closeEvent(self, event):
        if self.browser_thread and self.browser_thread.isRunning():
            self.browser_thread.quit()
            self.browser_thread.wait(3000)
        
        if self.api_thread and self.api_thread.isRunning():
            self.api_thread.quit()
            self.api_thread.wait(3000)
        
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.stop()
            self.search_thread.quit()
            self.search_thread.wait(3000)
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
