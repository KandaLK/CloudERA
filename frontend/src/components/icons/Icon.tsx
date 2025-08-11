import React from 'react';

interface IconProps {
  className?: string;
  strokeWidth?: number;
}

const IconWrapper: React.FC<{ children: React.ReactNode, className?: string, viewBox?: string }> = ({ children, className = "w-6 h-6", viewBox="0 0 24 24" }) => (
    <svg className={className} viewBox={viewBox} fill="none" xmlns="http://www.w3.org/2000/svg">
        {children}
    </svg>
);

export const CloudEraIcon: React.FC<IconProps> = ({ className }) => (
    <IconWrapper className={className} viewBox="0 0 24 24">
        <path d="M18 17.99c1.93 0 3.5-1.57 3.5-3.5s-1.57-3.5-3.5-3.5c0-.17.01-1.15 0-1.5 0-3.04-2.46-5.5-5.5-5.5S7 6.45 7 9.49c-.16.02-1.25.1-1.5.1C3.57 9.59 2 11.16 2 13.09s1.57 3.5 3.5 3.5" fill="rgba(255, 255, 255, 0.1)" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M12 13v6m-2-4l2-2 2 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="12" cy="11" r="1" fill="currentColor" />
        <path d="M10 12a2 2 0 104 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </IconWrapper>
);

export const LogoIcon: React.FC<IconProps & { theme?: 'light' | 'dark' }> = ({ className = "w-8 h-8", theme = 'light' }) => (
    <img 
        src={theme === 'dark' ? "/assets/dark-robot-logo.png" : "/assets/cloud-era-logo.png"} 
        alt="Cloud ERA Logo" 
        className={`${className} object-contain`}
    />
);

export const WelcomeAssistantIcon: React.FC<IconProps> = ({ className = "w-20 h-20" }) => (
    <div className={`flex items-center justify-center rounded-full bg-light-accent dark:bg-dark-accent ${className}`}>
        <div className="dark:hidden">
            <LogoIcon className="w-12 h-12" theme="light" />
        </div>
        <div className="hidden dark:block">
            <LogoIcon className="w-12 h-12" theme="dark" />
        </div>
    </div>
);

export const NewChatIcon: React.FC<IconProps> = ({ className }) => (
    <IconWrapper className={className}>
        <path d="M12 6V18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M6 12H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const SettingsIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <IconWrapper className={className} viewBox="0 0 24 24">
      <path d="M14 21H10L9.44904 18.5206C8.7879 18.2618 8.17573 17.9053 7.63028 17.4689L5.20573 18.232L3.20573 14.7679L5.07828 13.0503C5.02673 12.7077 5 12.357 5 12C5 11.643 5.02673 11.2923 5.07828 10.9496L3.20573 9.23204L5.20574 5.76794L7.6303 6.53106C8.17575 6.09467 8.78791 5.73819 9.44904 5.47935L10 3H14L14.551 5.47935C15.2121 5.73819 15.8242 6.09466 16.3697 6.53104L18.7942 5.76794L20.7942 9.23204L18.9217 10.9496C18.9733 11.2922 19 11.643 19 12C19 12.357 18.9733 12.7078 18.9217 13.0504L20.7942 14.7679L18.7942 18.232L16.3697 17.4689C15.8243 17.9053 15.2121 18.2618 14.551 18.5206L14 21Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"/>
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
    </IconWrapper>
);

export const ThemeToggleIcon: React.FC<IconProps & { theme?: 'light' | 'dark' }> = ({ className = "w-6 h-6", theme = 'light' }) => {
    // In light mode, show sun. In dark mode, show moon
    return theme === 'light' ? (
        <SunIcon className={className} />
    ) : (
        <MoonIconDynamic className={className} />
    );
};

export const LogoutIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
  </svg>
);

export const EditIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className}>
      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const DeleteIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className}>
       <path d="M3 6h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
       <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const CopyIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className}>
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const RetryIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
  <IconWrapper className={className}>
    <path d="M20 11A8.1 8.1 0 0 0 4.5 9M4 5v4h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </IconWrapper>
);

export const ThumbsUpIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className} viewBox="0 0 24 24">
        <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const ThumbsDownIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className} viewBox="0 0 24 24">
       <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const SendIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <IconWrapper className={className} viewBox="0 0 24 24">
       <path d="M2.69 12h18.62" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
       <path d="M16.5 7.25l4.81 4.75-4.81 4.75" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const CloseIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
);

export const MenuIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
);

export const SunIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
);

export const MoonIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="currentColor" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
);

export const MoonIconDynamic: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <IconWrapper className={className} viewBox="0 0 16 16">
        <path d="M6.67,0C2.98,0 0,2.98 0,6.67C0,10.35 2.98,13.33 6.67,13.33C10.35,13.33 13.33,10.35 13.33,6.67C13.33,6.2 13.29,5.75 13.2,5.32C12.72,7.14 11.06,8.48 9.09,8.48C6.75,8.48 4.85,6.59 4.85,4.24C4.85,2.27 6.19,0.61 8.02,0.14C7.58,0.05 7.13,0 6.67,0Z" stroke="currentColor" strokeWidth="1.33" strokeLinecap="round" strokeLinejoin="round" fill="none" transform="translate(1.33 1.33)"/>
    </IconWrapper>
);

export const LanguageIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
   <IconWrapper className={className}>
     <path d="M6 12h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
     <path d="M10 5h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
     <path d="M12 5v14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
     <path d="M17 12h2a3 3 0 0 1 3 3v2a2 2 0 0 1-2 2h-1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
     <path d="M5 12H3a3 3 0 0 0-3 3v2a2 2 0 0 0 2 2h1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
   </IconWrapper>
);

export const UserAvatarIcon: React.FC<{className?: string}> = ({className}) => (
    <IconWrapper className={className} viewBox="0 0 24 24">
        <path d="M14.5 8.5C14.5 9.88071 13.3807 11 12 11C10.6193 11 9.5 9.88071 9.5 8.5C9.5 7.11929 10.6193 6 12 6C13.3807 6 14.5 7.11929 14.5 8.5Z" fill="currentColor"/>
        <path d="M15.5812 16H8.50626C8.09309 16 7.87415 15.5411 8.15916 15.242C9.00598 14.3533 10.5593 13 12.1667 13C13.7899 13 15.2046 14.3801 15.947 15.2681C16.2011 15.5721 15.9774 16 15.5812 16Z" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
    </IconWrapper>
);

export const CheckIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
);

export const WarningIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
);

export const ErrorIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
);

export const InfoIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
);

export const WebSearchIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className}>
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M2 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 2C14.5013 4.46161 16 8.16334 16 12C16 15.8367 14.5013 19.5384 12 22C9.49872 19.5384 8 15.8367 8 12C8 8.16334 9.49872 4.46161 12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const ChevronRightIcon: React.FC<IconProps> = ({ className = "w-4 h-4" }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"></path></svg>
);

export const NotificationIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className}>
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const TrashIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className}>
        <path d="M3 6h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M10 11v6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M14 11v6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);

export const UserRemoveIcon: React.FC<IconProps> = ({ className = "w-5 h-5" }) => (
    <IconWrapper className={className}>
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="8.5" cy="7" r="4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <line x1="18" y1="8" x2="23" y2="13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <line x1="23" y1="8" x2="18" y2="13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);


export const CodeIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
        <polyline points="16 18 22 12 16 6"></polyline>
        <polyline points="8 6 2 12 8 18"></polyline>
    </svg>
);

export const WritingIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
        <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
    </svg>
);

export const LearningIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
        <path d="M6.5 2H20v15H6.5A2.5 2.5 0 0 1 4 14.5V4.5A2.5 2.5 0 0 1 6.5 2z"></path>
    </svg>
);

export const ProblemSolverIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
        <path d="m21.5 6.5-5 5"></path>
        <path d="m21.5 11.5-5-5"></path>
    </svg>
);

export const HomeIcon: React.FC<IconProps> = ({ className = "w-6 h-6" }) => (
    <IconWrapper className={className} viewBox="0 0 24 24">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <polyline points="9 22 9 12 15 12 15 22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </IconWrapper>
);