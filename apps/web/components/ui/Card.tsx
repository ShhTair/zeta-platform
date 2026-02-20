interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export default function Card({ children, className = '', hover = false }: CardProps) {
  return (
    <div 
      className={`
        bg-gdrive-white 
        border border-gdrive-border 
        rounded-google 
        p-6 
        shadow-google-sm 
        ${hover ? 'hover:shadow-google-md transition-shadow duration-200 cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
