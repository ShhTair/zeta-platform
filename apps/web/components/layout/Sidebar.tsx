'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Building2, 
  Bot, 
  Package, 
  BarChart3, 
  FileText, 
  User,
  LogOut
} from 'lucide-react';
import { useAuthStore } from '@/lib/store';

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout, hasRole, selectedCityId } = useAuthStore();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, show: true },
    { href: '/cities', label: 'Cities', icon: Building2, show: hasRole(['SUPER_ADMIN']) },
    { 
      href: selectedCityId ? `/cities/${selectedCityId}/settings` : '#', 
      label: 'City Settings', 
      icon: Building2, 
      show: selectedCityId && hasRole(['CITY_ADMIN', 'SUPER_ADMIN']) 
    },
    { 
      href: selectedCityId ? `/cities/${selectedCityId}/bot-config` : '#', 
      label: 'Bot Config', 
      icon: Bot, 
      show: selectedCityId && hasRole(['CITY_ADMIN', 'SUPER_ADMIN']) 
    },
    { 
      href: selectedCityId ? `/cities/${selectedCityId}/products` : '#', 
      label: 'Products', 
      icon: Package, 
      show: selectedCityId 
    },
    { 
      href: selectedCityId ? `/cities/${selectedCityId}/analytics` : '#', 
      label: 'Analytics', 
      icon: BarChart3, 
      show: selectedCityId && hasRole(['CITY_ADMIN', 'SUPER_ADMIN']) 
    },
    { 
      href: selectedCityId ? `/cities/${selectedCityId}/audit-logs` : '#', 
      label: 'Audit Logs', 
      icon: FileText, 
      show: selectedCityId && hasRole(['CITY_ADMIN', 'SUPER_ADMIN']) 
    },
    { href: '/profile', label: 'Profile', icon: User, show: true },
  ];

  return (
    <aside className="w-64 bg-gdrive-white h-screen sticky top-0 flex flex-col border-r border-gdrive-border">
      {/* Logo/Brand Section - Google Drive style */}
      <div className="px-4 py-5 border-b border-gdrive-border">
        <h1 className="text-2xl font-medium text-gdrive-text tracking-tight">ZETA Platform</h1>
        {user && (
          <p className="text-sm text-gdrive-secondary mt-1 truncate">{user.email}</p>
        )}
      </div>

      {/* Navigation - Google Drive style */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <div className="space-y-1">
          {navItems.filter(item => item.show).map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-4 px-3 py-2.5 rounded-google 
                  transition-all duration-200 group
                  ${isActive
                    ? 'bg-gdrive-hover text-gdrive-blue font-medium'
                    : 'text-gdrive-text hover:bg-gdrive-gray-hover'
                  }
                `}
              >
                <Icon 
                  size={20} 
                  className={`flex-shrink-0 transition-colors ${
                    isActive ? 'text-gdrive-blue' : 'text-gdrive-secondary group-hover:text-gdrive-text'
                  }`}
                  strokeWidth={2}
                />
                <span className="text-sm truncate">
                  {item.label}
                </span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Logout Section - Google Drive style */}
      <div className="px-3 py-4 border-t border-gdrive-border">
        <button
          onClick={handleLogout}
          className="
            flex items-center gap-4 px-3 py-2.5 w-full rounded-google
            text-gdrive-text hover:bg-gdrive-gray-hover 
            transition-all duration-200 group
          "
        >
          <LogOut 
            size={20} 
            className="flex-shrink-0 text-gdrive-secondary group-hover:text-gdrive-text"
            strokeWidth={2}
          />
          <span className="text-sm">Logout</span>
        </button>
      </div>
    </aside>
  );
}
