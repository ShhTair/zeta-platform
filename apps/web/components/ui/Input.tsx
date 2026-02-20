import { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export default function Input({ label, error, className = '', ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-[14px] font-medium text-[#202124] mb-2">
          {label}
        </label>
      )}
      <input
        className={`w-full bg-white border border-[#DADCE0] rounded-lg px-4 py-2.5 text-[#202124] text-[14px] placeholder-[#5F6368] focus:outline-none focus:border-[#1A73E8] focus:ring-1 focus:ring-[#1A73E8] transition-all ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1.5 text-[13px] text-[#D93025]">{error}</p>
      )}
    </div>
  );
}
