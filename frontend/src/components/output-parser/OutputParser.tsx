import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Components } from 'react-markdown';
import CodeBlock from './CodeBlock';
import TableRenderer from './TableRenderer';

interface OutputParserProps {
  content: string;
  className?: string;
}

const OutputParser: React.FC<OutputParserProps> = ({ content, className = '' }) => {
  // Custom components for react-markdown
  const components: Components = {
    // Code blocks with syntax highlighting
    code: ({ node, className: codeClassName, children, ...props }: any) => {
      const inline = !codeClassName;
      const match = /language-(\w+)/.exec(codeClassName || '');
      const language = match ? match[1] : '';
      
      return !inline ? (
        <CodeBlock 
          code={String(children).replace(/\n$/, '')} 
          language={language}
        />
      ) : (
        <code 
          className="px-2 py-1 bg-light-accent dark:bg-dark-accent rounded text-sm font-mono text-light-text dark:text-dark-text border border-light-border dark:border-dark-border"
          {...props}
        >
          {children}
        </code>
      );
    },
    
    // Tables with enhanced styling
    table: ({ children }) => (
      <TableRenderer>
        <table className="w-full border-collapse border border-light-border dark:border-dark-border rounded-lg overflow-hidden">
          {children}
        </table>
      </TableRenderer>
    ),
    
    // Table headers
    thead: ({ children }) => (
      <thead className="bg-light-secondary dark:bg-dark-secondary">
        {children}
      </thead>
    ),
    
    // Table header cells
    th: ({ children }) => (
      <th className="border border-light-border dark:border-dark-border px-4 py-2 text-left font-semibold text-light-text dark:text-dark-text">
        {children}
      </th>
    ),
    
    // Table body cells
    td: ({ children }) => (
      <td className="border border-light-border dark:border-dark-border px-4 py-2 text-light-text dark:text-dark-text">
        {children}
      </td>
    ),
    
    // Links with security and styling
    a: ({ href, children }) => (
      <a 
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline transition-colors duration-200"
      >
        {children}
      </a>
    ),
    
    // Headers with proper styling
    h1: ({ children }) => (
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-4 mt-6 first:mt-0 border-b border-light-border dark:border-dark-border pb-2">
        {children}
      </h1>
    ),
    
    h2: ({ children }) => (
      <h2 className="text-xl font-bold text-light-text dark:text-dark-text mb-3 mt-5 first:mt-0">
        {children}
      </h2>
    ),
    
    h3: ({ children }) => (
      <h3 className="text-lg font-semibold text-light-text dark:text-dark-text mb-2 mt-4 first:mt-0">
        {children}
      </h3>
    ),
    
    h4: ({ children }) => (
      <h4 className="text-base font-semibold text-light-text dark:text-dark-text mb-2 mt-3 first:mt-0">
        {children}
      </h4>
    ),
    
    h5: ({ children }) => (
      <h5 className="text-sm font-semibold text-light-text dark:text-dark-text mb-1 mt-2 first:mt-0">
        {children}
      </h5>
    ),
    
    h6: ({ children }) => (
      <h6 className="text-sm font-medium text-light-text dark:text-dark-text mb-1 mt-2 first:mt-0">
        {children}
      </h6>
    ),
    
    // Lists with proper spacing
    ul: ({ children }) => (
      <ul className="list-disc list-inside space-y-1 mb-4 text-light-text dark:text-dark-text ml-4">
        {children}
      </ul>
    ),
    
    ol: ({ children }) => (
      <ol className="list-decimal list-inside space-y-1 mb-4 text-light-text dark:text-dark-text ml-4">
        {children}
      </ol>
    ),
    
    li: ({ children }) => (
      <li className="text-light-text dark:text-dark-text leading-relaxed">
        {children}
      </li>
    ),
    
    // Paragraphs with proper spacing
    p: ({ children }) => (
      <p className="text-light-text dark:text-dark-text mb-4 leading-relaxed last:mb-0">
        {children}
      </p>
    ),
    
    // Blockquotes with styling
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-400 dark:border-blue-500 pl-4 py-2 mb-4 bg-light-accent dark:bg-dark-accent rounded-r text-light-text dark:text-dark-text italic">
        {children}
      </blockquote>
    ),
    
    // Horizontal rules
    hr: () => (
      <hr className="border-t border-light-border dark:border-dark-border my-6" />
    ),
    
    // Strong/Bold text
    strong: ({ children }) => (
      <strong className="font-bold text-light-text dark:text-dark-text">
        {children}
      </strong>
    ),
    
    // Emphasis/Italic text
    em: ({ children }) => (
      <em className="italic text-light-text dark:text-dark-text">
        {children}
      </em>
    ),
  };

  return (
    <div className={`output-parser prose max-w-none ${className}`}>
      <ReactMarkdown
        components={components}
        remarkPlugins={[remarkGfm]}
        skipHtml={true}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default OutputParser;