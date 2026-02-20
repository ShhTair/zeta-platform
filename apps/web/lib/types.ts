export interface City {
  id: string;
  name: string;
  slug: string;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
}

export interface Product {
  id: string;
  name: string;
  description?: string;
  price?: number;
  isActive: boolean;
  cityId: string;
  article?: string;
  category?: string;
  imageUrl?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface BotConfig {
  id: string;
  cityId: string;
  systemPrompt: string;
  managerTelegram: string;
  escalationAction: 'LINK' | 'NOTIFY_MANAGER' | 'BITRIX';
  updatedAt?: string;
}

export interface AnalyticsByDay {
  date: string;
  conversations: number;
}

export interface Analytics {
  totalConversationsToday: number;
  totalConversationsWeek: number;
  totalConversationsMonth: number;
  topProducts: Array<{ productId: string; name: string; count: number }>;
  conversationsByDay: AnalyticsByDay[];
}

export interface AuditLog {
  id: string;
  action: string;
  entityType: string;
  entityId: string;
  userId: string;
  user?: {
    id: string;
    name: string;
    email: string;
  };
  details?: Record<string, unknown>;
  createdAt: string;
}

export interface PaginatedAuditLogs {
  logs: AuditLog[];
  total: number;
  page: number;
  pageSize: number;
}
