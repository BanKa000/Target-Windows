import { useState } from 'react';
import { Community } from '../types';
import { fetchCommunityDetails } from '../services/vkParser';

interface ManualAddProps {
  onAdd: (community: Community) => void;
  searchedIds: Set<number>;
}

export default function ManualAdd({ onAdd, searchedIds }: ManualAddProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [showBatch, setShowBatch] = useState(false);
  const [batchUrls, setBatchUrls] = useState('');
  const [isBatchLoading, setIsBatchLoading] = useState(false);
  const [batchProgress, setBatchProgress] = useState('');
  const [batchError, setBatchError] = useState<string | null>(null);

  const extractScreenName = (input: string): string | null => {
    const trimmed = input.trim();
    if (!trimmed) return null;
    
    const urlMatch = trimmed.match(/vk\.com\/(club\d+|[a-zA-Z][a-zA-Z0-9_.]+)/);
    if (urlMatch) return urlMatch[1];
    
    const directMatch = trimmed.match(/^(club\d+|[a-zA-Z][a-zA-Z0-9_.]+)$/);
    if (directMatch) return directMatch[1];
    
    return null;
  };

  const getIdFromScreenName = (screenName: string): number => {
    return screenName.startsWith('club') 
      ? parseInt(screenName.replace('club', ''))
      : hashCode(screenName);
  };

  const handleAdd = async () => {
    const screenName = extractScreenName(url);
    if (!screenName) {
      setError('Неверный формат. Введите ссылку вида: vk.com/community_name или club123456');
      return;
    }

    const id = getIdFromScreenName(screenName);

    if (searchedIds.has(id)) {
      setError('Это сообщество уже добавлено');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const details = await fetchCommunityDetails(screenName);
      
      const community: Community = {
        id,
        name: screenName,
        screen_name: screenName,
        type: 'group',
        description: details.description || '',
        members_count: details.members_count || 0,
        photo_200: '',
        site: details.site || '',
        phone: details.phone || '',
        email: details.email || '',
        status: details.status || '',
        city: details.city,
        verified: details.verified || false,
        is_closed: 0,
        activity: details.activity || '',
      };

      onAdd(community);
      setUrl('');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Неизвестная ошибка';
      setError(`Ошибка: ${message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBatchAdd = async () => {
    const lines = batchUrls.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length === 0) return;

    setIsBatchLoading(true);
    setBatchError(null);
    let added = 0;
    let skipped = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      setBatchProgress(`${i + 1}/${lines.length}`);
      
      const screenName = extractScreenName(line);
      if (!screenName) {
        skipped++;
        continue;
      }

      const id = getIdFromScreenName(screenName);
      if (searchedIds.has(id)) {
        skipped++;
        continue;
      }

      try {
        const details = await fetchCommunityDetails(screenName);
        
        const community: Community = {
          id,
          name: screenName,
          screen_name: screenName,
          type: 'group',
          description: details.description || '',
          members_count: details.members_count || 0,
          photo_200: '',
          site: details.site || '',
          phone: details.phone || '',
          email: details.email || '',
          status: details.status || '',
          city: details.city,
          verified: details.verified || false,
          is_closed: 0,
          activity: details.activity || '',
        };

        onAdd(community);
        added++;
      } catch {
        skipped++;
      }

      // Задержка между запросами
      if (i < lines.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }

    setIsBatchLoading(false);
    setBatchUrls('');
    setBatchProgress('');
    
    if (added > 0) {
      setBatchError(null);
    }
    if (skipped > 0 && added === 0) {
      setBatchError(`Не удалось добавить ${skipped} сообществ. Проверьте ссылки.`);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="w-full mb-6 bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-4 text-left hover:bg-white/10 transition-all group"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center group-hover:bg-purple-500/30 transition-colors">
            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <div>
            <p className="text-white font-medium text-sm">Добавить сообщество вручную</p>
            <p className="text-white/50 text-xs">Вставьте ссылку на сообщество VK для сбора контактов</p>
          </div>
          <svg className="w-5 h-5 text-white/30 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
    );
  }

  return (
    <div className="mb-6 bg-white/5 backdrop-blur-lg border border-purple-500/30 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-medium flex items-center gap-2">
          <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Добавить сообщество по ссылке
        </h3>
        <button onClick={() => setIsOpen(false)} className="text-white/50 hover:text-white transition-colors">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
          </svg>
        </button>
      </div>

      {/* Single add */}
      <div className="flex gap-3">
        <div className="flex-1">
          <input
            type="text"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setError(null); }}
            onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="https://vk.com/community_name или club123456"
            className="w-full bg-black/30 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
          />
        </div>
        <button
          onClick={handleAdd}
          disabled={isLoading || !url.trim()}
          className="px-5 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              Загрузка...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Добавить
            </>
          )}
        </button>
      </div>

      {error && (
        <p className="mt-2 text-red-400 text-sm">{error}</p>
      )}

      {/* Batch mode */}
      <div className="mt-4 pt-4 border-t border-white/10">
        <button 
          onClick={() => setShowBatch(!showBatch)}
          className="text-purple-400 hover:text-purple-300 text-xs flex items-center gap-1 transition-colors"
        >
          <svg className={`w-3 h-3 transition-transform ${showBatch ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          Массовое добавление по списку ссылок
        </button>
        
        {showBatch && (
          <div className="mt-3">
            <textarea
              value={batchUrls}
              onChange={(e) => { setBatchUrls(e.target.value); setBatchError(null); }}
              placeholder={"Вставьте ссылки (по одной на строку):\nhttps://vk.com/community1\nhttps://vk.com/club12345\nvk.com/community3"}
              rows={5}
              className="w-full bg-black/30 border border-white/20 rounded-xl px-4 py-3 text-white text-sm placeholder-white/30 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 resize-none"
            />
            <button
              onClick={handleBatchAdd}
              disabled={isBatchLoading || !batchUrls.trim()}
              className="mt-2 px-4 py-2 bg-purple-600/80 hover:bg-purple-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-all"
            >
              {isBatchLoading ? `Обработка... (${batchProgress})` : `Добавить все (${batchUrls.split('\n').filter((l: string) => l.trim()).length} ссылок)`}
            </button>
            {batchError && <p className="mt-2 text-red-400 text-xs">{batchError}</p>}
            <p className="mt-2 text-white/40 text-xs">
              ⏱ Между запросами пауза 2 сек. для избежания блокировки VK
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function hashCode(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash) || 1;
}
