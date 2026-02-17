'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuditLogs, useCity } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import { FileText, User, Clock } from 'lucide-react';

export default function AuditLogsPage() {
  const params = useParams();
  const cityId = params.id as string;
  const { hasRole, canAccessCity } = useAuthStore();
  const { data: city } = useCity(cityId);
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAuditLogs(cityId, page, 50);

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

  const logs = data?.logs || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / 50);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit Logs</h1>
        <p className="text-gray-400 mt-1">{city?.name}</p>
      </div>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileText size={20} className="text-gray-400" />
            <span className="text-sm text-gray-400">{total} total logs</span>
          </div>
          {totalPages > 1 && (
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 bg-gray-800 rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-3 py-1">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 bg-gray-800 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>

        {logs.length > 0 ? (
          <div className="space-y-3">
            {logs.map((log) => (
              <div key={log.id} className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-600 rounded-lg">
                      <User size={16} />
                    </div>
                    <div>
                      <p className="font-medium">{log.userName}</p>
                      <p className="text-sm text-gray-400">{log.action}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <Clock size={14} />
                    <span>{new Date(log.timestamp).toLocaleString()}</span>
                  </div>
                </div>

                <div className="mt-2 text-sm text-gray-400">
                  <p>
                    <span className="text-gray-500">Entity:</span> {log.entityType} ({log.entityId})
                  </p>
                  {log.changes && (
                    <details className="mt-2">
                      <summary className="cursor-pointer hover:text-white">
                        View changes
                      </summary>
                      <pre className="mt-2 p-2 bg-black rounded text-xs overflow-x-auto">
                        {JSON.stringify(log.changes, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <FileText size={48} className="mx-auto text-gray-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Audit Logs</h3>
            <p className="text-gray-400">No activity has been recorded yet.</p>
          </div>
        )}
      </Card>
    </div>
  );
}
