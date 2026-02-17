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
        <p className="text-center text-red-500">Access denied.</p>
      </Card>
    );
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!city) {
    return <Card><p>City not found</p></Card>;
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
      <div>
        <h1 className="text-3xl font-bold">City Settings</h1>
        <p className="text-gray-400 mt-1">{city.name}</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
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
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
            />
            <label htmlFor="isActive" className="text-sm font-medium">
              City is active
            </label>
          </div>

          <Button type="submit" disabled={updateCity.isPending}>
            {updateCity.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </form>
      </Card>

      <Card>
        <h2 className="text-lg font-bold mb-2">City Information</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">City ID:</span>
            <span className="font-mono">{city.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Created:</span>
            <span>{new Date(city.createdAt).toLocaleString()}</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
