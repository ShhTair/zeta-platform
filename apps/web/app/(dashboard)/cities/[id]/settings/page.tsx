'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useCity, useUpdateCity } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function CitySettingsPage() {
  const params = useParams();
  const cityId = params.id as string;
  const { hasRole, canAccessCity } = useAuthStore();
  const { data: city, isLoading } = useCity(cityId);
  const updateCity = useUpdateCity();

  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    isActive: true,
  });

  useEffect(() => {
    if (city) {
      setFormData({
        name: city.name,
        slug: city.slug,
        isActive: city.isActive,
      });
    }
  }, [city]);

  if (!hasRole(['SUPER_ADMIN', 'CITY_ADMIN']) || !canAccessCity(cityId)) {
    return (
      <Card>
        <p className="text-center text-[#D93025] text-[14px]">Access denied.</p>
      </Card>
    );
  }

  if (isLoading) {
    return <div className="text-[#5F6368] text-[14px]">Loading...</div>;
  }

  if (!city) {
    return <Card><p className="text-[#5F6368]">City not found</p></Card>;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await updateCity.mutateAsync({
        id: cityId,
        ...formData,
      });
      alert('City updated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.message || 'Failed to update city');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-[28px] font-medium text-[#202124]">City Settings</h1>
        <p className="text-[#5F6368] mt-1 text-[14px]">{city.name}</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            label="City Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Los Angeles"
            required
          />

          <Input
            label="Slug (URL-friendly)"
            value={formData.slug}
            onChange={(e) => setFormData({ 
              ...formData, 
              slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') 
            })}
            placeholder="los-angeles"
            required
          />

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="isActive"
              checked={formData.isActive}
              onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
              className="w-4 h-4 text-[#1A73E8] bg-white border-[#DADCE0] rounded focus:ring-[#1A73E8]"
            />
            <label htmlFor="isActive" className="text-[14px] font-medium text-[#202124]">
              City is active
            </label>
          </div>

          <div className="pt-2">
            <Button type="submit" disabled={updateCity.isPending}>
              {updateCity.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </Card>

      <Card>
        <h2 className="text-[16px] font-medium text-[#202124] mb-4">City Information</h2>
        <div className="space-y-3 text-[14px]">
          <div className="flex justify-between py-2 border-b border-[#F1F3F4]">
            <span className="text-[#5F6368]">City ID:</span>
            <span className="font-mono text-[#202124]">{city.id}</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-[#5F6368]">Created:</span>
            <span className="text-[#202124]">{new Date(city.createdAt).toLocaleString()}</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
