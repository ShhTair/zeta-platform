import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ city_id: string }> }
) {
  const { city_id } = await params;
  const products = await request.json();

  // In a real app, this would do bulk update in database
  const updated = products.map((p: any) => ({
    ...p,
    updated_at: new Date().toISOString(),
  }));

  return NextResponse.json(updated);
}
