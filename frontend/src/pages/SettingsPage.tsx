import React, { useState } from 'react';
import { User, Theme } from '../types/types';
import Button from '../components/ui/Button';
import ProfileModal from '../components/ui/ProfileModal';
import { useToast } from '../hooks/useToast';
import { ToastType } from '../types/types';
import { 
  UserAvatarIcon, SunIcon, MoonIcon, LanguageIcon, LogoutIcon, ChevronRightIcon,
  NotificationIcon, TrashIcon, UserRemoveIcon, ThemeToggleIcon
} from '../components/icons/Icon';

interface SettingsPageProps {
  user: User | null;
  onLogout: () => void;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  onDeleteAllChats: () => void;
  onDeleteAccount: () => void;
}

const SettingsItem: React.FC<{icon: React.ReactNode, title: string, children: React.ReactNode}> = ({ icon, title, children }) => (
    <div className="flex items-center justify-between p-3 rounded-md">
        <div className="flex items-center">
            <div className="w-5 h-5 mr-4 text-light-text-secondary dark:text-dark-text-secondary">{icon}</div>
            <span className="font-medium text-light-text dark:text-dark-text">{title}</span>
        </div>
        <div>{children}</div>
    </div>
);

const SettingsPage: React.FC<SettingsPageProps> = ({ user, onLogout, theme, setTheme, onDeleteAllChats, onDeleteAccount }) => {
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const { addToast } = useToast();

  const handleThemeChange = () => {
    const newTheme = theme === Theme.LIGHT ? Theme.DARK : Theme.LIGHT;
    setTheme(newTheme);
    addToast(`Theme changed to ${newTheme}`, ToastType.INFO);
  };

  return (
    <div className="h-full bg-light-secondary dark:bg-dark-main p-4 sm:p-8 overflow-y-auto text-light-text dark:text-dark-text">
      <div className="max-w-xl mx-auto">
        <h1 className="text-4xl font-bold mb-10">Settings</h1>

        {/* Profile Section */}
        <button
            onClick={() => setIsProfileModalOpen(true)}
            className="flex items-center justify-between w-full p-4 bg-light-main dark:bg-dark-secondary rounded-lg hover:bg-light-accent dark:hover:bg-dark-accent transition-colors mb-8"
        >
            <div className="flex items-center">
              <UserAvatarIcon className="w-12 h-12 mr-4" />
              <div>
                <p className="font-semibold text-lg text-left text-light-text dark:text-dark-text">{user?.username}</p>
                <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">View Profile</p>
              </div>
            </div>
            <ChevronRightIcon className="w-5 h-5 text-light-text-secondary dark:text-dark-text-secondary" />
        </button>

        {/* General Settings */}
        <h2 className="px-2 pt-1 pb-2 text-md font-semibold text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">General</h2>
        <div className="bg-light-main dark:bg-dark-secondary rounded-lg p-1 space-y-0.5 mb-8">
            <SettingsItem icon={<ThemeToggleIcon theme={theme}/>} title="Theme">
                 <div onClick={handleThemeChange} className={`relative flex items-center w-[52px] h-7 rounded-full cursor-pointer p-1 transition-colors ${theme === Theme.LIGHT ? 'bg-light-accent' : 'bg-accent-light-blue'}`}>
                    <div className="absolute w-5 h-5 bg-white dark:bg-gray-400 rounded-full shadow-md transform transition-transform duration-300 ease-in-out" style={{ transform: theme === Theme.LIGHT ? 'translateX(0)' : 'translateX(24px)'}}></div>
                </div>
            </SettingsItem>
            <SettingsItem icon={<NotificationIcon/>} title="Notifications">
                <label htmlFor="notification-toggle" className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" id="notification-toggle" className="sr-only peer" checked={notificationsEnabled} onChange={() => setNotificationsEnabled(!notificationsEnabled)} />
                  <div className="w-11 h-6 bg-light-accent dark:bg-dark-accent rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-accent-light-blue"></div>
                </label>
            </SettingsItem>
        </div>

        {/* Danger Zone */}
        <h2 className="px-2 pt-1 pb-2 text-md font-semibold text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Account settings</h2>
        <div className="bg-light-main dark:bg-dark-secondary rounded-lg p-1 space-y-0.5">
            <SettingsItem icon={<TrashIcon/>} title="Clear History">
                <Button variant="danger" size="sm" onClick={onDeleteAllChats}>Delete all chats</Button>
            </SettingsItem>
            <SettingsItem icon={<UserRemoveIcon/>} title="Delete Account">
                <Button variant="danger" size="sm" onClick={onDeleteAccount}>Delete account</Button>
            </SettingsItem>
        </div>

      </div>
      <ProfileModal isOpen={isProfileModalOpen} onClose={() => setIsProfileModalOpen(false)} user={user} />
    </div>
  );
};

export default SettingsPage;