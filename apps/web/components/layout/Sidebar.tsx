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
    <div className="w-64 bg-white border-r border-[#DADCE0] flex flex-col shadow-sm">
      {/* Logo/Brand Section */}
      <div className="px-6 py-5 border-b border-[#DADCE0]">
        <h1 className="text-[22px] font-medium text-[#202124]">ZETA Platform</h1>
        {user && (
          <p className="text-sm text-[#5F6368] mt-1">{user.email}</p>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-2">
        <div className="space-y-1">
          {navItems.filter(item => item.show).map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 group ${
                  isActive
                    ? 'bg-[#E8F0FE] text-[#1A73E8]'
                    : 'text-[#5F6368] hover:bg-[#F1F3F4]'
                }`}
              >
                <Icon 
                  size={20} 
                  className={`transition-colors ${
                    isActive ? 'text-[#1A73E8]' : 'text-[#5F6368] group-hover:text-[#202124]'
                  }`}
                  strokeWidth={2}
                />
                <span className={`text-[14px] font-medium ${
                  isActive ? 'text-[#1A73E8]' : 'text-[#202124]'
                }`}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Logout Section */}
      <div className="px-3 py-3 border-t border-[#DADCE0]">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-[#5F6368] hover:bg-[#F1F3F4] transition-all duration-150 group"
        >
          <LogOut 
            size={20} 
            className="text-[#5F6368] group-hover:text-[#202124]"
            strokeWidth={2}
          />
          <span className="text-[14px] font-medium text-[#202124]">Logout</span>
        </button>
      </div>
    </div>
  );
}
