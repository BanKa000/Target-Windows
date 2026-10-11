import { useState, useCallback } from 'react';
import { Community, SearchCriteria } from './types';
import SearchPanel from './components/SearchPanel';
import ResultsTable from './components/ResultsTable';
import TokenInput from './components/TokenInput';
import StatsPanel from './components/StatsPanel';
import { searchCommunities, fetchCommunityDetails } from './services/vkApi';
import { exportToExcel } from './services/excelExport';

function App() {
  const [token, setToken] = useState('');
  const [communities, setCommunities] = useState<Community[]>([]);
  const [searchedIds, setSearchedIds] = useState<Set<number>>(new Set());
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchCount, setSearchCount] = useState(0);

  const criteria: SearchCriteria = {
    query: '',
    type: 'group',
    cityId: null,
    sortBy: 'relevance',
    maxResults: 100,
  };

  const handleSearch = useCallback(async (searchCriteria: SearchCriteria) => {
    if (!token) {
      setError('Введите VK API токен');
      return;
    }

    setIsSearching(true);
    setError(null);

    try {
      const results = await searchCommunities(token, searchCriteria);
      
      // Фильтруем дубликаты
      const newCommunities: Community[] = [];
      
      for (const community of results) {
        if (!searchedIds.has(community.id)) {
          // Получаем детальную информацию
          const details = await fetchCommunityDetails(token, community.id);
          const enrichedCommunity: Community = {
            ...community,
            ...details,
          };
          newCommunities.push(enrichedCommunity);
          setSearchedIds(prev => new Set([...prev, community.id]));
        }
      }

      setCommunities(prev => [...prev, ...newCommunities]);
      setSearchCount(prev => prev + 1);
    } catch (err: any) {
      setError(err.message || 'Ошибка при поиске');
    } finally {
      setIsSearching(false);
    }
  }, [token, searchedIds]);

  const handleExport = () => {
    if (communities.length === 0) {
      setError('Нет данных для экспорта');
      return;
    }
    exportToExcel(communities);
  };

  const handleClear = () => {
    setCommunities([]);
    setSearchedIds(new Set());
    setSearchCount(0);
  };

  const handleRemoveCommunity = (id: number) => {
    setCommunities(prev => prev.filter(c => c.id !== id));
    setSearchedIds(prev => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center">
              <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.785 16.241s.288-.032.436-.194c.136-.148.132-.427.132-.427s-.019-1.302.587-1.496c.596-.19 1.362 1.26 2.174 1.818.614.42 1.08.328 1.08.328l2.172-.03s1.136-.07.598-.964c-.044-.073-.314-.661-1.618-1.869-1.366-1.265-1.183-1.06.462-3.246.998-1.328 1.396-2.14 1.272-2.488-.12-.334-.858-.244-.858-.244l-2.448.015s-.182-.025-.316.056c-.132.078-.216.264-.216.264s-.388 1.032-.904 1.91c-1.092 1.856-1.528 1.952-1.706 1.836-.414-.268-.31-1.076-.31-1.65 0-1.792.272-2.54-.53-2.734-.266-.064-.462-.106-1.142-.113-.872-.009-1.61.003-2.028.208-.278.136-.492.44-.362.458.162.02.528.098.722.362.25.342.24 1.108.24 1.108s.144 2.11-.336 2.372c-.33.18-.782-.188-1.75-1.87-.496-.862-.87-1.814-.87-1.814s-.072-.178-.2-.274c-.156-.116-.374-.152-.374-.152l-2.326.015s-.35.01-.478.162c-.114.134-.01.412-.01.412s1.82 4.258 3.882 6.404c1.888 1.968 4.032 1.838 4.032 1.838h.972z"/>
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-white">VK Community Finder</h1>
          </div>
          <p className="text-blue-200 text-sm">Поиск сообществ ВКонтакте и экспорт в Excel</p>
        </header>

        {/* Token Input */}
        <TokenInput token={token} setToken={setToken} />

        {/* Search Panel */}
        <SearchPanel 
          onSearch={handleSearch} 
          isSearching={isSearching}
          initialCriteria={criteria}
        />

        {/* Error */}
        {error && (
          <div className="mt-4 bg-red-500/20 border border-red-500/50 rounded-xl p-4 text-red-200 flex items-center gap-2">
            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Stats */}
        <StatsPanel 
          totalCommunities={communities.length} 
          searchCount={searchCount}
          onExport={handleExport}
          onClear={handleClear}
        />

        {/* Results Table */}
        <ResultsTable 
          communities={communities}
          onRemove={handleRemoveCommunity}
        />
      </div>
    </div>
  );
}

export default App;
