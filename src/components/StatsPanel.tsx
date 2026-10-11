interface StatsPanelProps {
  totalCommunities: number;
  searchCount: number;
  onExport: () => void;
  onClear: () => void;
}

export default function StatsPanel({ totalCommunities, searchCount, onExport, onClear }: StatsPanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {/* Всего сообществ */}
      <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <p className="text-white/50 text-xs">Найдено</p>
            <p className="text-white text-xl font-bold">{totalCommunities}</p>
          </div>
        </div>
      </div>

      {/* Количество поисков */}
      <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <div>
            <p className="text-white/50 text-xs">Поисков</p>
            <p className="text-white text-xl font-bold">{searchCount}</p>
          </div>
        </div>
      </div>

      {/* Кнопка экспорта */}
      <button
        onClick={onExport}
        disabled={totalCommunities === 0}
        className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-xl p-4 hover:bg-green-500/10 hover:border-green-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center group-hover:bg-green-500/30 transition-colors">
            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="text-left">
            <p className="text-white/50 text-xs">Экспорт</p>
            <p className="text-green-400 text-sm font-medium">Скачать Excel</p>
          </div>
        </div>
      </button>

      {/* Кнопка очистки */}
      <button
        onClick={onClear}
        disabled={totalCommunities === 0}
        className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-xl p-4 hover:bg-red-500/10 hover:border-red-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center group-hover:bg-red-500/30 transition-colors">
            <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <div className="text-left">
            <p className="text-white/50 text-xs">Данные</p>
            <p className="text-red-400 text-sm font-medium">Очистить всё</p>
          </div>
        </div>
      </button>
    </div>
  );
}
