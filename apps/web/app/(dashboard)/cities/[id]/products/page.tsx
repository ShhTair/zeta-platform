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
        <p className="text-center text-[#D93025] text-[14px]">Access denied.</p>
      </Card>
    );
  }

  if (isLoading) {
    return <div className="text-[#5F6368] text-[14px]">Loading...</div>;
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
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-[28px] font-medium text-[#202124]">Products</h1>
          <p className="text-[#5F6368] mt-1 text-[14px]">{city?.name}</p>
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
          <h2 className="text-[18px] font-medium text-[#202124] mb-6">
            {editingId ? 'Edit Product' : 'New Product'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Product Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Product name"
              required
            />

            <div>
              <label className="block text-[14px] font-medium text-[#202124] mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full bg-white border border-[#DADCE0] rounded-lg px-4 py-2.5 text-[#202124] placeholder-[#5F6368] focus:outline-none focus:border-[#1A73E8] focus:ring-1 focus:ring-[#1A73E8] text-[14px]"
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
                className="w-4 h-4 text-[#1A73E8] bg-white border-[#DADCE0] rounded focus:ring-[#1A73E8]"
              />
              <label htmlFor="isActive" className="text-[14px] font-medium text-[#202124]">
                Product is active
              </label>
            </div>

            <div className="flex gap-3 pt-2">
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
            <Card key={product.id} hover>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#E8F0FE] rounded-lg">
                    <Package size={20} className="text-[#1A73E8]" />
                  </div>
                  <div>
                    <h3 className="font-medium text-[#202124] text-[15px]">{product.name}</h3>
                  </div>
                </div>
                <span className={`text-[12px] px-2.5 py-1 rounded-full font-medium ${
                  product.isActive 
                    ? 'bg-[#E6F4EA] text-[#1E8E3E]' 
                    : 'bg-[#F1F3F4] text-[#5F6368]'
                }`}>
                  {product.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>

              {product.description && (
                <p className="text-[13px] text-[#5F6368] mb-3 line-clamp-2">{product.description}</p>
              )}

              {product.price && (
                <p className="text-[20px] font-medium text-[#1A73E8] mb-4">
                  ${product.price.toFixed(2)}
                </p>
              )}

              <div className="flex gap-2 pt-2 border-t border-[#F1F3F4]">
                <Button
                  size="sm"
                  variant="secondary"
                  className="flex-1"
                  onClick={() => handleEdit(product)}
                >
                  <Edit2 size={14} className="mr-1.5" />
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
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-[#F1F3F4] rounded-full flex items-center justify-center mx-auto mb-4">
              <Package size={32} className="text-[#5F6368]" />
            </div>
            <h3 className="text-[18px] font-medium text-[#202124] mb-2">No Products Yet</h3>
            <p className="text-[#5F6368] text-[14px] mb-6">Add your first product to get started.</p>
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
