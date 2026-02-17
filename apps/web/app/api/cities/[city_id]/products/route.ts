import { NextRequest, NextResponse } from 'next/server';

// Mock database
let mockProducts = [
  {
    id: 1,
    sku: 'PROD-001',
    name: 'Wireless Mouse',
    description: 'Ergonomic wireless mouse with 2.4GHz connectivity',
    category: 'Electronics',
    price: 29.99,
    stock: 150,
    link: 'https://example.com/mouse',
    is_active: true,
    created_at: '2026-01-15T10:00:00Z',
    updated_at: '2026-02-10T14:30:00Z',
    updated_by: 'admin@example.com',
  },
  {
    id: 2,
    sku: 'PROD-002',
    name: 'USB-C Cable',
    description: 'High-speed USB-C charging cable, 2m length',
    category: 'Accessories',
    price: 12.99,
    stock: 500,
    link: 'https://example.com/cable',
    is_active: true,
    created_at: '2026-01-16T09:00:00Z',
    updated_at: '2026-02-11T11:00:00Z',
    updated_by: 'john@example.com',
  },
  {
    id: 3,
    sku: 'PROD-003',
    name: 'Mechanical Keyboard',
    description: 'RGB backlit mechanical keyboard with Cherry MX switches',
    category: 'Electronics',
    price: 89.99,
    stock: 75,
    link: 'https://example.com/keyboard',
    is_active: true,
    created_at: '2026-01-17T08:00:00Z',
    updated_at: '2026-02-12T16:45:00Z',
    updated_by: 'admin@example.com',
  },
];

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ city_id: string }> }
) {
  const { city_id } = await params;
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get('page') || '1');
  const limit = parseInt(searchParams.get('limit') || '100');

  // Simple pagination
  const start = (page - 1) * limit;
  const end = start + limit;
  const paginatedProducts = mockProducts.slice(start, end);

  return NextResponse.json(paginatedProducts);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ city_id: string }> }
) {
  const { city_id } = await params;
  const product = await request.json();
  const newProduct = {
    ...product,
    id: mockProducts.length + 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
  mockProducts.push(newProduct);
  return NextResponse.json(newProduct, { status: 201 });
}
