'use client';

import { AIValidation } from './types';

interface AIValidationBadgeProps {
  validations: AIValidation[];
  onDismiss?: () => void;
}

export default function AIValidationBadge({ validations, onDismiss }: AIValidationBadgeProps) {
  if (validations.length === 0) return null;

  return (
    <div className="absolute top-0 right-0 z-10 bg-white border border-gray-300 rounded-lg shadow-lg p-3 min-w-64 max-w-sm">
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          <span className="text-blue-500 text-lg">🤖</span>
          <h4 className="font-semibold text-sm">AI Suggestions</h4>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-gray-600 text-lg leading-none"
          >
            ×
          </button>
        )}
      </div>
      <div className="space-y-2">
        {validations.map((validation, idx) => (
          <div key={idx} className="text-sm">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-gray-700 capitalize">{validation.field}:</span>
              <span className="text-xs text-gray-500">
                {Math.round(validation.confidence * 100)}% confidence
              </span>
            </div>
            {validation.issue && (
              <p className="text-red-600 text-xs mb-1">⚠️ {validation.issue}</p>
            )}
            <p className="text-gray-600 text-xs italic">💡 {validation.suggestion}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
