'use client';

import { useAuthStore } from '@/lib/store';
import { useCities } from '@/lib/queries';
import { ChevronDown, Search } from 'lucide-react';

export default function Navbar() {
  const { user, selectedCityId, setSelectedCityId } = useAuthStore();
  const { data: cities } = useCities();

  const accessibleCities = cities?.filter(city => 
    user?.role === 'SUPER_ADMIN' || user?.cityAccess.includes(city.id)
  ) || [];

  const selectedCity = accessibleCities.find(c => c.id === selectedCityId);

  return (
    <div className="h-16 bg-white border-b border-[#DADCE0] flex items-center justify-between px-6 shadow-sm">
      {/* Left section - City selector */}
      <div className="flex items-center gap-6">
        {accessibleCities.length > 0 && (
          <div className="relative">
            <select
              value={selectedCityId || ''}
              onChange={(e) => setSelectedCityId(e.target.value || null)}
              className="appearance-none bg-white text-[#202124] px-4 py-2 pr-10 rounded-lg border border-[#DADCE0] hover:bg-[#F1F3F4] focus:outline-none focus:border-[#1A73E8] focus:ring-1 focus:ring-[#1A73E8] cursor-pointer text-[14px] font-medium transition-all"
            >
              <option value="">Select City</option>
              {accessibleCities.map(city => (
                <option key={city.id} value={city.id}>
                  {city.name}
                </option>
              ))}
            </select>
            <ChevronDown 
              className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#5F6368]" 
              size={16} 
            />
          </div>
        )}
        {selectedCity && (
          <div className="flex items-center gap-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${selectedCity.isActive ? 'bg-green-500' : 'bg-red-500'}`}></span>
            <span className="text-[#5F6368] text-[13px]">
              {selectedCity.isActive ? 'Active' : 'Inactive'}
            </span>
          </div>
        )}
      </div>

      {/* Center - Search bar (Google Drive style) */}
      <div className="flex-1 max-w-2xl mx-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5F6368]" size={20} />
          <input
            type="text"
            placeholder="Search in ZETA Platform"
            className="w-full bg-[#F1F3F4] text-[#202124] pl-11 pr-4 py-2.5 rounded-lg border-0 focus:outline-none focus:bg-white focus:shadow-google-md transition-all text-[14px]"
          />
        </div>
      </div>

      {/* Right section - User info */}
      <div className="flex items-center gap-4">
        <div className="text-sm flex items-center gap-2">
          <span className="text-[#5F6368] text-[13px]">Role:</span>
          <span className="text-[#202124] font-medium text-[13px] bg-[#F1F3F4] px-3 py-1 rounded-full">
            {user?.role.replace('_', ' ')}
          </span>
        </div>
        
        {/* User Avatar (Google Drive style) */}
        <div className="w-8 h-8 rounded-full bg-[#1A73E8] flex items-center justify-center text-white text-sm font-medium">
          {user?.email?.charAt(0).toUpperCase() || 'U'}
        </div>
      </div>
    </div>
  );
}
