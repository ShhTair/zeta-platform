'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  requiresCityAccess?: boolean;
}

export default function ProtectedRoute({ 
  children, 
  requiredRoles,
  requiresCityAccess = false 
}: ProtectedRouteProps) {
  const router = useRouter();
  const { user, isAuthenticated, hasRole, selectedCityId, canAccessCity } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    if (requiredRoles && !hasRole(requiredRoles)) {
      router.push('/dashboard');
      return;
    }

    if (requiresCityAccess && selectedCityId && !canAccessCity(selectedCityId)) {
      router.push('/dashboard');
      return;
    }
  }, [isAuthenticated, hasRole, canAccessCity, selectedCityId, router, requiredRoles, requiresCityAccess]);

  if (!isAuthenticated()) {
    return null;
  }

  if (requiredRoles && !hasRole(requiredRoles)) {
    return null;
  }

  if (requiresCityAccess && selectedCityId && !canAccessCity(selectedCityId)) {
    return null;
  }

  return <>{children}</>;
}
