import { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export default function Input({ label, error, className = '', ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gdrive-text mb-2">
          {label}
        </label>
      )}
      <input
        className={`
          w-full bg-gdrive-white border border-gdrive-border 
          rounded-google-sm px-4 py-2.5 
          text-sm text-gdrive-text 
          placeholder:text-gdrive-secondary
          hover:border-gdrive-secondary
          focus:outline-none focus:border-gdrive-blue focus:ring-2 focus:ring-gdrive-hover 
          transition-all duration-200
          ${error ? 'border-gdrive-danger focus:border-gdrive-danger focus:ring-gdrive-danger-bg' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="mt-1.5 text-xs text-gdrive-danger flex items-center gap-1">
          <span>⚠</span>
          {error}
        </p>
      )}
    </div>
  );
}
