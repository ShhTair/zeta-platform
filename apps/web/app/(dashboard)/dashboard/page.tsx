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
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-[28px] font-medium text-[#202124]">Dashboard</h1>
        <p className="text-[#5F6368] mt-1 text-[14px]">Welcome back, {user?.name}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card hover>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-[#E8F0FE] rounded-lg">
              <Building2 size={24} className="text-[#1A73E8]" />
            </div>
            <div>
              <p className="text-[13px] text-[#5F6368]">Accessible Cities</p>
              <p className="text-[24px] font-medium text-[#202124]">{accessibleCities.length}</p>
            </div>
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-[#E6F4EA] rounded-lg">
              <Bot size={24} className="text-[#1E8E3E]" />
            </div>
            <div>
              <p className="text-[13px] text-[#5F6368]">Active Bots</p>
              <p className="text-[24px] font-medium text-[#202124]">
                {accessibleCities.filter(c => c.isActive).length}
              </p>
            </div>
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-[#F1F3F4] rounded-lg">
              <Users size={24} className="text-[#5F6368]" />
            </div>
            <div>
              <p className="text-[13px] text-[#5F6368]">Your Role</p>
              <p className="text-[16px] font-medium text-[#202124]">{user?.role.replace('_', ' ')}</p>
            </div>
          </div>
        </Card>
      </div>

      {!selectedCityId && accessibleCities.length > 0 && (
        <Card className="border-[#FDD663] bg-[#FEF7E0]">
          <div className="flex items-center gap-3">
            <AlertCircle size={20} className="text-[#E37400]" />
            <div>
              <h3 className="font-medium text-[#202124] text-[14px]">No City Selected</h3>
              <p className="text-[13px] text-[#5F6368] mt-0.5">
                Please select a city from the dropdown above to access city-specific features.
              </p>
            </div>
          </div>
        </Card>
      )}

      {selectedCity && (
        <Card>
          <h2 className="text-[18px] font-medium text-[#202124] mb-4">Selected City: {selectedCity.name}</h2>
          <div className="space-y-3 text-[14px]">
            <div className="flex justify-between py-2 border-b border-[#F1F3F4]">
              <span className="text-[#5F6368]">Slug:</span>
              <span className="text-[#202124] font-medium">{selectedCity.slug}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-[#F1F3F4]">
              <span className="text-[#5F6368]">Status:</span>
              <span className={`font-medium ${selectedCity.isActive ? 'text-[#1E8E3E]' : 'text-[#D93025]'}`}>
                {selectedCity.isActive ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-[#5F6368]">Created:</span>
              <span className="text-[#202124] font-medium">{new Date(selectedCity.createdAt).toLocaleDateString()}</span>
            </div>
          </div>
        </Card>
      )}

      {accessibleCities.length === 0 && (
        <Card>
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-[#F1F3F4] rounded-full flex items-center justify-center mx-auto mb-4">
              <Building2 size={32} className="text-[#5F6368]" />
            </div>
            <h3 className="text-[18px] font-medium text-[#202124] mb-2">No Cities Available</h3>
            <p className="text-[#5F6368] text-[14px]">
              You don't have access to any cities yet. Contact an administrator.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
