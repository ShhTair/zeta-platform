'use client';

import { useParams } from 'next/navigation';
import { useAnalytics, useCity } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MessageSquare, TrendingUp, Package } from 'lucide-react';

export default function AnalyticsPage() {
  const params = useParams();
  const cityId = params.id as string;
  const { hasRole, canAccessCity } = useAuthStore();
  const { data: city } = useCity(cityId);
  const { data: analytics, isLoading } = useAnalytics(cityId);

  if (!hasRole(['SUPER_ADMIN', 'CITY_ADMIN']) || !canAccessCity(cityId)) {
    return (
      <Card>
        <p className="text-center text-red-500">Access denied.</p>
      </Card>
    );
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!analytics) {
    return <Card><p>No analytics data available</p></Card>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-gray-400 mt-1">{city?.name}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-600 rounded-lg">
              <MessageSquare size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-400">Today</p>
              <p className="text-2xl font-bold">{analytics.totalConversationsToday}</p>
              <p className="text-xs text-gray-500">conversations</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-600 rounded-lg">
              <TrendingUp size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-400">This Week</p>
              <p className="text-2xl font-bold">{analytics.totalConversationsWeek}</p>
              <p className="text-xs text-gray-500">conversations</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-600 rounded-lg">
              <MessageSquare size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-400">This Month</p>
              <p className="text-2xl font-bold">{analytics.totalConversationsMonth}</p>
              <p className="text-xs text-gray-500">conversations</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <h2 className="text-xl font-bold mb-4">Average Messages Per Conversation</h2>
        <p className="text-4xl font-bold text-blue-500">
          {analytics.averageMessagesPerConversation.toFixed(1)}
        </p>
        <p className="text-sm text-gray-400 mt-2">messages per conversation</p>
      </Card>

      <Card>
        <h2 className="text-xl font-bold mb-4">Conversations Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analytics.conversationsByDay}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Line type="monotone" dataKey="count" stroke="#3B82F6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <h2 className="text-xl font-bold mb-4">Top Products Inquired</h2>
        {analytics.topProducts.length > 0 ? (
          <div className="space-y-4">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.topProducts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="productName" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Bar dataKey="count" fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>

            <div className="space-y-2">
              {analytics.topProducts.map((product, idx) => (
                <div key={product.productId} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center font-bold">
                      {idx + 1}
                    </div>
                    <div>
                      <p className="font-medium">{product.productName}</p>
                      <p className="text-sm text-gray-400">{product.count} inquiries</p>
                    </div>
                  </div>
                  <Package size={20} className="text-gray-500" />
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-gray-400 text-center py-8">No product inquiries yet</p>
        )}
      </Card>
    </div>
  );
}
