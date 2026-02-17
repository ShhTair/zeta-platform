import { Product, AuditLog, AIValidation } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '/api';

export async function fetchProducts(cityId: string, page = 1, limit = 100): Promise<Product[]> {
  const response = await fetch(`${API_BASE}/cities/${cityId}/products?page=${page}&limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch products');
  return response.json();
}

export async function updateProduct(cityId: string, product: Product): Promise<Product> {
  const response = await fetch(`${API_BASE}/cities/${cityId}/products/${product.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(product),
  });
  if (!response.ok) throw new Error('Failed to update product');
  return response.json();
}

export async function deleteProduct(cityId: string, productId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/cities/${cityId}/products/${productId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete product');
}

export async function bulkUpdateProducts(cityId: string, products: Product[]): Promise<Product[]> {
  const response = await fetch(`${API_BASE}/cities/${cityId}/products/bulk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(products),
  });
  if (!response.ok) throw new Error('Failed to bulk update products');
  return response.json();
}

export async function validateWithAI(
  cityId: string,
  product: Partial<Product>
): Promise<AIValidation[]> {
  const response = await fetch(`${API_BASE}/cities/${cityId}/products/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(product),
  });
  if (!response.ok) throw new Error('Failed to validate product');
  return response.json();
}

export async function fetchAuditLogs(cityId: string, productId: number): Promise<AuditLog[]> {
  const response = await fetch(`${API_BASE}/cities/${cityId}/products/${productId}/audit-logs`);
  if (!response.ok) throw new Error('Failed to fetch audit logs');
  return response.json();
}
