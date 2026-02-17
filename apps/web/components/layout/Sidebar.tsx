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
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold text-white">ZETA Platform</h1>
        {user && (
          <p className="text-sm text-gray-400 mt-2">{user.email}</p>
        )}
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.filter(item => item.show).map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}
