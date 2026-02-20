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
  const baseClasses = 'font-medium transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center';
  
  const variantClasses = {
    primary: 'bg-[#1A73E8] hover:bg-[#1765CC] active:bg-[#1557B0] text-white shadow-sm hover:shadow-md',
    secondary: 'border border-[#DADCE0] bg-white hover:bg-[#F1F3F4] text-[#202124] hover:border-[#DADCE0]',
    text: 'text-[#5F6368] hover:bg-[#F1F3F4] hover:text-[#202124]',
    danger: 'bg-[#D93025] hover:bg-[#C5221F] text-white shadow-sm',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-[13px] rounded-md',
    md: 'px-4 py-2 text-[14px] rounded-lg',
    lg: 'px-6 py-2.5 text-[15px] rounded-lg',
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
