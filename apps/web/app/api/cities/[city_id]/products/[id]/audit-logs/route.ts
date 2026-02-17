import { NextRequest, NextResponse } from 'next/server';

// Mock audit logs
const mockAuditLogs = [
  {
    id: 1,
    user_id: 1,
    user_name: 'admin@example.com',
    product_id: 1,
    field_name: 'price',
    old_value: '24.99',
    new_value: '29.99',
    created_at: '2026-02-10T14:30:00Z',
  },
  {
    id: 2,
    user_id: 2,
    user_name: 'john@example.com',
    product_id: 1,
    field_name: 'stock',
    old_value: '100',
    new_value: '150',
    created_at: '2026-02-09T10:15:00Z',
  },
  {
    id: 3,
    user_id: 1,
    user_name: 'admin@example.com',
    product_id: 1,
    field_name: 'description',
    old_value: 'Wireless mouse',
    new_value: 'Ergonomic wireless mouse with 2.4GHz connectivity',
    created_at: '2026-02-08T09:00:00Z',
  },
];

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ city_id: string; id: string }> }
) {
  const { city_id, id: idStr } = await params;
  const productId = parseInt(idStr);
  const logs = mockAuditLogs
    .filter((log) => log.product_id === productId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return NextResponse.json(logs);
}
