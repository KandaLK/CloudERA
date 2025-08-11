import React, { useState, useMemo } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { githubLight } from '@uiw/codemirror-theme-github';
import { vscodeDark } from '@uiw/codemirror-theme-vscode';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { php } from '@codemirror/lang-php';
import { rust } from '@codemirror/lang-rust';
import { sql } from '@codemirror/lang-sql';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { json } from '@codemirror/lang-json';
import { xml } from '@codemirror/lang-xml';
import { yaml } from '@codemirror/lang-yaml';
import { EditorView } from '@codemirror/view';
import { CopyIcon } from '../icons/Icon';

interface CodeBlockProps {
  code: string;
  language: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ code, language }) => {
  const [copied, setCopied] = useState(false);
  const [isDark, setIsDark] = useState(() => {
    // Check if dark mode is active
    return document.documentElement.classList.contains('dark');
  });

  // Listen for theme changes
  React.useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    });

    return () => observer.disconnect();
  }, []);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  // Language extension mapping
  const getLanguageExtension = (lang: string) => {
    const languageMap: { [key: string]: any } = {
      'javascript': javascript({ jsx: true }),
      'js': javascript({ jsx: true }),
      'jsx': javascript({ jsx: true }),
      'typescript': javascript({ jsx: true, typescript: true }),
      'ts': javascript({ jsx: true, typescript: true }),
      'tsx': javascript({ jsx: true, typescript: true }),
      'python': python(),
      'py': python(),
      'java': java(),
      'cpp': cpp(),
      'c++': cpp(),
      'c': cpp(),
      'csharp': cpp(), // Using cpp as closest alternative
      'php': php(),
      'rust': rust(),
      'rs': rust(),
      'sql': sql(),
      'html': html(),
      'htm': html(),
      'css': css(),
      'scss': css(),
      'json': json(),
      'xml': xml(),
      'yaml': yaml(),
      'yml': yaml(),
      'bash': javascript(), // Using javascript as fallback
      'shell': javascript(),
      'dockerfile': javascript(),
    };
    
    return languageMap[lang.toLowerCase()];
  };

  // Language display name mapping
  const getLanguageDisplay = (lang: string) => {
    const languageMap: { [key: string]: string } = {
      'javascript': 'JavaScript',
      'js': 'JavaScript',
      'jsx': 'JSX',
      'typescript': 'TypeScript',
      'ts': 'TypeScript',
      'tsx': 'TSX',
      'python': 'Python',
      'py': 'Python',
      'java': 'Java',
      'cpp': 'C++',
      'c++': 'C++',
      'c': 'C',
      'csharp': 'C#',
      'php': 'PHP',
      'rust': 'Rust',
      'rs': 'Rust',
      'sql': 'SQL',
      'html': 'HTML',
      'htm': 'HTML',
      'css': 'CSS',
      'scss': 'SCSS',
      'json': 'JSON',
      'xml': 'XML',
      'yaml': 'YAML',
      'yml': 'YAML',
      'bash': 'Bash',
      'shell': 'Shell',
      'dockerfile': 'Dockerfile',
    };
    
    return languageMap[lang.toLowerCase()] || lang.toUpperCase();
  };

  // Get language extension for CodeMirror
  const languageExtension = useMemo(() => {
    return getLanguageExtension(language);
  }, [language]);

  // Configure CodeMirror extensions
  const extensions = useMemo(() => {
    const exts = [
      EditorView.theme({
        '&': {
          fontSize: '0.875rem',
        },
        '.cm-content': {
          padding: '1rem',
        },
        '.cm-focused': {
          outline: 'none',
        },
        '.cm-editor': {
          borderRadius: '0 0 0.5rem 0.5rem',
        },
        '.cm-scroller': {
          lineHeight: '1.5',
        },
      }),
      EditorView.lineWrapping,
    ];
    
    if (languageExtension) {
      exts.push(languageExtension);
    }
    
    return exts;
  }, [languageExtension]);

  return (
    <div className="relative group mb-4">
      {/* Header with language and copy button */}
      <div className="flex items-center justify-between px-4 py-2 bg-light-secondary dark:bg-dark-secondary border border-light-border dark:border-dark-border rounded-t-lg">
        <span className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">
          {language ? getLanguageDisplay(language) : 'Code'}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center space-x-2 px-2 py-1 text-xs bg-light-accent dark:bg-dark-accent hover:bg-light-border dark:hover:bg-dark-border text-light-text dark:text-dark-text rounded transition-all duration-200 opacity-0 group-hover:opacity-100"
          title="Copy code"
        >
          <CopyIcon className="w-3 h-3" />
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>

      {/* Code content with CodeMirror */}
      <div className="relative overflow-hidden border border-light-border dark:border-dark-border border-t-0 rounded-b-lg">
        <CodeMirror
          value={code}
          editable={false}
          theme={isDark ? vscodeDark : githubLight}
          extensions={extensions}
          basicSetup={{
            lineNumbers: code.split('\n').length > 1,
            highlightActiveLine: false,
            highlightActiveLineGutter: false,
            foldGutter: false,
            dropCursor: false,
            allowMultipleSelections: false,
            indentOnInput: false,
            bracketMatching: true,
            closeBrackets: false,
            autocompletion: false,
            highlightSelectionMatches: false,
            searchKeymap: false,
          }}
        />
      </div>
    </div>
  );
};

export default CodeBlock;