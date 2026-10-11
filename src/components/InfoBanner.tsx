import { useState } from 'react';

export default function InfoBanner() {
  const [isOpen, setIsOpen] = useState(true);

  if (!isOpen) return null;

  return (
    <div className="mb-6 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-2xl p-5">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 bg-amber-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg className="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-amber-200 font-medium text-sm mb-1">Как это работает</h3>
          <ul className="text-amber-100/70 text-xs space-y-1">
            <li>• Программа работает через <strong>парсинг веб-страниц</strong> VK (без API токена)</li>
            <li>• Используются CORS-прокси для обхода ограничений браузера</li>
            <li>• Автоматически собирает: название, ссылку, участников, телефон, email, сайт, город</li>
            <li>• Дубликаты исключаются автоматически по ID сообщества</li>
            <li>• Каждый поиск добавляет новые сообщества к уже найденным</li>
            <li>• Данные экспортируются в Excel (.xlsx) с двумя листами</li>
          </ul>
          <div className="mt-3 p-2 bg-amber-900/30 rounded-lg border border-amber-700/30">
            <p className="text-amber-300/80 text-xs">
              <strong>⚠️ Важно:</strong> VK может ограничивать частые запросы (капча). 
              Если поиск не работает — подождите 1-2 минуты и попробуйте снова. 
              Программа автоматически переключает CORS-прокси при ошибках.
            </p>
          </div>
        </div>
        <button 
          onClick={() => setIsOpen(false)}
          className="text-amber-400/50 hover:text-amber-400 transition-colors"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
          </svg>
        </button>
      </div>
    </div>
  );
}
