'use client';

import { useAuthStore } from '@/lib/store';
import { useCities } from '@/lib/queries';
import Card from '@/components/ui/Card';
import { Building2, Users, Bot, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const { user, selectedCityId } = useAuthStore();
  const { data: cities } = useCities();

  const accessibleCities = cities?.filter(city => 
    user?.role === 'SUPER_ADMIN' || user?.cityAccess.includes(city.id)
  ) || [];

  const selectedCity = accessibleCities.find(c => c.id === selectedCityId);

  return (
    <div className="space-y-8">
      {/* Page Header - Google Drive style */}
      <div>
        <h1 className="text-3xl font-medium text-gdrive-text">Dashboard</h1>
        <p className="text-gdrive-secondary mt-2">Welcome back, {user?.name}</p>
      </div>

      {/* Stats Cards - Google Drive style */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card hover>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gdrive-hover rounded-google">
              <Building2 size={28} className="text-gdrive-blue" strokeWidth={2} />
            </div>
            <div>
              <p className="text-xs text-gdrive-secondary uppercase tracking-wide">Accessible Cities</p>
              <p className="text-3xl font-medium text-gdrive-text mt-1">{accessibleCities.length}</p>
            </div>
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gdrive-success-bg rounded-google">
              <Bot size={28} className="text-gdrive-success" strokeWidth={2} />
            </div>
            <div>
              <p className="text-xs text-gdrive-secondary uppercase tracking-wide">Active Bots</p>
              <p className="text-3xl font-medium text-gdrive-text mt-1">
                {accessibleCities.filter(c => c.isActive).length}
              </p>
            </div>
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gdrive-gray-hover rounded-google">
              <Users size={28} className="text-gdrive-secondary" strokeWidth={2} />
            </div>
            <div>
              <p className="text-xs text-gdrive-secondary uppercase tracking-wide">Your Role</p>
              <p className="text-lg font-medium text-gdrive-text mt-1">{user?.role.replace('_', ' ')}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Warning Banner - Google Drive style */}
      {!selectedCityId && accessibleCities.length > 0 && (
        <Card className="border-gdrive-warning bg-gdrive-warning-bg border-l-4">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-gdrive-warning flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-gdrive-text">No City Selected</h3>
              <p className="text-sm text-gdrive-secondary mt-1">
                Please select a city from the dropdown in the navigation bar to access city-specific features.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Selected City Details - Google Drive style */}
      {selectedCity && (
        <Card>
          <h2 className="text-xl font-medium text-gdrive-text mb-4">
            Selected City: {selectedCity.name}
          </h2>
          <div className="space-y-0">
            <div className="flex justify-between py-3 border-b border-gdrive-border">
              <span className="text-sm text-gdrive-secondary">Slug</span>
              <span className="text-sm text-gdrive-text font-medium">{selectedCity.slug}</span>
            </div>
            <div className="flex justify-between py-3 border-b border-gdrive-border">
              <span className="text-sm text-gdrive-secondary">Status</span>
              <span className={`text-sm font-medium flex items-center gap-2 ${
                selectedCity.isActive ? 'text-gdrive-success' : 'text-gdrive-danger'
              }`}>
                <span className={`w-2 h-2 rounded-full ${
                  selectedCity.isActive ? 'bg-gdrive-success' : 'bg-gdrive-danger'
                }`}></span>
                {selectedCity.isActive ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex justify-between py-3">
              <span className="text-sm text-gdrive-secondary">Created</span>
              <span className="text-sm text-gdrive-text font-medium">
                {new Date(selectedCity.createdAt).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </span>
            </div>
          </div>
        </Card>
      )}

      {/* Empty State - Google Drive style */}
      {accessibleCities.length === 0 && (
        <Card>
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gdrive-gray-hover rounded-full flex items-center justify-center mx-auto mb-6">
              <Building2 size={40} className="text-gdrive-secondary" strokeWidth={2} />
            </div>
            <h3 className="text-xl font-medium text-gdrive-text mb-2">No Cities Available</h3>
            <p className="text-gdrive-secondary max-w-md mx-auto">
              You don't have access to any cities yet. Contact your administrator to request access.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
