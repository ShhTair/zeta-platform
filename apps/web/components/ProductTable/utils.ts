import Papa from 'papaparse';
import { Product } from './types';

export function exportToCSV(products: Product[], filename = 'products.csv') {
  const csv = Papa.unparse(products);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function importFromCSV(file: File): Promise<Partial<Product>[]> {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const products = results.data.map((row: any) => ({
          sku: row.sku || '',
          name: row.name || '',
          description: row.description || '',
          category: row.category || '',
          price: parseFloat(row.price) || 0,
          stock: parseInt(row.stock) || 0,
          link: row.link || '',
          is_active: row.is_active === 'true' || row.is_active === '1',
        }));
        resolve(products);
      },
      error: (error) => reject(error),
    });
  });
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
}

export function validatePrice(price: number): { valid: boolean; message?: string } {
  if (price < 0) return { valid: false, message: 'Price cannot be negative' };
  if (price > 1000000) return { valid: false, message: 'Price seems unreasonably high' };
  if (price === 0) return { valid: true, message: 'Warning: Price is zero' };
  return { valid: true };
}

export function validateStock(stock: number): { valid: boolean; message?: string } {
  if (stock < 0) return { valid: false, message: 'Stock cannot be negative' };
  if (stock > 100000) return { valid: false, message: 'Stock seems unreasonably high' };
  return { valid: true };
}
