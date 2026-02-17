'use client';

import { useState, useEffect } from 'react';
import { AuditLog } from './types';
import { fetchAuditLogs } from './api';
import { formatDate } from './utils';

interface AuditPanelProps {
  cityId: string;
  productId: number | null;
  onClose: () => void;
}

export default function AuditPanel({ cityId, productId, onClose }: AuditPanelProps) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (productId) {
      setLoading(true);
      setError(null);
      fetchAuditLogs(cityId, productId)
        .then(setLogs)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [cityId, productId]);

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white border-l border-gray-300 shadow-xl z-50 flex flex-col">
      <div className="flex justify-between items-center p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold">Audit History</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
        >
          ×
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {loading && (
          <div className="text-center text-gray-500 py-8">Loading audit logs...</div>
        )}

        {error && (
          <div className="text-center text-red-500 py-8">
            <p>Error: {error}</p>
          </div>
        )}

        {!loading && !error && logs.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            No audit logs found for this product.
          </div>
        )}

        {!loading && !error && logs.length > 0 && (
          <div className="space-y-4">
            {logs.map((log) => (
              <div
                key={log.id}
                className="bg-gray-50 rounded-lg p-3 border border-gray-200"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-sm text-gray-700 capitalize">
                    {log.field_name.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDate(log.created_at)}
                  </span>
                </div>
                <div className="text-xs text-gray-600 mb-2">
                  by <span className="font-medium">{log.user_name}</span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-start gap-2">
                    <span className="text-red-500 font-mono text-xs">−</span>
                    <span className="text-gray-600 text-xs break-all line-through">
                      {log.old_value || '(empty)'}
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-green-500 font-mono text-xs">+</span>
                    <span className="text-gray-800 text-xs break-all font-medium">
                      {log.new_value || '(empty)'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
