import React from 'react';
import { Theme } from '../../types/types';
import { config } from '../../utils/config';

// Import logo assets
import lightLogo from '../../assets/images/mlc-logo.png';
import darkLogo from '../../assets/images/dark-robot-logo.png';

interface LogoProps {
  theme: Theme;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
}

const Logo: React.FC<LogoProps> = ({ 
  theme, 
  className = '', 
  size = 'md', 
  showText = false 
}) => {
  // Size mappings
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl',
    xl: 'text-2xl'
  };

  // Choose logo based on theme
  const logoSrc = theme === Theme.DARK ? darkLogo : lightLogo;
  const logoAlt = `${config.appName} Logo`;

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <img 
        src={logoSrc}
        alt={logoAlt}
        className={`${sizeClasses[size]} object-contain transition-opacity duration-200 hover:opacity-80`}
        loading="lazy"
      />
      {showText && (
        <div className="flex flex-col">
          <span className={`font-semibold text-light-text dark:text-dark-text ${textSizeClasses[size]}`}>
            Cloud ERA
          </span>
          {size === 'lg' || size === 'xl' ? (
            <span className="text-xs text-light-text-secondary dark:text-dark-text-secondary">
              AI Cloud Services Assistant
            </span>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default Logo;