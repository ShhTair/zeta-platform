import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'text' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export default function Button({ 
  variant = 'primary', 
  size = 'md',
  className = '',
  children,
  ...props 
}: ButtonProps) {
  const baseClasses = 'font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2';
  
  const variantClasses = {
    primary: 'bg-gdrive-blue hover:bg-gdrive-blue-hover active:bg-gdrive-blue-active text-white shadow-google-sm hover:shadow-google-md',
    secondary: 'border border-gdrive-border bg-gdrive-white hover:bg-gdrive-gray-hover text-gdrive-text hover:shadow-google-sm',
    text: 'text-gdrive-secondary hover:bg-gdrive-gray-hover hover:text-gdrive-text',
    danger: 'bg-gdrive-danger hover:bg-[#C5221F] active:bg-[#B31412] text-white shadow-google-sm',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs rounded-google-sm',
    md: 'px-4 py-2 text-sm rounded-google-sm',
    lg: 'px-6 py-2.5 text-base rounded-google-sm',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
