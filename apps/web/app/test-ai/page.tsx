'use client';

import { useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';

export default function TestAIPage() {
  const [product, setProduct] = useState({
    name: 'Mous',
    description: 'Small',
    category: 'Food',
    price: 0.5,
    stock: 0,
    sku: 'TEST-001',
  });

  const [validations, setValidations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const testValidation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/cities/city-123/products/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(product),
      });

      if (!response.ok) throw new Error('API request failed');

      const data = await response.json();
      setValidations(data);
      toast.success(`Received ${data.length} validation suggestions`);
    } catch (error: any) {
      toast.error(`Error: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <Toaster position="top-right" />
      
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">🤖 AI Validation Test</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Test Product</h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Name
              </label>
              <input
                type="text"
                value={product.name}
                onChange={(e) => setProduct({ ...product, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="e.g., Wireless Mouse"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                SKU
              </label>
              <input
                type="text"
                value={product.sku}
                onChange={(e) => setProduct({ ...product, sku: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={product.description}
                onChange={(e) => setProduct({ ...product, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                rows={3}
                placeholder="Detailed product description..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <input
                type="text"
                value={product.category}
                onChange={(e) => setProduct({ ...product, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="e.g., Electronics"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price ($)
              </label>
              <input
                type="number"
                step="0.01"
                value={product.price}
                onChange={(e) => setProduct({ ...product, price: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stock
              </label>
              <input
                type="number"
                value={product.stock}
                onChange={(e) => setProduct({ ...product, stock: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            onClick={testValidation}
            disabled={loading}
            className="mt-6 w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
          >
            {loading ? '🔄 Validating with OpenAI...' : '🤖 Validate Product'}
          </button>
        </div>

        {validations.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">
              ✨ AI Validation Results ({validations.length})
            </h2>

            <div className="space-y-4">
              {validations.map((validation, idx) => (
                <div
                  key={idx}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">
                        {validation.issue ? '⚠️' : '💡'}
                      </span>
                      <span className="font-semibold text-gray-800 capitalize">
                        {validation.field}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {Math.round(validation.confidence * 100)}% confidence
                    </span>
                  </div>

                  {validation.issue && (
                    <p className="text-red-600 text-sm mb-2">
                      <strong>Issue:</strong> {validation.issue}
                    </p>
                  )}

                  <p className="text-gray-700 text-sm">
                    <strong>Suggestion:</strong> {validation.suggestion}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Как это работает:</h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>OpenAI GPT-4o-mini анализирует продукт</li>
            <li>Проверяет название, описание, категорию, цену, остаток</li>
            <li>Находит ошибки и предлагает улучшения</li>
            <li>Возвращает уровень уверенности (confidence)</li>
            <li>Если API недоступен, используется fallback mock логика</li>
          </ul>
        </div>

        <div className="mt-6 text-center">
          <a
            href="/products"
            className="text-blue-500 hover:text-blue-700 font-medium"
          >
            ← Вернуться к таблице продуктов
          </a>
        </div>
      </div>
    </div>
  );
}
