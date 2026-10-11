import { Community, SearchCriteria } from '../types';

// CORS прокси для обхода ограничений браузера
const CORS_PROXIES = [
  'https://api.allorigins.win/raw?url=',
  'https://corsproxy.io/?',
  'https://api.codetabs.com/v1/proxy?quest=',
];

let currentProxyIndex = 0;

function getProxyUrl(url: string): string {
  const proxy = CORS_PROXIES[currentProxyIndex % CORS_PROXIES.length];
  return proxy + encodeURIComponent(url);
}

function rotateProxy(): void {
  currentProxyIndex++;
}

async function fetchWithProxy(url: string, retries = 3): Promise<string> {
  let lastError: Error | null = null;
  
  for (let i = 0; i < retries; i++) {
    try {
      const proxyUrl = getProxyUrl(url);
      const response = await fetch(proxyUrl, {
        headers: {
          'Accept': 'text/html,application/xhtml+xml',
        }
      });
      
      if (!response.ok) {
        throw new Error(`Ошибка загрузки страницы (код ${response.status}). CORS-прокси может быть недоступен.`);
      }
      
      const text = await response.text();
      
      if (text.includes('captcha') || text.includes('Капчу')) {
        throw new Error('VK запросил капчу. Подождите 1-2 минуты и попробуйте снова.');
      }
      
      return text;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Неизвестная ошибка';
      lastError = new Error(message);
      rotateProxy();
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  throw lastError || new Error('Не удалось загрузить страницу');
}

// Парсинг страницы поиска сообществ
export async function searchCommunities(criteria: SearchCriteria): Promise<Community[]> {
  const query = encodeURIComponent(criteria.query);
  const tabParam = criteria.type === 'page' ? 'publics' : criteria.type === 'event' ? 'events' : 'groups';
  
  const searchUrl = `https://vk.com/communities?q=${query}&section=communities&tab=${tabParam}`;
  
  try {
    const html = await fetchWithProxy(searchUrl);
    
    // Сначала пробуем парсить JSON из скриптов
    let communities = parseJsonFromHtml(html);
    
    // Если JSON не нашли, парсим HTML
    if (communities.length === 0) {
      communities = parseSearchResults(html);
    }
    
    // Ограничиваем количество результатов
    return communities.slice(0, criteria.maxResults);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Неизвестная ошибка';
    throw new Error(`Ошибка поиска: ${message}`);
  }
}

function parseSearchResults(html: string): Community[] {
  const communities: Community[] = [];
  const seen = new Set<number>();
  
  // Паттерн 1: Ищем ссылки на клубы и сообщества
  const clubPattern = /href="\/(club\d+)"[^>]*>([\s\S]*?)<\/a>/gi;
  let match;
  
  while ((match = clubPattern.exec(html)) !== null) {
    const screenName = match[1];
    const nameHtml = match[2];
    const name = decodeHtml(nameHtml.replace(/<[^>]*>/g, '').trim());
    
    if (!name || name.length < 2 || name.length > 100) continue;
    
    const id = parseInt(screenName.replace('club', ''));
    if (seen.has(id)) continue;
    seen.add(id);
    
    communities.push({
      id,
      name,
      screen_name: screenName,
      type: 'group',
      description: '',
      members_count: 0,
      photo_200: '',
      site: '',
      phone: '',
      email: '',
      status: '',
      verified: false,
      is_closed: 0,
      activity: '',
    });
  }
  
  // Паттерн 2: Ищем другие типы ссылок (именованные сообщества)
  const namePattern = /href="\/([a-zA-Z][a-zA-Z0-9_.]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  
  while ((match = namePattern.exec(html)) !== null) {
    const screenName = match[1];
    const nameHtml = match[2];
    const name = decodeHtml(nameHtml.replace(/<[^>]*>/g, '').trim());
    
    // Пропускаем системные ссылки
    const skipNames = ['login', 'register', 'restore', 'settings', 'feed', 'messages', 
                       'notifications', 'friends', 'groups', 'search', 'im', 'mail',
                       'communities', 'ads', 'developers', 'support', 'bugtracker'];
    if (skipNames.includes(screenName)) continue;
    if (screenName.startsWith('club')) continue;
    if (!name || name.length < 2 || name.length > 100) continue;
    
    const id = hashCode(screenName);
    if (seen.has(id)) continue;
    seen.add(id);
    
    communities.push({
      id,
      name,
      screen_name: screenName,
      type: 'group',
      description: '',
      members_count: 0,
      photo_200: '',
      site: '',
      phone: '',
      email: '',
      status: '',
      verified: false,
      is_closed: 0,
      activity: '',
    });
  }
  
  // Паттерн 3: Извлекаем количество участников рядом с найденными сообществами
  for (const community of communities) {
    const membersRegex = new RegExp(
      screenNameEscape(community.screen_name) + '[\\s\\S]{0,500}?(\\d[\\d\\s]*)\\s*(?:участник|подписчик|человек|member)',
      'i'
    );
    const membersMatch = html.match(membersRegex);
    if (membersMatch) {
      community.members_count = parseInt(membersMatch[1].replace(/\s/g, ''));
    }
  }
  
  return communities;
}

function screenNameEscape(name: string): string {
  return name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function parseJsonFromHtml(html: string): Community[] {
  const communities: Community[] = [];
  
  // Ищем JSON данные в скриптах VK
  const patterns = [
    /"groups"\s*:\s*(\[[\s\S]*?\])\s*[,}]/,
    /"search_results"\s*:\s*(\[[\s\S]*?\])\s*[,}]/,
    /"result"\s*:\s*\{[\s\S]*?"items"\s*:\s*(\[[\s\S]*?\])/,
  ];
  
  for (const pattern of patterns) {
    const match = html.match(pattern);
    if (match) {
      try {
        const data = JSON.parse(match[1]);
        if (Array.isArray(data)) {
          for (const item of data) {
            if (item.name || item.title) {
              communities.push({
                id: item.id || item.group_id || hashCode(item.name || item.title || ''),
                name: item.name || item.title || '',
                screen_name: item.screen_name || item.screenName || '',
                type: item.type || 'group',
                description: item.description || '',
                members_count: item.members_count || item.members || 0,
                photo_200: item.photo_200 || item.photo || '',
                site: item.site || '',
                phone: '',
                email: '',
                status: item.status || '',
                verified: item.verified || false,
                is_closed: item.is_closed || 0,
                activity: item.activity || '',
              });
            }
          }
        }
      } catch {
        // JSON невалидный, пропускаем
      }
    }
  }
  
  // Также ищем данные в формате VK "cur" или "search"
  const curPattern = /var\s+search\s*=\s*(\{[\s\S]*?\});/;
  const curMatch = html.match(curPattern);
  if (curMatch) {
    try {
      const data = JSON.parse(curMatch[1]);
      if (data.rows && Array.isArray(data.rows)) {
        for (const row of data.rows) {
          const nameMatch = row.match(/href="\/([^"]+)"[^>]*>([^<]+)</);
          if (nameMatch) {
            communities.push({
              id: hashCode(nameMatch[1]),
              name: decodeHtml(nameMatch[2].trim()),
              screen_name: nameMatch[1],
              type: 'group',
              description: '',
              members_count: 0,
              photo_200: '',
              site: '',
              phone: '',
              email: '',
              status: '',
              verified: false,
              is_closed: 0,
              activity: '',
            });
          }
        }
      }
    } catch {
      // пропускаем
    }
  }
  
  return communities;
}

// Парсинг отдельной страницы сообщества для сбора контактов
export async function fetchCommunityDetails(screenName: string): Promise<Partial<Community>> {
  const url = `https://vk.com/${screenName}`;
  
  try {
    const html = await fetchWithProxy(url);
    const details: Partial<Community> = {};
    
    // Извлекаем телефон
    const phonePatterns = [
      /href="tel:([\+\d\s\-\(\)]+)"/i,
      /(?:tel|phone|телефон)[^>]*>([\+\d\s\-\(\)]{7,20})</i,
      /([\+]?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})/,
      /([\+]?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})/,
    ];
    
    for (const pattern of phonePatterns) {
      const match = html.match(pattern);
      if (match) {
        details.phone = match[1].trim();
        break;
      }
    }
    
    // Извлекаем email
    const emailMatch = html.match(/([\w.+-]+@[\w.-]+\.\w{2,})/);
    if (emailMatch) {
      const email = emailMatch[1];
      // Фильтруем email из VK
      if (!email.includes('vk.com') && !email.includes('vk.ru')) {
        details.email = email;
      }
    }
    
    // Извлекаем сайт
    const sitePatterns = [
      /class="[^"]*(?:group_info_row_link|profile_info_link)[^"]*"[^>]*href="([^"]+)"/i,
      /(?:website|сайт|site)[^>]*href="([^"]+)"/i,
      /"website"\s*:\s*"([^"]+)"/,
    ];
    
    for (const pattern of sitePatterns) {
      const match = html.match(pattern);
      if (match) {
        const site = match[1].trim();
        if (!site.includes('vk.com') && !site.includes('vk.ru') && site.startsWith('http')) {
          details.site = site;
          break;
        }
      }
    }
    
    // Извлекаем описание
    const descPatterns = [
      /<meta\s+property="og:description"\s+content="([^"]+)"/i,
      /class="[^"]*group_info[^"]*"[^>]*>([^<]+)/i,
      /"description"\s*:\s*"([^"]+)"/,
    ];
    
    for (const pattern of descPatterns) {
      const match = html.match(pattern);
      if (match && match[1].length > 10) {
        details.description = decodeHtml(match[1]);
        break;
      }
    }
    
    // Извлекаем статус
    const statusMatch = html.match(/class="[^"]*group_status[^"]*"[^>]*>([^<]+)/i) ||
                        html.match(/"status"\s*:\s*"([^"]{1,200})"/);
    if (statusMatch) {
      details.status = decodeHtml(statusMatch[1].trim());
    }
    
    // Извлекаем количество участников
    const membersPatterns = [
      /(\d[\d\s]*)\s*(?:участник|подписчик|человек)/i,
      /"members_count"\s*:\s*(\d+)/,
      /(\d[\d\s]*)\s*member/i,
    ];
    
    for (const pattern of membersPatterns) {
      const match = html.match(pattern);
      if (match) {
        details.members_count = parseInt(match[1].replace(/\s/g, ''));
        break;
      }
    }
    
    // Извлекаем город
    const cityPatterns = [
      /(?:город|city)[^>]*>([^<]+)</i,
      /"city"\s*:\s*\{[^}]*"title"\s*:\s*"([^"]+)"/,
      /class="[^"]*group_info_row[^"]*"[^>]*>[^<]*город[^<]*<[^>]*>([^<]+)/i,
    ];
    
    for (const pattern of cityPatterns) {
      const match = html.match(pattern);
      if (match) {
        const cityTitle = decodeHtml(match[1].trim());
        if (cityTitle.length > 1 && cityTitle.length < 50) {
          details.city = { id: 0, title: cityTitle };
          break;
        }
      }
    }
    
    // Извлекаем контакты из блока контактов
    const contactsBlock = html.match(/class="[^"]*contacts[^"]*"[\s\S]*?(?:<\/div>\s*){2,8}/i);
    if (contactsBlock) {
      const block = contactsBlock[0];
      
      const contactPhone = block.match(/([\+]?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2,4}[\s\-]?\d{0,2})/);
      if (contactPhone && !details.phone) {
        details.phone = contactPhone[1].trim();
      }
      
      const contactEmail = block.match(/([\w.+-]+@[\w.-]+\.\w{2,})/);
      if (contactEmail && !details.email) {
        details.email = contactEmail[1];
      }
    }
    
    // Проверяем верификацию
    if (html.includes('group_verified') || html.includes('profile_verified')) {
      details.verified = true;
    }
    
    return details;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Неизвестная ошибка';
    console.warn(`Не удалось получить детали для ${screenName}: ${message}`);
    return {};
  }
}

// Утилиты
function decodeHtml(html: string): string {
  const txt = document.createElement('textarea');
  txt.innerHTML = html;
  return txt.value;
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
