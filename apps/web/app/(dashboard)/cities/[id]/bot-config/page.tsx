'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useBotConfig, useUpdateBotConfig, useCity } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function BotConfigPage() {
  const params = useParams();
  const cityId = params.id as string;
  const { hasRole, canAccessCity } = useAuthStore();
  const { data: city } = useCity(cityId);
  const { data: config, isLoading } = useBotConfig(cityId);
  const updateConfig = useUpdateBotConfig();

  const [formData, setFormData] = useState({
    systemPrompt: '',
    managerTelegram: '',
    escalationAction: 'LINK' as 'LINK' | 'NOTIFY_MANAGER' | 'BITRIX',
  });

  useEffect(() => {
    if (config) {
      setFormData({
        systemPrompt: config.systemPrompt,
        managerTelegram: config.managerTelegram,
        escalationAction: config.escalationAction,
      });
    }
  }, [config]);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await updateConfig.mutateAsync({
        cityId,
        ...formData,
      });
      alert('Bot configuration updated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.message || 'Failed to update configuration');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Bot Configuration</h1>
        <p className="text-gray-400 mt-1">{city?.name}</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              System Prompt
            </label>
            <textarea
              value={formData.systemPrompt}
              onChange={(e) => setFormData({ ...formData, systemPrompt: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              rows={15}
              placeholder="Enter the system prompt for the bot..."
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              This prompt defines the bot's behavior and personality.
            </p>
          </div>

          <Input
            label="Manager Telegram Handle"
            value={formData.managerTelegram}
            onChange={(e) => setFormData({ ...formData, managerTelegram: e.target.value })}
            placeholder="@username"
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Escalation Action
            </label>
            <select
              value={formData.escalationAction}
              onChange={(e) => setFormData({ 
                ...formData, 
                escalationAction: e.target.value as 'LINK' | 'NOTIFY_MANAGER' | 'BITRIX'
              })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="LINK">Send Link to Manager</option>
              <option value="NOTIFY_MANAGER">Notify Manager Directly</option>
              <option value="BITRIX">Create Bitrix Task</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              What happens when the bot escalates a conversation to a human.
            </p>
          </div>

          <Button type="submit" disabled={updateConfig.isPending}>
            {updateConfig.isPending ? 'Saving...' : 'Save Configuration'}
          </Button>
        </form>
      </Card>

      {config && (
        <Card>
          <h2 className="text-lg font-bold mb-2">Configuration Info</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Last Updated:</span>
              <span>{new Date(config.updatedAt).toLocaleString()}</span>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
