const { app, BrowserWindow, Menu, session } = require('electron');
const path = require('path');

// Отключаем аппаратное ускорение для лучшей совместимости
app.disableHardwareAcceleration();

let mainWindow;

// Настраиваем сессию для обхода CORS
function setupSession() {
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    // Удаляем CSP заголовки, которые могут блокировать запросы
    delete details.responseHeaders['Content-Security-Policy'];
    delete details.responseHeaders['content-security-policy'];
    delete details.responseHeaders['X-Frame-Options'];
    delete details.responseHeaders['x-frame-options'];
    
    callback({ responseHeaders: details.responseHeaders });
  });

  // Разрешаем все запросы
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(true);
  });
}

function createWindow() {
  // Создаём окно браузера
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    title: 'VK Community Finder - Поиск сообществ ВК',
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false, // Разрешаем CORS для работы с VK
      allowRunningInsecureContent: true,
      preload: path.join(__dirname, 'preload.js')
    },
    autoHideMenuBar: true,
    show: false
  });

  // Загружаем index.html из папки dist
  const isDev = process.env.NODE_ENV === 'development';
  
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Показываем окно когда оно готово
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Открываем DevTools в режиме разработки
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Обработчик закрытия окна
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Логируем ошибки
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Ошибка загрузки:', errorCode, errorDescription);
  });
}

// Создаём меню приложения
const template = [
  {
    label: 'Файл',
    submenu: [
      {
        label: 'Обновить',
        accelerator: 'CmdOrCtrl+R',
        click: () => mainWindow.reload()
      },
      { type: 'separator' },
      {
        label: 'Выход',
        accelerator: 'CmdOrCtrl+Q',
        click: () => app.quit()
      }
    ]
  },
  {
    label: 'Вид',
    submenu: [
      {
        label: 'Перезагрузить',
        accelerator: 'CmdOrCtrl+Shift+R',
        click: () => mainWindow.reload()
      },
      {
        label: 'Полноэкранный режим',
        accelerator: 'F11',
        click: () => mainWindow.setFullScreen(!mainWindow.isFullScreen())
      },
      {
        label: 'Инструменты разработчика',
        accelerator: 'F12',
        click: () => mainWindow.webContents.toggleDevTools()
      }
    ]
  },
  {
    label: 'Справка',
    submenu: [
      {
        label: 'О программе',
        click: () => {
          const { dialog } = require('electron');
          dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'О программе',
            message: 'VK Community Finder',
            detail: 'Версия: 1.0.0\n\nПрограмма для поиска сообществ ВКонтакте\nи сбора контактной информации.\n\n© 2026',
            buttons: ['OK']
          });
        }
      }
    ]
  }
];

// Когда Electron готов
app.whenReady().then(() => {
  setupSession();
  
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
  
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Выход когда все окна закрыты (кроме macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
