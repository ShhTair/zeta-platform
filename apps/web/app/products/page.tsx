'use client';

import ProductTable from '@/components/ProductTable';

export default function ProductsPage() {
  // In a real app, these would come from auth/routing
  const cityId = 'city-123';
  const currentUser = 'demo-user';

  return (
    <div className="w-full h-screen">
      <ProductTable cityId={cityId} currentUser={currentUser} />
    </div>
  );
}
