export interface Community {
  id: number;
  name: string;
  screen_name: string;
  type: string;
  description: string;
  members_count: number;
  photo_200: string;
  site: string;
  phone: string;
  email: string;
  status: string;
  city?: {
    id: number;
    title: string;
  };
  verified: boolean;
  is_closed: number;
  activity: string;
}

export interface SearchCriteria {
  query: string;
  type: string;
  cityId: number | null;
  sortBy: string;
  maxResults: number;
}

export interface AppState {
  token: string;
  communities: Community[];
  searchedIds: Set<number>;
  isSearching: boolean;
  error: string | null;
  criteria: SearchCriteria;
}
