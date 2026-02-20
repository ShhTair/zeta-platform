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
        <p className="text-center text-[#D93025] text-[14px]">Access denied. Super Admin only.</p>
      </Card>
    );
  }

  if (isLoading) {
    return <div className="text-[#5F6368] text-[14px]">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-[28px] font-medium text-[#202124]">Cities</h1>
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
            <Card key={city.id} hover>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#E8F0FE] rounded-lg">
                    <Building2 size={20} className="text-[#1A73E8]" />
                  </div>
                  <div>
                    <h3 className="font-medium text-[#202124] text-[15px]">{city.name}</h3>
                    <p className="text-[13px] text-[#5F6368]">{city.slug}</p>
                  </div>
                </div>
                <span className={`text-[12px] px-2.5 py-1 rounded-full font-medium ${
                  city.isActive 
                    ? 'bg-[#E6F4EA] text-[#1E8E3E]' 
                    : 'bg-[#FCE8E6] text-[#D93025]'
                }`}>
                  {city.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="text-[13px] text-[#5F6368] mb-4">
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
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-[#F1F3F4] rounded-full flex items-center justify-center mx-auto mb-4">
              <Building2 size={32} className="text-[#5F6368]" />
            </div>
            <h3 className="text-[18px] font-medium text-[#202124] mb-2">No Cities Yet</h3>
            <p className="text-[#5F6368] text-[14px] mb-6">Create your first city to get started.</p>
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
