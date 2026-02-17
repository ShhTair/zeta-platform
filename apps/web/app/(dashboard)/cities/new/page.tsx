'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateCity } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function NewCityPage() {
  const router = useRouter();
  const { hasRole } = useAuthStore();
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
  });
  const createCity = useCreateCity();

  if (!hasRole(['SUPER_ADMIN'])) {
    return (
      <Card>
        <p className="text-center text-red-500">Access denied. Super Admin only.</p>
      </Card>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await createCity.mutateAsync({
        ...formData,
        isActive: true,
      });
      router.push('/cities');
    } catch (error: any) {
      alert(error.response?.data?.message || 'Failed to create city');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Create New City</h1>
        <p className="text-gray-400 mt-1">Add a new city to the platform</p>
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

          <div className="flex gap-3">
            <Button type="submit" disabled={createCity.isPending}>
              {createCity.isPending ? 'Creating...' : 'Create City'}
            </Button>
            <Button 
              type="button" 
              variant="secondary" 
              onClick={() => router.back()}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
