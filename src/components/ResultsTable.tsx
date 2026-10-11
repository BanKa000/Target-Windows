import { Community } from '../types';

interface ResultsTableProps {
  communities: Community[];
  onRemove: (id: number) => void;
}

export default function ResultsTable({ communities, onRemove }: ResultsTableProps) {
  if (communities.length === 0) {
    return (
      <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-12 text-center">
        <svg className="w-16 h-16 text-white/20 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 className="text-white/50 text-lg mb-2">Результаты поиска</h3>
        <p className="text-white/30 text-sm">Введите критерии поиска и нажмите "Найти" для начала работы</p>
      </div>
    );
  }

  return (
    <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10 bg-white/5">
              <th className="px-4 py-3 text-left text-xs font-medium text-white/50 uppercase tracking-wider">№</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/50 uppercase tracking-wider">Сообщество</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/50 uppercase tracking-wider">Участники</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/50 uppercase tracking-wider">Контакты</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/50 uppercase tracking-wider">Город</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/50 uppercase tracking-wider">Ссылки</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/50 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {communities.map((community, index) => (
              <tr key={community.id} className="hover:bg-white/5 transition-colors">
                <td className="px-4 py-3 text-sm text-white/50">{index + 1}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {community.photo_200 ? (
                      <img 
                        src={community.photo_200} 
                        alt="" 
                        className="w-10 h-10 rounded-lg object-cover"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                        <span className="text-blue-400 text-sm font-bold">{community.name[0]}</span>
                      </div>
                    )}
                    <div>
                      <a 
                        href={`https://vk.com/${community.screen_name}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-white font-medium hover:text-blue-400 transition-colors text-sm"
                      >
                        {community.name}
                      </a>
                      {community.verified && (
                        <span className="ml-1 inline-flex items-center text-blue-400" title="Верифицировано">
                          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                          </svg>
                        </span>
                      )}
                      <p className="text-white/40 text-xs truncate max-w-[200px]">
                        {community.type === 'group' ? 'Группа' : community.type === 'page' ? 'Страница' : 'Встреча'} • {community.screen_name}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-white text-sm font-medium">
                    {community.members_count.toLocaleString('ru-RU')}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1">
                    {community.phone && (
                      <div className="flex items-center gap-1 text-green-400 text-xs">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
                        </svg>
                        {community.phone}
                      </div>
                    )}
                    {community.email && (
                      <div className="flex items-center gap-1 text-blue-400 text-xs">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                          <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                        </svg>
                        {community.email}
                      </div>
                    )}
                    {!community.phone && !community.email && (
                      <span className="text-white/30 text-xs">—</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-white/70 text-sm">{community.city?.title || '—'}</span>
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1">
                    {community.site && (
                      <a 
                        href={community.site.startsWith('http') ? community.site : `https://${community.site}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs transition-colors"
                      >
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd"/>
                        </svg>
                        <span className="truncate max-w-[120px]">{community.site}</span>
                      </a>
                    )}
                    <a 
                      href={`https://vk.com/${community.screen_name}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs transition-colors"
                    >
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12.785 16.241s.288-.032.436-.194c.136-.148.132-.427.132-.427s-.019-1.302.587-1.496c.596-.19 1.362 1.26 2.174 1.818.614.42 1.08.328 1.08.328l2.172-.03s1.136-.07.598-.964c-.044-.073-.314-.661-1.618-1.869-1.366-1.265-1.183-1.06.462-3.246.998-1.328 1.396-2.14 1.272-2.488-.12-.334-.858-.244-.858-.244l-2.448.015s-.182-.025-.316.056c-.132.078-.216.264-.216.264s-.388 1.032-.904 1.91c-1.092 1.856-1.528 1.952-1.706 1.836-.414-.268-.31-1.076-.31-1.65 0-1.792.272-2.54-.53-2.734-.266-.064-.462-.106-1.142-.113-.872-.009-1.61.003-2.028.208-.278.136-.492.44-.362.458.162.02.528.098.722.362.25.342.24 1.108.24 1.108s.144 2.11-.336 2.372c-.33.18-.782-.188-1.75-1.87-.496-.862-.87-1.814-.87-1.814s-.072-.178-.2-.274c-.156-.116-.374-.152-.374-.152l-2.326.015s-.35.01-.478.162c-.114.134-.01.412-.01.412s1.82 4.258 3.882 6.404c1.888 1.968 4.032 1.838 4.032 1.838h.972z"/>
                      </svg>
                      vk.com/{community.screen_name}
                    </a>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <a
                      href={`https://vk.com/${community.screen_name}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 bg-blue-500/20 hover:bg-blue-500/40 text-blue-400 rounded-lg transition-colors"
                      title="Открыть в VK"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"/>
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
                      </svg>
                    </a>
                    <button
                      onClick={() => onRemove(community.id)}
                      className="p-1.5 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-lg transition-colors"
                      title="Удалить из списка"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
