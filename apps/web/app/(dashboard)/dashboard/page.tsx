'use client';

import { useAuthStore } from '@/lib/store';
import { useCities } from '@/lib/queries';
import Card from '@/components/ui/Card';
import { Building2, Users, Bot } from 'lucide-react';

export default function DashboardPage() {
  const { user, selectedCityId } = useAuthStore();
  const { data: cities } = useCities();

  const accessibleCities = cities?.filter(city => 
    user?.role === 'SUPER_ADMIN' || user?.cityAccess.includes(city.id)
  ) || [];

  const selectedCity = accessibleCities.find(c => c.id === selectedCityId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-400 mt-1">Welcome back, {user?.name}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-600 rounded-lg">
              <Building2 size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-400">Accessible Cities</p>
              <p className="text-2xl font-bold">{accessibleCities.length}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-600 rounded-lg">
              <Bot size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-400">Active Bots</p>
              <p className="text-2xl font-bold">
                {accessibleCities.filter(c => c.isActive).length}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-600 rounded-lg">
              <Users size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-400">Your Role</p>
              <p className="text-lg font-bold">{user?.role.replace('_', ' ')}</p>
            </div>
          </div>
        </Card>
      </div>

      {!selectedCityId && accessibleCities.length > 0 && (
        <Card className="border-yellow-600">
          <div className="flex items-center gap-3">
            <div className="text-yellow-500">⚠️</div>
            <div>
              <h3 className="font-semibold">No City Selected</h3>
              <p className="text-sm text-gray-400">
                Please select a city from the dropdown above to access city-specific features.
              </p>
            </div>
          </div>
        </Card>
      )}

      {selectedCity && (
        <Card>
          <h2 className="text-xl font-bold mb-4">Selected City: {selectedCity.name}</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Slug:</span>
              <span>{selectedCity.slug}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Status:</span>
              <span className={selectedCity.isActive ? 'text-green-500' : 'text-red-500'}>
                {selectedCity.isActive ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Created:</span>
              <span>{new Date(selectedCity.createdAt).toLocaleDateString()}</span>
            </div>
          </div>
        </Card>
      )}

      {accessibleCities.length === 0 && (
        <Card>
          <div className="text-center py-8">
            <Building2 size={48} className="mx-auto text-gray-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Cities Available</h3>
            <p className="text-gray-400">
              You don't have access to any cities yet. Contact an administrator.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
