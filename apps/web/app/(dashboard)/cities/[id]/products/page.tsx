'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useProducts, useCreateProduct, useUpdateProduct, useDeleteProduct, useCity } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { Plus, Edit2, Trash2, Package } from 'lucide-react';
import { Product } from '@/lib/types';

export default function ProductsPage() {
  const params = useParams();
  const cityId = params.id as string;
  const { canAccessCity } = useAuthStore();
  const { data: city } = useCity(cityId);
  const { data: products, isLoading } = useProducts(cityId);
  const createProduct = useCreateProduct();
  const updateProduct = useUpdateProduct();
  const deleteProduct = useDeleteProduct();

  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    isActive: true,
  });

  if (!canAccessCity(cityId)) {
    return (
      <Card>
        <p className="text-center text-red-500">Access denied.</p>
      </Card>
    );
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      price: '',
      isActive: true,
    });
    setIsAdding(false);
    setEditingId(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingId) {
        await updateProduct.mutateAsync({
          cityId,
          id: editingId,
          name: formData.name,
          description: formData.description || undefined,
          price: formData.price ? parseFloat(formData.price) : undefined,
          isActive: formData.isActive,
        });
      } else {
        await createProduct.mutateAsync({
          cityId,
          name: formData.name,
          description: formData.description || undefined,
          price: formData.price ? parseFloat(formData.price) : undefined,
          isActive: formData.isActive,
        });
      }
      resetForm();
    } catch (error: any) {
      alert(error.response?.data?.message || 'Operation failed');
    }
  };

  const handleEdit = (product: Product) => {
    setFormData({
      name: product.name,
      description: product.description || '',
      price: product.price?.toString() || '',
      isActive: product.isActive,
    });
    setEditingId(product.id);
    setIsAdding(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      await deleteProduct.mutateAsync({ cityId, id });
    } catch (error: any) {
      alert(error.response?.data?.message || 'Delete failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Products</h1>
          <p className="text-gray-400 mt-1">{city?.name}</p>
        </div>
        {!isAdding && (
          <Button onClick={() => setIsAdding(true)}>
            <Plus size={16} className="mr-2" />
            Add Product
          </Button>
        )}
      </div>

      {isAdding && (
        <Card>
          <h2 className="text-xl font-bold mb-4">
            {editingId ? 'Edit Product' : 'New Product'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Product Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Product name"
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Product description (optional)"
              />
            </div>

            <Input
              label="Price"
              type="number"
              step="0.01"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              placeholder="0.00"
            />

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="isActive"
                checked={formData.isActive}
                onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
              />
              <label htmlFor="isActive" className="text-sm font-medium">
                Product is active
              </label>
            </div>

            <div className="flex gap-3">
              <Button type="submit" disabled={createProduct.isPending || updateProduct.isPending}>
                {editingId ? 'Update' : 'Create'} Product
              </Button>
              <Button type="button" variant="secondary" onClick={resetForm}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      {products && products.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <Card key={product.id}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-600 rounded-lg">
                    <Package size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold">{product.name}</h3>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  product.isActive 
                    ? 'bg-green-600 text-white' 
                    : 'bg-gray-600 text-white'
                }`}>
                  {product.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>

              {product.description && (
                <p className="text-sm text-gray-400 mb-3">{product.description}</p>
              )}

              {product.price && (
                <p className="text-lg font-bold text-blue-400 mb-3">
                  ${product.price.toFixed(2)}
                </p>
              )}

              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  className="flex-1"
                  onClick={() => handleEdit(product)}
                >
                  <Edit2 size={14} className="mr-1" />
                  Edit
                </Button>
                <Button
                  size="sm"
                  variant="danger"
                  onClick={() => handleDelete(product.id)}
                >
                  <Trash2 size={14} />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-8">
            <Package size={48} className="mx-auto text-gray-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Products Yet</h3>
            <p className="text-gray-400 mb-4">Add your first product to get started.</p>
            <Button onClick={() => setIsAdding(true)}>
              <Plus size={16} className="mr-2" />
              Add Product
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
