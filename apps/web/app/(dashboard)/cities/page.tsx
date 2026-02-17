'use client';

import { useCities } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Link from 'next/link';
import { Plus, Building2 } from 'lucide-react';

export default function CitiesPage() {
  const { hasRole } = useAuthStore();
  const { data: cities, isLoading } = useCities();

  if (!hasRole(['SUPER_ADMIN'])) {
    return (
      <Card>
        <p className="text-center text-red-500">Access denied. Super Admin only.</p>
      </Card>
    );
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Cities</h1>
        <Link href="/cities/new">
          <Button>
            <Plus size={16} className="mr-2" />
            New City
          </Button>
        </Link>
      </div>

      {cities && cities.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cities.map((city) => (
            <Card key={city.id}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <Building2 size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold">{city.name}</h3>
                    <p className="text-sm text-gray-400">{city.slug}</p>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  city.isActive 
                    ? 'bg-green-600 text-white' 
                    : 'bg-red-600 text-white'
                }`}>
                  {city.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="text-sm text-gray-400 mb-4">
                Created {new Date(city.createdAt).toLocaleDateString()}
              </div>
              <Link href={`/cities/${city.id}/settings`}>
                <Button variant="secondary" size="sm" className="w-full">
                  Manage
                </Button>
              </Link>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-8">
            <Building2 size={48} className="mx-auto text-gray-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Cities Yet</h3>
            <p className="text-gray-400 mb-4">Create your first city to get started.</p>
            <Link href="/cities/new">
              <Button>
                <Plus size={16} className="mr-2" />
                Create City
              </Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
}
