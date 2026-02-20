import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from './api';
import type { City, Product, BotConfig, Analytics, PaginatedAuditLogs } from './types';
import type { User } from './store';

// ─── Cities ─────────────────────────────────────────────────────────────────

export function useCities() {
  return useQuery<City[]>({
    queryKey: ['cities'],
    queryFn: async () => {
      const { data } = await api.get('/cities');
      return data;
    },
  });
}

export function useCity(cityId: string) {
  return useQuery<City>({
    queryKey: ['city', cityId],
    queryFn: async () => {
      const { data } = await api.get(`/cities/${cityId}`);
      return data;
    },
    enabled: !!cityId,
  });
}

export function useCreateCity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { name: string; slug: string; isActive?: boolean }) => {
      const { data } = await api.post('/cities', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cities'] });
    },
  });
}

export function useUpdateCity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { id: string; name?: string; slug?: string; isActive?: boolean }) => {
      const { id, ...body } = payload;
      const { data } = await api.patch(`/cities/${id}`, body);
      return data;
    },
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['cities'] });
      queryClient.invalidateQueries({ queryKey: ['city', vars.id] });
    },
  });
}

// ─── Products ────────────────────────────────────────────────────────────────

export function useProducts(cityId: string) {
  return useQuery<Product[]>({
    queryKey: ['products', cityId],
    queryFn: async () => {
      const { data } = await api.get(`/cities/${cityId}/products`);
      return data;
    },
    enabled: !!cityId,
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      cityId: string;
      name: string;
      description?: string;
      price?: number;
      isActive?: boolean;
    }) => {
      const { cityId, ...body } = payload;
      const { data } = await api.post(`/cities/${cityId}/products`, body);
      return data;
    },
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['products', vars.cityId] });
    },
  });
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      cityId: string;
      id: string;
      name?: string;
      description?: string;
      price?: number;
      isActive?: boolean;
    }) => {
      const { cityId, id, ...body } = payload;
      const { data } = await api.patch(`/cities/${cityId}/products/${id}`, body);
      return data;
    },
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['products', vars.cityId] });
    },
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { cityId: string; id: string }) => {
      await api.delete(`/cities/${payload.cityId}/products/${payload.id}`);
    },
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['products', vars.cityId] });
    },
  });
}

// ─── Bot Config ──────────────────────────────────────────────────────────────

export function useBotConfig(cityId: string) {
  return useQuery<BotConfig>({
    queryKey: ['botConfig', cityId],
    queryFn: async () => {
      const { data } = await api.get(`/cities/${cityId}/bot-config`);
      return data;
    },
    enabled: !!cityId,
  });
}

export function useUpdateBotConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      cityId: string;
      systemPrompt?: string;
      managerTelegram?: string;
      escalationAction?: 'LINK' | 'NOTIFY_MANAGER' | 'BITRIX';
    }) => {
      const { cityId, ...body } = payload;
      const { data } = await api.patch(`/cities/${cityId}/bot-config`, body);
      return data;
    },
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: ['botConfig', vars.cityId] });
    },
  });
}

// ─── Analytics ───────────────────────────────────────────────────────────────

export function useAnalytics(cityId: string) {
  return useQuery<Analytics>({
    queryKey: ['analytics', cityId],
    queryFn: async () => {
      const { data } = await api.get(`/cities/${cityId}/analytics`);
      return data;
    },
    enabled: !!cityId,
  });
}

// ─── Audit Logs ──────────────────────────────────────────────────────────────

export function useAuditLogs(cityId: string, page = 1, limit = 50) {
  return useQuery<PaginatedAuditLogs>({
    queryKey: ['auditLogs', cityId, page, limit],
    queryFn: async () => {
      const { data } = await api.get(`/cities/${cityId}/audit-logs`, {
        params: { page, limit },
      });
      return data;
    },
    enabled: !!cityId,
  });
}

// ─── Profile ─────────────────────────────────────────────────────────────────

export function useProfile() {
  return useQuery<User>({
    queryKey: ['profile'],
    queryFn: async () => {
      const { data } = await api.get('/auth/me');
      return data;
    },
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { name?: string; email?: string }) => {
      const { data } = await api.patch('/auth/me', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });
}
