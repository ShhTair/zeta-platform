'use client';

import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import { Building2, Users, Bot, AlertCircle, CheckCircle } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuthStore();
  
  // Mock data for client-side demo
  const accessibleCities = user?.role === 'SUPER_ADMIN' ? [
    { id: '1', name: 'Almaty', slug: 'almaty', isActive: true, createdAt: new Date().toISOString() },
    { id: '2', name: 'Astana', slug: 'astana', isActive: true, createdAt: new Date().toISOString() },
  ] : [];

  const selectedCity = accessibleCities[0]; // Default to first city for demo

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

      {/* Success Banner - Demo Mode */}
      {accessibleCities.length > 0 && (
        <Card className="border-gdrive-success bg-gdrive-success-bg border-l-4">
          <div className="flex items-start gap-3">
            <CheckCircle size={20} className="text-gdrive-success flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-gdrive-text">Welcome to ZETA Platform</h3>
              <p className="text-sm text-gdrive-secondary mt-1">
                You're logged in as {user?.name}. This is a demo dashboard with mock data.
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
