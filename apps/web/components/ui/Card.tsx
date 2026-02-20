interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export default function Card({ children, className = '', hover = false }: CardProps) {
  return (
    <div className={`
      bg-white 
      border border-[#DADCE0] 
      rounded-lg 
      p-6 
      shadow-google-sm 
      ${hover ? 'hover:shadow-google-md transition-shadow duration-150' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
}
