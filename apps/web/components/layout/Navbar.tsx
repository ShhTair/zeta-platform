'use client';

import { useAuthStore } from '@/lib/store';
import { useCities } from '@/lib/queries';
import { ChevronDown } from 'lucide-react';

export default function Navbar() {
  const { user, selectedCityId, setSelectedCityId } = useAuthStore();
  const { data: cities } = useCities();

  const accessibleCities = cities?.filter(city => 
    user?.role === 'SUPER_ADMIN' || user?.cityAccess.includes(city.id)
  ) || [];

  const selectedCity = accessibleCities.find(c => c.id === selectedCityId);

  return (
    <div className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        {accessibleCities.length > 0 && (
          <div className="relative">
            <select
              value={selectedCityId || ''}
              onChange={(e) => setSelectedCityId(e.target.value || null)}
              className="appearance-none bg-gray-800 text-white px-4 py-2 pr-10 rounded-lg border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              <option value="">Select City</option>
              {accessibleCities.map(city => (
                <option key={city.id} value={city.id}>
                  {city.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400" size={16} />
          </div>
        )}
        {selectedCity && (
          <div className="text-sm text-gray-400">
            {selectedCity.isActive ? (
              <span className="text-green-500">● Active</span>
            ) : (
              <span className="text-red-500">● Inactive</span>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <div className="text-sm">
          <span className="text-gray-400">Role:</span>
          <span className="ml-2 text-white font-medium">
            {user?.role.replace('_', ' ')}
          </span>
        </div>
      </div>
    </div>
  );
}
