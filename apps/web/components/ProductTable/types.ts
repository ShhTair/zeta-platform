export interface Product {
  id: number;
  sku: string;
  name: string;
  description: string;
  category: string;
  price: number;
  stock: number;
  link: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  updated_by: string;
}

export interface AuditLog {
  id: number;
  user_id: number;
  user_name: string;
  product_id: number;
  field_name: string;
  old_value: string;
  new_value: string;
  created_at: string;
}

export interface AIValidation {
  field: string;
  suggestion: string;
  confidence: number;
  issue?: string;
}

export interface HistoryAction {
  type: 'edit' | 'delete' | 'add' | 'bulk';
  productId: number;
  field?: string;
  oldValue?: any;
  newValue?: any;
  timestamp: number;
  products?: Product[];
}

export type SortDirection = 'ASC' | 'DESC' | 'NONE';

export interface ColumnFilter {
  field: keyof Product;
  value: string;
}
