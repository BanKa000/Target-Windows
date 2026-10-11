import { useState } from 'react';
import { SearchCriteria } from '../types';

interface SearchPanelProps {
  onSearch: (criteria: SearchCriteria) => void;
  isSearching: boolean;
  initialCriteria: SearchCriteria;
}

export default function SearchPanel({ onSearch, isSearching, initialCriteria }: SearchPanelProps) {
  const [query, setQuery] = useState('');
  const [type, setType] = useState(initialCriteria.type);
  const [sortBy, setSortBy] = useState(initialCriteria.sortBy);
  const [maxResults, setMaxResults] = useState(initialCriteria.maxResults);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSearch = () => {
    if (!query.trim()) return;
    onSearch({
      query: query.trim(),
      type,
      cityId: null,
      sortBy,
      maxResults,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 mb-6">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        Критерии поиска
      </h2>

      {/* Main search */}
      <div className="flex gap-3 mb-4">
        <div className="flex-1 relative">
          <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Введите ключевые слова (например: автосервис, доставка, салон красоты)..."
            className="w-full bg-black/30 border border-white/20 rounded-xl pl-12 pr-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>
        
        <button
          onClick={handleSearch}
          disabled={isSearching || !query.trim()}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20"
        >
          {isSearching ? (
            <>
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              Поиск...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Найти
            </>
          )}
        </button>
      </div>

      {/* Advanced settings toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mb-4 transition-colors"
      >
        <svg className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        Расширенные настройки
      </button>

      {/* Advanced settings */}
      {showAdvanced && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-black/20 rounded-xl border border-white/5">
          {/* Type filter */}
          <div>
            <label className="block text-white/70 text-sm mb-2">Тип сообщества</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full bg-black/30 border border-white/20 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-blue-500 appearance-none"
            >
              <option value="group" className="bg-gray-800">Группа</option>
              <option value="page" className="bg-gray-800">Публичная страница</option>
              <option value="event" className="bg-gray-800">Встреча</option>
            </select>
          </div>

          {/* Sort */}
          <div>
            <label className="block text-white/70 text-sm mb-2">Сортировка</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full bg-black/30 border border-white/20 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-blue-500 appearance-none"
            >
              <option value="relevance" className="bg-gray-800">По релевантности</option>
              <option value="growth" className="bg-gray-800">По скорости роста</option>
            </select>
          </div>

          {/* Max results */}
          <div>
            <label className="block text-white/70 text-sm mb-2">Макс. результатов</label>
            <input
              type="number"
              value={maxResults}
              onChange={(e) => setMaxResults(Math.min(1000, Math.max(10, parseInt(e.target.value) || 10)))}
              min={10}
              max={1000}
              className="w-full bg-black/30 border border-white/20 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      )}

      {/* Quick search suggestions */}
      <div className="mt-4 flex flex-wrap gap-2">
        <span className="text-white/50 text-sm">Быстрый поиск:</span>
        {['Автосервис', 'Доставка еды', 'Салон красоты', 'Фитнес', 'Ремонт квартир', 'Стоматология'].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => setQuery(suggestion)}
            className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white/70 hover:text-white text-sm rounded-full transition-all"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
