import { ReactNode } from 'react';

interface TableProps {
  children: ReactNode;
  className?: string;
}

interface TableHeaderProps {
  children: ReactNode;
  className?: string;
}

interface TableBodyProps {
  children: ReactNode;
  className?: string;
}

interface TableRowProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  selected?: boolean;
}

interface TableHeadProps {
  children: ReactNode;
  className?: string;
  sortable?: boolean;
  onClick?: () => void;
}

interface TableCellProps {
  children: ReactNode;
  className?: string;
}

// Main Table Container
export function Table({ children, className = '' }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={`w-full ${className}`}>
        {children}
      </table>
    </div>
  );
}

// Table Header
export function TableHeader({ children, className = '' }: TableHeaderProps) {
  return (
    <thead className={`border-b border-gdrive-border ${className}`}>
      {children}
    </thead>
  );
}

// Table Body
export function TableBody({ children, className = '' }: TableBodyProps) {
  return (
    <tbody className={className}>
      {children}
    </tbody>
  );
}

// Table Row
export function TableRow({ children, className = '', onClick, selected = false }: TableRowProps) {
  return (
    <tr 
      className={`
        border-b border-gdrive-border last:border-0
        transition-colors duration-150
        ${onClick ? 'cursor-pointer' : ''}
        ${selected ? 'bg-gdrive-hover' : 'hover:bg-gdrive-gray-hover'}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </tr>
  );
}

// Table Head Cell
export function TableHead({ children, className = '', sortable = false, onClick }: TableHeadProps) {
  return (
    <th 
      className={`
        text-left px-4 py-3
        text-xs font-medium text-gdrive-secondary uppercase tracking-wider
        ${sortable ? 'cursor-pointer hover:text-gdrive-text select-none' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </th>
  );
}

// Table Cell
export function TableCell({ children, className = '' }: TableCellProps) {
  return (
    <td className={`px-4 py-3 text-sm text-gdrive-text ${className}`}>
      {children}
    </td>
  );
}

// Export as default with subcomponents
const TableComponent = Object.assign(Table, {
  Header: TableHeader,
  Body: TableBody,
  Row: TableRow,
  Head: TableHead,
  Cell: TableCell,
});

export default TableComponent;
