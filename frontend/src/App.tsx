import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';
import HomePage from './pages/HomePage';
import UserOnboarding from './components/ui/UserOnboarding';
import { ToastProvider } from './hooks/useToast';
import { Theme, User, OnboardingStep } from './types/types';
import * as api from './services/api';

// Website components
import Header from './components/website/Layout/Header';
import Footer from './components/website/Layout/Footer';
import WebsiteHome from './pages/website/WebsiteHome';
import WebsiteAbout from './pages/website/WebsiteAbout';
import WebsiteFeeds from './pages/website/WebsiteFeeds';
import WebsiteCalculator from './pages/website/WebsiteCalculator';
import ProtectedRoute from './components/website/ProtectedRoute';

enum AppMode {
  WEBSITE,
  CHATBOT,
}

enum Page {
  LOGIN,
  SIGNUP,
  HOME,
}

const onboardingSteps: OnboardingStep[] = [
    {
        selector: '#new-chat-button',
        title: 'Start a New Conversation',
        description: 'Click here to start a fresh chat anytime. Your conversations are automatically saved in the list below.',
        position: 'right',
    },
    {
        selector: '#chat-history-list',
        title: 'Manage Your Chats',
        description: 'Your recent chats appear here. Hover over any chat to reveal options for renaming or deleting it.',
        position: 'bottom-left-corner',
    },
    {
        selector: '#sidebar-footer',
        title: 'Your Account & Settings',
        description: 'Access your profile, switch between light and dark modes, or open the main settings panel from here.',
        position: 'top',
    },
    {
        selector: '#web-search-toggle',
        title: 'Enable Web Search',
        description: 'Toggle this on to allow the AI to access up-to-date information from the web for more relevant answers.',
        position: 'top',
    },
    {
        selector: '#language-toggle',
        title: 'Select Language',
        description: 'Choose your preferred language for the conversation before sending your first message.',
        position: 'top',
    }
];

// Main App Component with Router
const App: React.FC = () => {
  return (
    <ToastProvider>
      <Router>
        <AppContent />
      </Router>
    </ToastProvider>
  );
};

// App Content Component (inside Router context)
const AppContent: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState<Page>(Page.LOGIN);
  const [theme, setTheme] = useState<Theme>(Theme.LIGHT);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [appMode, setAppMode] = useState<AppMode>(AppMode.WEBSITE);
  const location = useLocation();

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove(theme === Theme.DARK ? 'light' : 'dark');
    root.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Determine app mode based on route
  useEffect(() => {
    if (location.pathname.startsWith('/chatbot')) {
      setAppMode(AppMode.CHATBOT);
    } else {
      setAppMode(AppMode.WEBSITE);
    }
  }, [location.pathname]);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    }
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    if (!savedTheme && mediaQuery.matches) {
        setTheme(Theme.DARK);
    }
    
    // Check for existing authentication
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // Validate token and get user info
          const user = await api.getCurrentUser();
          if (user) {
            setCurrentUser(user);
            if (appMode === AppMode.CHATBOT) {
              setCurrentPage(Page.HOME);
            }
          }
        } catch (error) {
          localStorage.removeItem('token');
        }
      }
    };
    
    checkAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appMode]);

  const handleLoginSuccess = (user: User) => {
    setCurrentUser(user);
    const isNewUser = localStorage.getItem(`onboarded_${user.id}`) !== 'true';
    if(isNewUser) {
      setShowOnboarding(true);
      localStorage.setItem(`onboarded_${user.id}`, 'true');
    }
    setCurrentPage(Page.HOME);
  };
  
  const handleSignUpSuccess = (user: User) => {
    // After sign up, redirect to login
    setCurrentPage(Page.LOGIN);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setCurrentPage(Page.LOGIN);
  };

  const renderChatbotMode = () => {
    switch (currentPage) {
      case Page.LOGIN:
        return <LoginPage onLoginSuccess={handleLoginSuccess} onSwitchToSignUp={() => setCurrentPage(Page.SIGNUP)} />;
      case Page.SIGNUP:
        return <SignUpPage onSignUpSuccess={handleSignUpSuccess} onSwitchToLogin={() => setCurrentPage(Page.LOGIN)} />;
      case Page.HOME:
        if (currentUser) {
          return (
            <>
              <HomePage user={currentUser} onLogout={handleLogout} theme={theme} setTheme={setTheme} />
              {showOnboarding && <UserOnboarding isOpen={showOnboarding} onClose={() => setShowOnboarding(false)} steps={onboardingSteps} />}
            </>
          );
        }
        // Fallback to login if no user
        setCurrentPage(Page.LOGIN);
        return null;
      default:
        return <LoginPage onLoginSuccess={handleLoginSuccess} onSwitchToSignUp={() => setCurrentPage(Page.SIGNUP)} />;
    }
  };

  // Render based on app mode
  if (appMode === AppMode.CHATBOT) {
    return renderChatbotMode();
  }

  // Website mode with React Router
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-all duration-500 flex flex-col">
      <Header 
        currentUser={currentUser}
        theme={theme}
        setTheme={setTheme}
        onLogin={() => window.location.href = '/login'}
        onLogout={handleLogout}
      />
      
      <main className="flex-1">
        <Routes>
          {/* Website Routes */}
          <Route path="/" element={<WebsiteHome />} />
          <Route path="/about" element={<WebsiteAbout />} />
          <Route path="/feeds" element={<WebsiteFeeds />} />
          <Route path="/post/:id" element={<div>Post Detail - Coming Soon</div>} />
          
          {/* Protected Website Routes */}
          <Route path="/calculator" element={
            <ProtectedRoute user={currentUser}>
              <WebsiteCalculator />
            </ProtectedRoute>
          } />
          
          {/* Authentication Routes */}
          <Route path="/login" element={
            <LoginPage 
              onLoginSuccess={handleLoginSuccess} 
              onSwitchToSignUp={() => window.location.href = '/signup'} 
            />
          } />
          <Route path="/signup" element={
            <SignUpPage 
              onSignUpSuccess={handleSignUpSuccess} 
              onSwitchToLogin={() => window.location.href = '/login'} 
            />
          } />
          
          {/* Chatbot Redirect */}
          <Route path="/chatbot" element={
            <ProtectedRoute user={currentUser}>
              <HomePage user={currentUser!} onLogout={handleLogout} theme={theme} setTheme={setTheme} />
            </ProtectedRoute>
          } />
          
          {/* Admin Routes */}
          <Route path="/admin/*" element={
            <ProtectedRoute user={currentUser} requireAdmin>
              <div>Admin Panel - Coming Soon</div>
            </ProtectedRoute>
          } />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      
      <Footer />
      
      {/* Onboarding for chatbot mode */}
      {showOnboarding && (
        <UserOnboarding 
          isOpen={showOnboarding} 
          onClose={() => setShowOnboarding(false)} 
          steps={onboardingSteps} 
        />
      )}
    </div>
  );
};

export default App;
export { AppMode };