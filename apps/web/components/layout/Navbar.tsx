'use client';

import { useAuthStore } from '@/lib/store';
import { ChevronDown, Search } from 'lucide-react';

export default function Navbar() {
  const { user, selectedCityId, setSelectedCityId } = useAuthStore();
  
  // Mock cities for demo
  const cities = user?.role === 'SUPER_ADMIN' ? [
    { id: '1', name: 'Almaty', slug: 'almaty', isActive: true },
    { id: '2', name: 'Astana', slug: 'astana', isActive: true },
  ] : [];

  const accessibleCities = cities;

  const selectedCity = accessibleCities.find(c => c.id === selectedCityId);

  return (
    <header className="h-16 bg-gdrive-white border-b border-gdrive-border flex items-center justify-between px-6 sticky top-0 z-10">
      {/* Left section - City selector */}
      <div className="flex items-center gap-4">
        {accessibleCities.length > 0 && (
          <div className="relative">
            <select
              value={selectedCityId || ''}
              onChange={(e) => setSelectedCityId(e.target.value || null)}
              className="
                appearance-none bg-gdrive-white text-gdrive-text 
                px-4 py-2 pr-10 rounded-google-sm 
                border border-gdrive-border 
                hover:bg-gdrive-gray-hover hover:shadow-google-sm
                focus:outline-none focus:border-gdrive-blue focus:shadow-google-sm
                cursor-pointer text-sm font-medium 
                transition-all duration-200
              "
            >
              <option value="">Select City</option>
              {accessibleCities.map(city => (
                <option key={city.id} value={city.id}>
                  {city.name}
                </option>
              ))}
            </select>
            <ChevronDown 
              className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gdrive-secondary" 
              size={16} 
            />
          </div>
        )}
        {selectedCity && (
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${selectedCity.isActive ? 'bg-gdrive-success' : 'bg-gdrive-danger'}`}></span>
            <span className="text-xs text-gdrive-secondary">
              {selectedCity.isActive ? 'Active' : 'Inactive'}
            </span>
          </div>
        )}
      </div>

      {/* Center - Search bar (Google Drive style) */}
      <div className="flex-1 max-w-2xl mx-8">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gdrive-secondary" size={20} />
          <input
            type="text"
            placeholder="Search in ZETA Platform"
            className="
              w-full bg-gdrive-bg text-gdrive-text 
              pl-12 pr-4 py-2.5 rounded-google
              border-0 
              focus:outline-none focus:bg-gdrive-white focus:shadow-google-md 
              transition-all duration-200 
              placeholder:text-gdrive-secondary
            "
          />
        </div>
      </div>

      {/* Right section - User info */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gdrive-secondary">Role:</span>
          <span className="text-xs text-gdrive-text font-medium bg-gdrive-gray-hover px-3 py-1.5 rounded-full">
            {user?.role.replace('_', ' ')}
          </span>
        </div>
        
        {/* User Avatar (Google Drive style) */}
        <div 
          className="w-9 h-9 rounded-full bg-gdrive-blue flex items-center justify-center text-white text-sm font-medium cursor-pointer hover:shadow-google-sm transition-shadow"
          title={user?.email}
        >
          {user?.email?.charAt(0).toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  );
}
