'use client';

import { useRef } from 'react';

interface ToolbarProps {
  selectedCount: number;
  aiEnabled: boolean;
  onToggleAI: () => void;
  onAdd: () => void;
  onDelete: () => void;
  onBulkEdit: () => void;
  onImport: (file: File) => void;
  onExport: () => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export default function Toolbar({
  selectedCount,
  aiEnabled,
  onToggleAI,
  onAdd,
  onDelete,
  onBulkEdit,
  onImport,
  onExport,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  searchQuery,
  onSearchChange,
}: ToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImport(file);
      e.target.value = '';
    }
  };

  return (
    <div className="bg-white border-b border-gray-300 p-4 space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="flex-1 min-w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        {/* AI Toggle */}
        <button
          onClick={onToggleAI}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            aiEnabled
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          🤖 AI {aiEnabled ? 'ON' : 'OFF'}
        </button>

        {/* Undo/Redo */}
        <div className="flex gap-1">
          <button
            onClick={onUndo}
            disabled={!canUndo}
            className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Undo (Ctrl+Z)"
          >
            ↶
          </button>
          <button
            onClick={onRedo}
            disabled={!canRedo}
            className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Redo (Ctrl+Y)"
          >
            ↷
          </button>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {/* Add Row */}
        <button
          onClick={onAdd}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 font-medium"
        >
          + Add Row
        </button>

        {/* Delete */}
        <button
          onClick={onDelete}
          disabled={selectedCount === 0}
          className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          🗑️ Delete {selectedCount > 0 ? `(${selectedCount})` : ''}
        </button>

        {/* Bulk Edit */}
        <button
          onClick={onBulkEdit}
          disabled={selectedCount === 0}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ✏️ Bulk Edit {selectedCount > 0 ? `(${selectedCount})` : ''}
        </button>

        {/* Import */}
        <button
          onClick={handleImportClick}
          className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 font-medium"
        >
          📥 Import CSV
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Export */}
        <button
          onClick={onExport}
          className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 font-medium"
        >
          📤 Export CSV
        </button>
      </div>
    </div>
  );
}
