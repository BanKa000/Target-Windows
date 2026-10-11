// Preload script - выполняется в контексте страницы до её загрузки
// Здесь можно безопасно expose API из Node.js в браузер

const { contextBridge } = require('electron');

// Expose защищённый API в браузер
contextBridge.exposeInMainWorld('electronAPI', {
  // Версия приложения
  getVersion: () => require('electron').app.getVersion(),
  
  // Платформа
  getPlatform: () => process.platform,
  
  // Путь к userData
  getUserDataPath: () => require('electron').app.getPath('userData'),
  
  // Открыть внешнюю ссылку в системном браузере
  openExternal: (url) => {
    require('electron').shell.openExternal(url);
  }
});
