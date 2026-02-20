import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type UserRole = 'SUPER_ADMIN' | 'CITY_ADMIN' | 'MANAGER';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  cityAccess: string[];
  createdAt: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  selectedCityId: string | null;

  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setSelectedCityId: (cityId: string | null) => void;

  isAuthenticated: () => boolean;
  hasRole: (roles: string[]) => boolean;
  canAccessCity: (cityId: string) => boolean;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      selectedCityId: null,

      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      setSelectedCityId: (cityId) => set({ selectedCityId: cityId }),

      isAuthenticated: () => {
        const { token } = get();
        if (token) return true;
        // Fallback: check localStorage for token set by login page
        if (typeof window !== 'undefined') {
          return !!localStorage.getItem('token');
        }
        return false;
      },

      hasRole: (roles) => {
        const { user } = get();
        if (!user) return false;
        return roles.includes(user.role);
      },

      canAccessCity: (cityId) => {
        const { user } = get();
        if (!user) return false;
        if (user.role === 'SUPER_ADMIN') return true;
        return user.cityAccess.includes(cityId);
      },

      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
        set({ user: null, token: null, selectedCityId: null });
      },
    }),
    {
      name: 'zeta-auth-storage',
      // Persist user and token, but NOT selectedCityId across hard refreshes
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
    }
  )
);
