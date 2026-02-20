'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { DataGrid, Column, SelectColumn } from 'react-data-grid';
import 'react-data-grid/lib/styles.css';
import '@/app/data-grid-custom.css';
import toast, { Toaster } from 'react-hot-toast';
import { Product, AIValidation, SortDirection } from './types';
import {
  fetchProducts,
  updateProduct,
  deleteProduct,
  validateWithAI,
} from './api';
import { exportToCSV, importFromCSV, debounce } from './utils';
import Toolbar from './Toolbar';
import AuditPanel from './AuditPanel';
import { useHistory } from './useHistory';

interface ProductTableProps {
  cityId: string;
  currentUser: string;
}

export default function ProductTable({ cityId, currentUser }: ProductTableProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [aiEnabled, setAiEnabled] = useState(false);
  const [showAuditPanel, setShowAuditPanel] = useState(false);
  const [selectedProductForAudit, setSelectedProductForAudit] = useState<number | null>(null);
  const [aiValidations, setAiValidations] = useState<Record<number, AIValidation[]>>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [sortColumn, setSortColumn] = useState<keyof Product | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('NONE');

  const { addAction, undo, redo, canUndo, canRedo } = useHistory();

  // Load products
  useEffect(() => {
    loadProducts();
  }, [cityId]);

  // Filter and search
  useEffect(() => {
    let filtered = [...products];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((p) =>
        Object.values(p).some((val) =>
          String(val).toLowerCase().includes(query)
        )
      );
    }

    if (sortColumn && sortDirection !== 'NONE') {
      filtered.sort((a, b) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];
        if (aVal === bVal) return 0;
        const comparison = aVal > bVal ? 1 : -1;
        return sortDirection === 'ASC' ? comparison : -comparison;
      });
    }

    setFilteredProducts(filtered);
  }, [products, searchQuery, sortColumn, sortDirection]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await fetchProducts(cityId);
      setProducts(data);
    } catch (error: any) {
      toast.error(`Failed to load products: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Debounced save
  const debouncedSave = useMemo(
    () =>
      debounce(async (product: Product) => {
        try {
          await updateProduct(cityId, product);
          toast.success('Saved');
        } catch (error: any) {
          toast.error(`Save failed: ${error.message}`);
          loadProducts(); // Rollback
        }
      }, 1000),
    [cityId]
  );

  const handleRowsChange = (rows: Product[], { indexes }: any) => {
    const updatedProducts = [...products];
    indexes.forEach((idx: number) => {
      const oldProduct = products[idx];
      const newProduct = rows[idx];

      // Find changed field
      let changedField: keyof Product | null = null;
      for (const key in newProduct) {
        if (newProduct[key as keyof Product] !== oldProduct[key as keyof Product]) {
          changedField = key as keyof Product;
          break;
        }
      }

      if (changedField) {
        addAction({
          type: 'edit',
          productId: newProduct.id,
          field: changedField,
          oldValue: oldProduct[changedField],
          newValue: newProduct[changedField],
          timestamp: Date.now(),
        });

        // Update metadata
        newProduct.updated_at = new Date().toISOString();
        newProduct.updated_by = currentUser;

        // Trigger AI validation if enabled
        if (aiEnabled) {
          validateProduct(newProduct);
        }

        // Save to backend
        debouncedSave(newProduct);
      }

      updatedProducts[idx] = newProduct;
    });

    setProducts(updatedProducts);
  };

  const validateProduct = async (product: Product) => {
    try {
      const validations = await validateWithAI(cityId, product);
      setAiValidations((prev) => ({ ...prev, [product.id]: validations }));
    } catch (error: any) {
      console.error('AI validation failed:', error);
    }
  };

  const handleAddRow = () => {
    const newProduct: Product = {
      id: Date.now(), // Temporary ID
      sku: '',
      name: '',
      description: '',
      category: '',
      price: 0,
      stock: 0,
      link: '',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      updated_by: currentUser,
    };

    setProducts([...products, newProduct]);
    addAction({
      type: 'add',
      productId: newProduct.id,
      timestamp: Date.now(),
    });
    toast.success('Row added');
  };

  const handleDelete = async () => {
    if (selectedRows.size === 0) return;

    const confirmed = window.confirm(
      `Delete ${selectedRows.size} product(s)? This cannot be undone.`
    );
    if (!confirmed) return;

    try {
      const selectedProducts = products.filter((p) => selectedRows.has(p.id));
      await Promise.all(
        selectedProducts.map((p) => deleteProduct(cityId, p.id))
      );

      addAction({
        type: 'delete',
        productId: 0,
        products: selectedProducts,
        timestamp: Date.now(),
      });

      setProducts(products.filter((p) => !selectedRows.has(p.id)));
      setSelectedRows(new Set());
      toast.success(`Deleted ${selectedRows.size} product(s)`);
    } catch (error: any) {
      toast.error(`Delete failed: ${error.message}`);
    }
  };

  const handleBulkEdit = () => {
    if (selectedRows.size === 0) return;

    const field = prompt('Field to edit: sku, name, description, category, price, stock, link, is_active');
    if (!field) return;

    const value = prompt(`New value for ${field}:`);
    if (value === null) return;

    const updatedProducts = products.map((p) => {
      if (selectedRows.has(p.id)) {
        const updated = { ...p, [field]: value, updated_by: currentUser, updated_at: new Date().toISOString() };
        debouncedSave(updated);
        return updated;
      }
      return p;
    });

    addAction({
      type: 'bulk',
      productId: 0,
      timestamp: Date.now(),
    });

    setProducts(updatedProducts);
    toast.success(`Updated ${selectedRows.size} product(s)`);
  };

  const handleImport = async (file: File) => {
    try {
      const imported = await importFromCSV(file);
      const newProducts = imported.map((p, idx) => ({
        ...p,
        id: Date.now() + idx,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        updated_by: currentUser,
      })) as Product[];

      setProducts([...products, ...newProducts]);
      toast.success(`Imported ${newProducts.length} products`);
    } catch (error: any) {
      toast.error(`Import failed: ${error.message}`);
    }
  };

  const handleExport = () => {
    exportToCSV(filteredProducts);
    toast.success('Exported to CSV');
  };

  const handleUndo = () => {
    const action = undo();
    if (!action) return;

    if (action.type === 'edit' && action.field) {
      const field = action.field as keyof Product;
      const updated = products.map((p) =>
        p.id === action.productId
          ? { ...p, [field]: action.oldValue }
          : p
      );
      setProducts(updated);
      toast.success('Undone');
    }
  };

  const handleRedo = () => {
    const action = redo();
    if (!action) return;

    if (action.type === 'edit' && action.field) {
      const field = action.field as keyof Product;
      const updated = products.map((p) =>
        p.id === action.productId
          ? { ...p, [field]: action.newValue }
          : p
      );
      setProducts(updated);
      toast.success('Redone');
    }
  };

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      setSortDirection(
        sortDirection === 'NONE' ? 'ASC' : sortDirection === 'ASC' ? 'DESC' : 'NONE'
      );
    } else {
      setSortColumn(columnKey as keyof Product);
      setSortDirection('ASC');
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
      }
      if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        handleRedo();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canUndo, canRedo]);

  const columns: Column<Product>[] = [
    SelectColumn,
    {
      key: 'id',
      name: 'ID',
      width: 80,
      frozen: true,
      resizable: true,
    },
    {
      key: 'sku',
      name: 'SKU',
      width: 120,
      editable: true,
      resizable: true,
    },
    {
      key: 'name',
      name: 'Name',
      width: 200,
      editable: true,
      resizable: true,
      renderCell: ({ row }) => (
        <div className="relative">
          {row.name}
          {aiValidations[row.id]?.length > 0 && (
            <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[#1A73E8] text-xs">
              AI
            </span>
          )}
        </div>
      ),
    },
    {
      key: 'description',
      name: 'Description',
      width: 250,
      editable: true,
      resizable: true,
    },
    {
      key: 'category',
      name: 'Category',
      width: 150,
      editable: true,
      resizable: true,
    },
    {
      key: 'price',
      name: 'Price',
      width: 100,
      editable: true,
      resizable: true,
      renderCell: ({ row }) => `$${row.price.toFixed(2)}`,
    },
    {
      key: 'stock',
      name: 'Stock',
      width: 100,
      editable: true,
      resizable: true,
    },
    {
      key: 'link',
      name: 'Link',
      width: 200,
      editable: true,
      resizable: true,
    },
    {
      key: 'is_active',
      name: 'Active',
      width: 80,
      editable: true,
      resizable: true,
      renderCell: ({ row }) => (
        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
          row.is_active ? 'bg-[#E6F4EA] text-[#1E8E3E]' : 'bg-[#FCE8E6] text-[#D93025]'
        }`}>
          {row.is_active ? 'Yes' : 'No'}
        </span>
      ),
    },
    {
      key: 'updated_by',
      name: 'Updated By',
      width: 150,
      resizable: true,
    },
    {
      key: 'updated_at',
      name: 'Updated At',
      width: 180,
      resizable: true,
      renderCell: ({ row }) => new Date(row.updated_at).toLocaleString(),
    },
    {
      key: 'actions',
      name: 'Actions',
      width: 100,
      renderCell: ({ row }) => (
        <button
          onClick={() => {
            setSelectedProductForAudit(row.id);
            setShowAuditPanel(true);
          }}
          className="text-[#1A73E8] hover:text-[#1557B0] text-sm font-medium"
        >
          History
        </button>
      ),
    },
  ];

  return (
    <div className="h-screen flex flex-col">
      <Toaster position="top-right" />
      
      <Toolbar
        selectedCount={selectedRows.size}
        aiEnabled={aiEnabled}
        onToggleAI={() => setAiEnabled(!aiEnabled)}
        onAdd={handleAddRow}
        onDelete={handleDelete}
        onBulkEdit={handleBulkEdit}
        onImport={handleImport}
        onExport={handleExport}
        onUndo={handleUndo}
        onRedo={handleRedo}
        canUndo={canUndo}
        canRedo={canRedo}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <div className="flex-1 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500 text-lg">Loading products...</div>
          </div>
        ) : (
          <DataGrid
            columns={columns}
            rows={filteredProducts}
            rowKeyGetter={(row) => row.id}
            onRowsChange={handleRowsChange}
            selectedRows={selectedRows}
            onSelectedRowsChange={setSelectedRows}
            className="rdg-light"
            style={{ height: '100%' }}
            rowHeight={40}
            headerRowHeight={40}
          />
        )}
      </div>

      {showAuditPanel && (
        <AuditPanel
          cityId={cityId}
          productId={selectedProductForAudit}
          onClose={() => {
            setShowAuditPanel(false);
            setSelectedProductForAudit(null);
          }}
        />
      )}
    </div>
  );
}
