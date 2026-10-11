import { Community, SearchCriteria } from '../types';

const VK_API_VERSION = '5.199';
const BASE_URL = 'https://api.vk.com/method';

// JSONP helper for VK API (works without CORS issues in browser)
function vkApiRequest(method: string, params: Record<string, any>): Promise<any> {
  return new Promise((resolve, reject) => {
    const callbackName = `vkCallback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const script = document.createElement('script');
    const url = new URL(`${BASE_URL}/${method}`);
    
    url.searchParams.set('access_token', params.access_token);
    url.searchParams.set('v', VK_API_VERSION);
    url.searchParams.set('callback', callbackName);
    
    Object.keys(params).forEach(key => {
      if (key !== 'access_token' && key !== 'v' && key !== 'callback') {
        url.searchParams.set(key, params[key]);
      }
    });

    (window as any)[callbackName] = (data: any) => {
      delete (window as any)[callbackName];
      document.head.removeChild(script);
      
      if (data.error) {
        reject(new Error(`VK API Error: ${data.error.error_msg}`));
      } else {
        resolve(data.response);
      }
    };

    script.src = url.toString();
    script.onerror = () => {
      delete (window as any)[callbackName];
      document.head.removeChild(script);
      reject(new Error('Ошибка загрузки скрипта VK API'));
    };

    document.head.appendChild(script);
  });
}

export async function searchCommunities(token: string, criteria: SearchCriteria): Promise<Community[]> {
  const params: Record<string, any> = {
    access_token: token,
    q: criteria.query,
    type: criteria.type,
    sort: criteria.sortBy === 'relevance' ? 0 : criteria.sortBy === 'growth' ? 1 : 0,
    count: Math.min(criteria.maxResults, 1000),
    offset: 0,
  };

  if (criteria.cityId) {
    params.city_id = criteria.cityId;
  }

  try {
    const response = await vkApiRequest('groups.search', params);
    
    if (!response.items) return [];

    return response.items.map((item: any) => ({
      id: item.id,
      name: item.name,
      screen_name: item.screen_name,
      type: item.type,
      description: item.description || '',
      members_count: item.member_count || 0,
      photo_200: item.photo_200 || item.photo_100 || '',
      site: '',
      phone: '',
      email: '',
      status: '',
      city: item.city,
      verified: item.verified || false,
      is_closed: item.is_closed || 0,
      activity: item.activity || '',
    }));
  } catch (error: any) {
    throw new Error(`Ошибка поиска: ${error.message}`);
  }
}

export async function fetchCommunityDetails(token: string, groupId: number): Promise<Partial<Community>> {
  try {
    const response = await vkApiRequest('groups.getById', {
      access_token: token,
      group_id: groupId,
      fields: 'description,site,contacts,phone,email,status,activity,city,members_count',
    });

    const group = response.groups ? response.groups[0] : response;
    
    // Extract phone from contacts
    let phone = '';
    let email = '';
    
    if (group.contacts && group.contacts.length > 0) {
      const phoneContact = group.contacts.find((c: any) => c.desc?.includes('тел') || c.desc?.includes('Тел') || c.desc?.includes('phone'));
      if (phoneContact?.phone) {
        phone = phoneContact.phone;
      }
      const emailContact = group.contacts.find((c: any) => c.desc?.includes('email') || c.desc?.includes('почт') || c.desc?.includes('Email'));
      if (emailContact?.email) {
        email = emailContact.email;
      }
    }

    return {
      description: group.description || '',
      site: group.site || '',
      phone: phone,
      email: email,
      status: group.status || '',
      activity: group.activity || '',
      members_count: group.members_count || 0,
      city: group.city,
      verified: group.verified || false,
    };
  } catch (error: any) {
    console.warn(`Не удалось получить детали для группы ${groupId}:`, error.message);
    return {};
  }
}

export async function verifyToken(token: string): Promise<boolean> {
  try {
    await vkApiRequest('users.get', {
      access_token: token,
      fields: 'photo_50',
    });
    return true;
  } catch {
    return false;
  }
}
