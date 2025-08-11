import React from 'react';

interface TableRendererProps {
  children: React.ReactNode;
}

const TableRenderer: React.FC<TableRendererProps> = ({ children }) => {
  return (
    <div className="table-container mb-4 overflow-x-auto bg-light-main dark:bg-dark-main rounded-lg border border-light-border dark:border-dark-border">
      <div className="min-w-full">
        {children}
      </div>
    </div>
  );
};

export default TableRenderer;